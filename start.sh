#!/bin/bash

# Startup script for Energy Monitoring System

echo "Starting Energy Monitoring System..."

# Set environment variables
export FLASK_ENV=production
export PORT=5000

# Initialize database if it doesn't exist
if [ ! -f "energy_monitor.db" ]; then
    echo "Initializing database..."
    python3 -c "import database as db; db.init_database()"
fi

# Start the application
echo "Starting application on port $PORT..."
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app_advanced:app
