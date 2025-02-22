#!/bin/sh
# Start Ollama in the background
ollama serve &

# Wait a bit to ensure Ollama is running
sleep 2

# pull the model
ollama run deepseek-r1:1.5b

# Start Flask app
exec flask run --host=0.0.0.0