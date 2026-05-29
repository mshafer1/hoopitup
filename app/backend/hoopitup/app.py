"""
Hoop It Up Backend - Flask with SocketIO
"""
import datetime
import enum

import apscheduler.schedulers.background

# from flask import Flask, jsonify, request
import flask
import flask_cors
import flask_socketio

from hoopitup import config

app = flask.Flask(__name__, static_folder=None)
app.config["SECRET_KEY"] = config.config.SECRET_KEY
flask_cors.CORS(app)
socketio = flask_socketio.SocketIO(app, cors_allowed_origins="*")

# Initialize background scheduler for cron jobs
scheduler = apscheduler.schedulers.background.BackgroundScheduler(timezone=config.SCHEDULE_TIMEZONE)
scheduler.start()


class VoteValues(enum.StrEnum):
    YES = "yes"
    YES_IF_3 = "yes_if_3"
    YES_IF_5 = "yes_if_5"
    NO = "no"
    MAYBE = "maybe"


_VALID_VOTE_CHOICES = {vote.value for vote in VoteValues}

# In-memory storage for voting data
# In production, use a database
votes = {}
vote_counts = {vote.value: 0 for vote in VoteValues}
participants = {}


def send_scheduled_message():
    """
    Send scheduled message to all connected clients.
    This function is called by the scheduler based on the cron expression.
    """
    message = config.SCHEDULE_MESSAGE
    timestamp = datetime.datetime.now().isoformat()

    socketio.emit("scheduled_message", {"message": message, "timestamp": timestamp}, broadcast=True)

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
    flask_socketio.emit("votes_update", vote_counts, broadcast=True)


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return flask.jsonify({"status": "healthy"})


@app.route("/api/votes", methods=["GET"])
def get_votes():
    """Get current vote counts"""
    return flask.jsonify(vote_counts)


@socketio.on("connect")
def handle_connect(data=None):
    """Handle client connection"""
    print(f"Client connected: {flask.request.sid if hasattr(flask.request, 'sid') else 'unknown'}")
    flask_socketio.emit("connection_response", {"message": "Connected to server"})
    # Send current votes to new client
    send_current_votes()


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection"""
    return  # disconnected does not trigger a vote change, so we can skip updating votes on disconnect


@socketio.on("vote")
def handle_vote(data):
    """Handle vote submission"""
    from flask_socketio import request

    vote_choice = data.get("vote")  # 'yes', 'no', 'maybe', 'yes_if_3', 'yes_if_5'

    if vote_choice not in _VALID_VOTE_CHOICES:
        flask_socketio.emit("error", {"message": "Invalid vote choice"})
        return

    sid = request.sid
    if sid not in votes:
        votes[sid] = vote_choice
        vote_counts[vote_choice] += 1
    else:
        # Update existing vote
        old_vote = votes[sid]
        if old_vote != vote_choice:
            vote_counts[old_vote] -= 1
            if vote_counts[old_vote] < 0:
                vote_counts[old_vote] = 0  # Ensure count doesn't go negative
            votes[sid] = vote_choice
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
        minutes=5,
        id="periodic_vote_update",
        name="Periodic update of current votes to clients",
        replace_existing=True,
    )
    print(f"Scheduled message job configured: {config.SCHEDULE_CRON} - '{config.SCHEDULE_MESSAGE}'")
except Exception as e:
    print(f"Error scheduling message job: {e}")


@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    """Shutdown the scheduler when the app closes"""
    if scheduler.running:
        scheduler.shutdown()


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
