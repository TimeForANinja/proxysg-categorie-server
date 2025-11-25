# Stage 1: Build the React frontend
FROM node:20 AS frontend-builder

# Set working directory
WORKDIR /frontend

# Copy frontend code
COPY ./frontend/ ./

RUN npm install
RUN npm run build

# Stage 2: Prepare the Flask backend
FROM python:3.11 AS backend

MAINTAINER Tobias Kutscha

# Set working directory
WORKDIR /backend

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# make dir for persistent content
RUN mkdir -p /backend/data

# copy only the requirements.txt (improves layer caching)
COPY ./backend/requirements.txt ./

# install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy all other backend code
COPY ./backend/ ./

# Copy built React code from the previous stage
COPY --from=frontend-builder /frontend/build ./dist

# create start-script to start the server with Gunicorn
RUN echo '#!/bin/sh' > /backend/start.sh && \
    echo 'set -e' >> /backend/start.sh && \
    echo 'exec gunicorn -c gunicorn_config.py -w 4 -b 0.0.0.0:8080 app:app' >> /backend/start.sh
RUN chmod +x /backend/start.sh

# Expose the port for Flask (optional, adjust as necessary)
EXPOSE 8080

CMD ["/backend/start.sh"]
