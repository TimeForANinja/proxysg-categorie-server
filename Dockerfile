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

# Set working directory
WORKDIR /backend

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# make dir for persistent content
RUN mkdir -p /backend/data

# Copy the backend code
COPY ./backend/ ./

# install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy built React code from the previous stage
COPY --from=frontend-builder /frontend/build ./dist

# Expose the port for Flask (optional, adjust as necessary)
EXPOSE 8080

# Start the server with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
