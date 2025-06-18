# Alpha - Honeypot Threat Intelligence Solution
# Multi-stage Docker build for production deployment

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r honeypot && useradd -r -g honeypot honeypot

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/honeypot/.local

# Copy application code
COPY --chown=honeypot:honeypot . .

# Make sure scripts are executable
RUN chmod +x setup.py

# Set environment variables
ENV PATH=/home/honeypot/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Switch to non-root user
USER honeypot

# Create necessary directories and initialize files
RUN mkdir -p /app && \
    touch logs.csv && \
    echo "0" > log_count.txt && \
    echo "[]" > ip_cache.json

# Try to run setup script, but don't fail the build if it has issues
RUN python -c "
import os, csv, json
# Create .env if not exists
if not os.path.exists('.env'):
    with open('.env', 'w') as f:
        f.write('SECRET_KEY=docker-honeypot-secret-key\\n')
        f.write('HOST=0.0.0.0\\n')
        f.write('PORT=5000\\n')
        f.write('DEBUG=False\\n')
        f.write('RETRAIN_THRESHOLD=10\\n')

# Create initial logs.csv with headers
if not os.path.exists('logs.csv') or os.path.getsize('logs.csv') == 0:
    with open('logs.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'ip', 'username', 'password', 'classification'])
        # Add some sample data for ML model
        writer.writerow(['2025-06-15 10:00:00', '192.168.1.100', 'admin', 'password123', 'normal_user'])
        writer.writerow(['2025-06-15 10:15:00', '203.0.113.45', 'admin', 'admin', 'attacker'])

print('Docker initialization completed!')
" || echo "Setup completed with basic initialization"

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Start command
CMD ["python", "app.py"]
