#!/bin/bash

echo "Starting Automated Web Scraper Services..."
echo

# Function to start service in background
start_service() {
    local name=$1
    local command=$2
    echo "Starting $name..."
    nohup $command > "${name}.log" 2>&1 &
    echo "$name started with PID: $!"
    echo
}

# Start Celery Worker
start_service "Celery Worker" "python3 celery_worker.py"

# Start Celery Beat Scheduler
start_service "Celery Beat" "python3 celery_beat.py"

echo "All services started!"
echo
echo "To use the scraper, run:"
echo "  python3 main.py --help"
echo
echo "To stop all services, run:"
echo "  pkill -f 'celery_worker.py'"
echo "  pkill -f 'celery_beat.py'"
echo
echo "Service logs are saved to:"
echo "  Celery Worker: Celery Worker.log"
echo "  Celery Beat: Celery Beat.log"
echo
echo "Press Ctrl+C to exit this script (services will continue running)"
echo

# Wait for user input
read -p "Press Enter to exit..."
