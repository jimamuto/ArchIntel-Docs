# Multi-stage build for a single-service monorepo
# Stage 1: Build the Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
ENV NEXT_PUBLIC_API_BASE_URL=/api
RUN npm run build

# Stage 2: Final Image
FROM python:3.11-slim
WORKDIR /app

# Install Node.js, Git, and Redis in the final image
RUN apt-get update && apt-get install -y nodejs npm git redis-server && rm -rf /var/lib/apt/lists/*

# Copy backend and install dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy frontend build and source
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/package*.json ./frontend/
COPY --from=frontend-builder /app/frontend/node_modules ./frontend/node_modules

# Copy backend source
COPY backend/ ./backend/

# Copy a startup script
COPY start.sh .
RUN chmod +x start.sh

# Expose the port Render expects
EXPOSE 8080

# Environment variables
ENV PORT=8080

CMD ["./start.sh"]
