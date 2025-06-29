FROM python:3.11-slim

# Creating Working Directory inside docker container 
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/

# Install all the requirements with proper cleanup
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app

# Add healthcheck to ensure container is running properly
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8000/ || exit 1

# Use non-root user for security
USER 1000

# Command to run the application
CMD ["sh","-c","python manage.py runserver 0.0.0.0:8000"]

