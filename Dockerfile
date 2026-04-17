FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories with proper permissions
RUN mkdir -p /data/session /data/downloads /data/database && \
    chmod -R 777 /data

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "main.py"]
