#!/bin/bash
set -e

echo "Starting Hoop It Up application..."

# Start uwsgi for Flask backend
echo "Starting Flask backend with uwsgi..."
cd /app/backend
python3 -m hoopitup.app &
hoopitup_PID=$!

# Function to handle signals
handle_signal() {
    echo "Shutting down gracefully..."
    kill $hoopitup_PID 2>/dev/null || true
    wait $hoopitup_PID 2>/dev/null || true
    exit 0
}

# Trap signals
trap handle_signal SIGTERM SIGINT

# Wait for all processes
wait
