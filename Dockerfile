FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary files without running setup.py
RUN python -c "
import os, csv, json

# Create .env file
if not os.path.exists('.env'):
    with open('.env', 'w') as f:
        f.write('SECRET_KEY=docker-honeypot-secret\\n')
        f.write('HOST=0.0.0.0\\n')
        f.write('PORT=5000\\n')
        f.write('DEBUG=False\\n')
        f.write('RETRAIN_THRESHOLD=10\\n')

# Create logs.csv with headers and sample data
with open('logs.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'ip', 'username', 'password', 'classification'])
    writer.writerow(['2025-06-15 10:00:00', '192.168.1.100', 'admin', 'password123', 'normal_user'])
    writer.writerow(['2025-06-15 10:05:00', '10.0.0.50', 'user', 'mypassword', 'normal_user'])
    writer.writerow(['2025-06-15 10:10:00', '172.16.0.25', 'john', 'john123', 'normal_user'])
    writer.writerow(['2025-06-15 10:15:00', '203.0.113.45', 'admin', 'admin', 'attacker'])
    writer.writerow(['2025-06-15 10:20:00', '198.51.100.67', 'root', '123456', 'attacker'])
    writer.writerow(['2025-06-15 10:25:00', '203.0.113.89', 'administrator', 'password', 'attacker'])
    writer.writerow(['2025-06-15 10:30:00', '192.168.1.101', 'sarah', 'sarah2023', 'normal_user'])
    writer.writerow(['2025-06-15 10:35:00', '10.0.0.51', 'mike', 'complex_pass_456', 'normal_user'])

# Create other required files
with open('ip_cache.json', 'w') as f:
    json.dump({}, f)

with open('log_count.txt', 'w') as f:
    f.write('8')

print('Docker initialization completed successfully!')
"

EXPOSE 5000

CMD ["python", "app.py"]
