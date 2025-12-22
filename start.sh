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

# Start the backend in the background on internal port 8001
cd /app/backend && uvicorn main:app --host 127.0.0.1 --port 8001 &

# Start the arq worker in the background
cd /app/backend && arq tasks.WorkerSettings &

# Start the frontend in the foreground binding to the Render port
cd /app/frontend && npm start -- -p $PORT -H 0.0.0.0
