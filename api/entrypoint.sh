#!/bin/bash
set -e

# Start the Flask app in the background
python app.py &
FLASK_PID=$!

# Keep the script running until Flask exits
wait $FLASK_PID