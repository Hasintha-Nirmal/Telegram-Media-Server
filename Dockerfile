FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p /data/session /data/downloads /data/database

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "main.py"]
