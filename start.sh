#!/bin/bash

# Start the backend in the background
cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start the frontend in the foreground
cd /app/frontend && npm start -- -p 8080
