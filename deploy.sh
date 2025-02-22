#!/bin/bash

# Build the Docker image
echo "Building Docker image..."
docker build -t flask-app .

# Check if the container is already running, and stop it if it is
if [ "$(docker ps -q -f name=flask-app)" ]; then
    echo "Stopping existing container..."
    docker stop flask-app
    docker rm flask-app
fi

# Run the Docker container
echo "Running Docker container..."
docker run -d -p 3000:5000 --name flask-app -v "$(pwd)":/app flask-app

# Final message with URL
echo "Deployment complete. Flask app is running at http://localhost:3000"