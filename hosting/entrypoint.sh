#!/bin/bash
set -e

echo "Starting Hoop It Up application..."

# Start nginx in background
echo "Starting nginx..."
nginx -c /etc/nginx/nginx.conf &
NGINX_PID=$!

# Start uwsgi for Flask backend
echo "Starting Flask backend with uwsgi..."
cd /app
uwsgi --ini uwsgi.ini --plugin python3 &
UWSGI_PID=$!

# Function to handle signals
handle_signal() {
    echo "Shutting down gracefully..."
    kill $UWSGI_PID 2>/dev/null || true
    kill $NGINX_PID 2>/dev/null || true
    wait $UWSGI_PID 2>/dev/null || true
    wait $NGINX_PID 2>/dev/null || true
    exit 0
}

# Trap signals
trap handle_signal SIGTERM SIGINT

# Wait for all processes
wait
