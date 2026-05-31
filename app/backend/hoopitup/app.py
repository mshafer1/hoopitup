"""
Hoop It Up Backend - Flask with SocketIO
"""

import atexit
import datetime
import enum
import logging
import pathlib
import urllib.parse
import uuid

import apscheduler.schedulers.background
import flask
import flask_cors
import flask_socketio
from flask_wtf import CSRFProtect

from hoopitup import config

app = flask.Flask(__name__, static_folder=None)
app.config["SECRET_KEY"] = config.SECRET_KEY
# Initialize CSRF protection (Flask-WTF)
csrf = CSRFProtect()
csrf.init_app(app)

MODULE_LOGGER = logging.getLogger(__name__)
MODULE_LOGGER.info("CSRF protection enabled")
MODULE_DIR = pathlib.Path(__file__).parent
FRONTEND_PATH = MODULE_DIR / ".." / ".." / "frontend"
DIST_PATH = (FRONTEND_PATH / "dist").resolve()

_SECONDS_IN_A_YEAR = 60 * 60 * 24 * 365

logging.warning("Dist path is: %s", DIST_PATH)

extra_socket_args = {}
if config.DEBUG:
    logging.basicConfig(level=logging.DEBUG)
    MODULE_LOGGER.setLevel(logging.DEBUG)
    logging.warning("enabling cross-origin-resource-loading")
    cors = flask_cors.CORS(app)
    extra_socket_args = {
        "cors_allowed_origins": "*",
        "logger": True,
        "enginio_logger": True,
    }

socketio = flask_socketio.SocketIO(app, **extra_socket_args)


# Initialize background scheduler for cron jobs
scheduler = apscheduler.schedulers.background.BackgroundScheduler(timezone=config.SCHEDULE_TIMEZONE)


class VoteValues(enum.StrEnum):
    YES = "yes"
    YES_IF_3 = "yes_if_3"
    YES_IF_5 = "yes_if_5"
    NO = "no"
    MAYBE = "maybe"


_VALID_VOTE_CHOICES = {vote.value for vote in VoteValues}

# In-memory storage for voting data
# In production, use a database
votes = {}  # session_id -> vote
vote_counts = {vote.value: 0 for vote in VoteValues}
sid_to_session = {}  # sid -> session_id
participants = {}


def send_scheduled_message():
    """
    Send scheduled message to all connected clients.
    This function is called by the scheduler based on the cron expression.
    """
    message = config.SCHEDULE_MESSAGE
    timestamp = datetime.datetime.now().isoformat()

    socketio.emit("scheduled_message", {"message": message, "timestamp": timestamp})

    print(f"[{timestamp}] Scheduled message sent: {message}")


def reset_votes():
    """Reset all votes and notify clients"""
    votes.clear()
    vote_counts.clear()
    vote_counts.update({vote.value: 0 for vote in VoteValues})
    send_current_votes()


def parse_cron_expression(cron_str):
    """
    Parse a cron expression string into APScheduler cron kwargs.
    Expected format: 'minute hour day month day_of_week' e.g., '0 7 * * 2,4'
    """
    parts = cron_str.split()
    if len(parts) != 5:
        raise ValueError(
            f"Invalid cron expression: {cron_str}. Expected 5 parts (minute hour day month day_of_week)"
        )

    minute, hour, day, month, day_of_week = parts

    return {
        "minute": minute,
        "hour": hour,
        "day": day if day != "*" else None,
        "month": month if month != "*" else None,
        "day_of_week": day_of_week if day_of_week != "*" else None,
    }


def send_current_votes():
    """Send current vote counts to a specific client"""
    MODULE_LOGGER.debug(f"Sending current votes to clients: {vote_counts}")
    socketio.emit("votes_update", vote_counts)


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return flask.jsonify({"status": "healthy"})


@socketio.on("connect")
def handle_connect(data=None):
    """Handle client connection"""
    sid = flask.request.sid
    session_id = flask.request.cookies.get("session_id")
    if not session_id:
        # Should not happen if HTTP route sets cookie, but fallback
        session_id = str(uuid.uuid4())
    sid_to_session[sid] = session_id
    print(f"Client connected: sid={sid}, session_id={session_id}")
    socketio.emit(
        "connection_response",
        {"message": "Connected to server", "session_id": session_id},
        room=sid,
    )
    # Send current votes to new client
    send_current_votes()


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection"""
    return  # disconnected does not trigger a vote change, so we can skip updating votes on disconnect


@socketio.on("vote")
def handle_vote(data):
    """Handle vote submission"""
    vote_choice = data.get("vote")  # 'yes', 'no', 'maybe', 'yes_if_3', 'yes_if_5'

    if vote_choice not in _VALID_VOTE_CHOICES:
        socketio.emit("error", {"message": "Invalid vote choice"}, room=flask.request.sid)
        return

    sid = flask.request.sid
    session_id = sid_to_session.get(sid)
    if not session_id:
        # Fallback: try to get from cookie
        session_id = flask.request.cookies.get("session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
        sid_to_session[sid] = session_id

    if session_id not in votes:
        votes[session_id] = vote_choice
        vote_counts[vote_choice] += 1
    else:
        # Update existing vote
        old_vote = votes[session_id]
        if old_vote != vote_choice:
            vote_counts[old_vote] -= 1
            if vote_counts[old_vote] < 0:
                vote_counts[old_vote] = 0  # Ensure count doesn't go negative
            votes[session_id] = vote_choice
            vote_counts[vote_choice] += 1
    # Broadcast updated vote counts to all clients
    send_current_votes()


# Schedule the message sending job
try:
    scheduler.add_job(
        send_scheduled_message,
        "cron",
        **parse_cron_expression(config.SCHEDULE_CRON),
        id="scheduled_message",
        name="Send scheduled game message",
        replace_existing=True,
    )
    print(f"Scheduled message job configured: {config.SCHEDULE_CRON} - '{config.SCHEDULE_MESSAGE}'")
    scheduler.add_job(
        reset_votes,
        "cron",
        hour=0,
        minute=0,
        id="daily_reset",
        name="Daily reset of votes",
        replace_existing=True,
    )
    scheduler.add_job(
        send_current_votes,
        "interval",
        minutes=10,
        id="periodic_vote_update",
        name="Periodic update of current votes to clients",
        replace_existing=True,
    )
except Exception as e:
    MODULE_LOGGER.error("Error scheduling message job: %s", e)


@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    """Shutdown the scheduler when the app closes"""
    # Previously this shut down the scheduler on every request teardown,
    # which caused scheduled jobs to stop running. Scheduler shutdown
    # should happen on process exit, not after each request.
    return


# Ensure the scheduler is started in the worker process (not before forking)
def start_scheduler():
    """Start the scheduler when the first request is handled by this process."""
    MODULE_LOGGER.info("Checking if scheduler is running...")
    if not scheduler.running:
        try:
            MODULE_LOGGER.info("Starting scheduler in process")
            scheduler.start()
        except Exception as e:
            MODULE_LOGGER.error(f"Error starting scheduler (continuing): {e}")
            # If already started concurrently, ignore
            pass


with app.app_context():
    start_scheduler()

    # Register a clean shutdown for the scheduler on process exit
    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)


# region: web-server


@app.route("/", defaults={"path": "index.html"}, methods=["GET"])
def get_index(path):
    print("Handling root path")
    resp = _handle_path("index.html")
    return resp


@app.route("/api/current-vote", methods=["GET"])
def get_current_vote():
    session_id = flask.request.cookies.get("session_id")
    if not session_id:
        return flask.jsonify({"error": "Session ID not found"}), 400

    vote = votes.get(session_id)
    if not vote:
        return flask.jsonify({"error": "No vote found for this session"}), 404

    return flask.jsonify({"vote": vote})


@app.route("/<path:path>", methods=["GET"])
def get_dir(path):
    parsed = urllib.parse.urlparse(path).path
    print("Requested path is", path, "parsed to", parsed)
    resp = _handle_path(parsed)
    return resp


def _handle_path(parsed):
    session_id = flask.request.cookies.get("session_id")
    MODULE_LOGGER.debug(f"Handling parsed: {parsed}, session_id: {session_id}")
    resource_path = "/" + (parsed if "." in parsed else "index.html")
    MODULE_LOGGER.debug(f"Resource path resolved to: {resource_path}")
    resp = flask.make_response(flask.send_from_directory(DIST_PATH, resource_path.lstrip("/")))
    if not session_id:
        session_id = str(uuid.uuid4())
    # set or renew cookie on each visit to keep active users from losing their session_id
    resp.set_cookie(
        "session_id",
        session_id,
        max_age=_SECONDS_IN_A_YEAR,
        httponly=True,
        samesite="Strict",
        secure=not config.DEBUG,
    )
    return resp


# endregion

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
