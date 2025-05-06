# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Agent4ALL with the 'call' extra and ensure it's the latest version
RUN pip install --no-cache-dir --upgrade "agent4all[call]"

# Expose the port the app runs on
EXPOSE 8090

# Run the application
CMD ["agent4all", "call"]
