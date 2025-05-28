#!/bin/bash
set -e

# Start the Flask app in the background
python app.py &
FLASK_PID=$!

# Configure and start ngrok if auth token is provided
if [ -n "$NGROK_AUTH_TOKEN" ]; then
    echo "Configuring ngrok with provided auth token..."
    ngrok config add-authtoken "$NGROK_AUTH_TOKEN"
    
    echo "Starting ngrok tunnel to expose port 5000..."
    ngrok http 5000 &
    NGROK_PID=$!
    
    # Wait for ngrok to be ready
    sleep 3
    
    # Try to get and display public URL through ngrok API
    echo "Checking ngrok tunnel URL..."
    curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | sed 's/"public_url":"/Ngrok public URL: /'
else
    echo "NGROK_AUTH_TOKEN not provided. API will only be available locally."
fi

# Keep the script running until Flask exits
wait $FLASK_PID