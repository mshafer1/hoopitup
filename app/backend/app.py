"""
Hoop It Up Backend - Flask with SocketIO
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import json
from datetime import datetime
from config import Config

app = Flask(__name__, static_folder=None)
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize background scheduler for cron jobs
scheduler = BackgroundScheduler(timezone=Config.SCHEDULE_TIMEZONE)
scheduler.start()

# In-memory storage for voting data
# In production, use a database
votes = {}
participants = {}


def send_scheduled_message():
    """
    Send scheduled message to all connected clients.
    This function is called by the scheduler based on the cron expression.
    """
    message = Config.SCHEDULE_MESSAGE
    timestamp = datetime.now().isoformat()
    
    socketio.emit('scheduled_message', {
        'message': message,
        'timestamp': timestamp
    }, broadcast=True)
    
    print(f"[{timestamp}] Scheduled message sent: {message}")


def parse_cron_expression(cron_str):
    """
    Parse a cron expression string into APScheduler cron kwargs.
    Expected format: 'minute hour day month day_of_week' e.g., '0 7 * * 2,4'
    """
    parts = cron_str.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {cron_str}. Expected 5 parts (minute hour day month day_of_week)")
    
    minute, hour, day, month, day_of_week = parts
    
    return {
        'minute': minute,
        'hour': hour,
        'day': day if day != '*' else None,
        'month': month if month != '*' else None,
        'day_of_week': day_of_week if day_of_week != '*' else None
    }


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


@app.route('/api/votes', methods=['GET'])
def get_votes():
    """Get current vote counts"""
    yes = len([v for v in votes.values() if v == 'yes'])
    yes_if_3 = len([v for v in votes.values() if v == 'yes_if_3'])
    yes_if_5 = len([v for v in votes.values() if v == 'yes_if_5'])
    no = len([v for v in votes.values() if v == 'no'])
    maybe = len([v for v in votes.values() if v == 'maybe'])

    vote_counts = {
        'yes': yes,
        'yes_if_3': yes_if_3,
        'yes_if_5': yes_if_5,
        'no': no,
        'maybe': maybe,
        'total': len(votes),
        'enough_for_3': (yes + yes_if_3) >= 6,
        'enough_for_5': (yes + yes_if_5) >= 10
    }
    return jsonify(vote_counts)


@socketio.on('connect')
def handle_connect(data=None):
    """Handle client connection"""
    print(f"Client connected: {request.sid if hasattr(request, 'sid') else 'unknown'}")
    emit('connection_response', {'message': 'Connected to server'})
    # Send current votes to new client
    vote_counts = {
        'yes': len([v for v in votes.values() if v == 'yes']),
        'yes_if_3': len([v for v in votes.values() if v == 'yes_if_3']),
        'yes_if_5': len([v for v in votes.values() if v == 'yes_if_5']),
        'no': len([v for v in votes.values() if v == 'no']),
        'maybe': len([v for v in votes.values() if v == 'maybe']),
        'total': len(votes),
        'enough_for_3': (len([v for v in votes.values() if v == 'yes']) + len([v for v in votes.values() if v == 'yes_if_3'])) >= 6,
        'enough_for_5': (len([v for v in votes.values() if v == 'yes']) + len([v for v in votes.values() if v == 'yes_if_5'])) >= 10
    }
    emit('votes_update', vote_counts)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    from flask_socketio import request
    sid = request.sid
    if sid in votes:
        del votes[sid]
    if sid in participants:
        del participants[sid]
    # Notify all clients of the update
    vote_counts = {
        'yes': len([v for v in votes.values() if v == 'yes']),
        'yes_if_3': len([v for v in votes.values() if v == 'yes_if_3']),
        'yes_if_5': len([v for v in votes.values() if v == 'yes_if_5']),
        'no': len([v for v in votes.values() if v == 'no']),
        'maybe': len([v for v in votes.values() if v == 'maybe']),
        'total': len(votes),
        'enough_for_3': (len([v for v in votes.values() if v == 'yes']) + len([v for v in votes.values() if v == 'yes_if_3'])) >= 6,
        'enough_for_5': (len([v for v in votes.values() if v == 'yes']) + len([v for v in votes.values() if v == 'yes_if_5'])) >= 10
    }
    emit('votes_update', vote_counts, broadcast=True)


@socketio.on('vote')
def handle_vote(data):
    """Handle vote submission"""
    from flask_socketio import request
    vote_choice = data.get('vote')  # 'yes', 'no', 'maybe', 'yes_if_3', 'yes_if_5'

    valid_choices = ['yes', 'no', 'maybe', 'yes_if_3', 'yes_if_5']
    if vote_choice not in valid_choices:
        emit('error', {'message': 'Invalid vote choice'})
        return
    
    sid = request.sid
    votes[sid] = vote_choice
    
    # Broadcast updated vote counts to all clients
    vote_counts = {
        'yes': len([v for v in votes.values() if v == 'yes']),
        'yes_if_3': len([v for v in votes.values() if v == 'yes_if_3']),
        'yes_if_5': len([v for v in votes.values() if v == 'yes_if_5']),
        'no': len([v for v in votes.values() if v == 'no']),
        'maybe': len([v for v in votes.values() if v == 'maybe']),
        'total': len(votes),
        'enough_for_3': (len([v for v in votes.values() if v == 'yes']) + len([v for v in votes.values() if v == 'yes_if_3'])) >= 6,
        'enough_for_5': (len([v for v in votes.values() if v == 'yes']) + len([v for v in votes.values() if v == 'yes_if_5'])) >= 10
    }
    emit('votes_update', vote_counts, broadcast=True)


@socketio.on('reset_votes')
def handle_reset():
    """Reset all votes"""
    votes.clear()
    emit('votes_update', {
        'yes': 0,
        'yes_if_3': 0,
        'yes_if_5': 0,
        'no': 0,
        'maybe': 0,
        'total': 0,
        'enough_for_3': False,
        'enough_for_5': False
    }, broadcast=True)


# Schedule the message sending job
try:
    scheduler.add_job(
        send_scheduled_message,
        'cron',
        **parse_cron_expression(Config.SCHEDULE_CRON),
        id='scheduled_message',
        name='Send scheduled game message',
        replace_existing=True
    )
    print(f"Scheduled message job configured: {Config.SCHEDULE_CRON} - '{Config.SCHEDULE_MESSAGE}'")
except Exception as e:
    print(f"Error scheduling message job: {e}")


@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    """Shutdown the scheduler when the app closes"""
    if scheduler.running:
        scheduler.shutdown()


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
