#!/bin/bash

# Start Redis server
echo "Starting Redis server..."
redis-server --daemonize yes

# Wait for Redis to be ready
until redis-cli ping | grep -q PONG; do
  echo "Waiting for Redis..."
  sleep 1
done
echo "Redis is ready!"

# Start the backend in the background
cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start the arq worker in the background
cd /app/backend && arq tasks.WorkerSettings &

# Start the frontend in the foreground
cd /app/frontend && npm start -- -p 8080
