#!/usr/bin/env python3
"""
Alpha - Honeypot Threat Intelligence Solution Setup Script
This script initializes the honeypot system with default data and configurations.
"""

import os
import sys
import csv
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def create_initial_logs():
    """Create initial logs.csv file with sample data if it doesn't exist."""
    if not os.path.exists('logs.csv'):
        print("📝 Creating initial logs.csv file...")
        
        # Sample data for initial model training
        sample_data = [
            ['timestamp', 'ip', 'username', 'password', 'classification'],
            ['2025-06-15 10:00:00', '192.168.1.100', 'admin', 'password123', 'normal_user'],
            ['2025-06-15 10:05:00', '10.0.0.50', 'user', 'mypassword', 'normal_user'],
            ['2025-06-15 10:10:00', '172.16.0.25', 'john', 'john123', 'normal_user'],
            ['2025-06-15 10:15:00', '203.0.113.45', 'admin', 'admin', 'attacker'],
            ['2025-06-15 10:20:00', '198.51.100.67', 'root', '123456', 'attacker'],
            ['2025-06-15 10:25:00', '203.0.113.89', 'administrator', 'password', 'attacker'],
            ['2025-06-15 10:30:00', '192.168.1.101', 'sarah', 'sarah2023', 'normal_user'],
            ['2025-06-15 10:35:00', '10.0.0.51', 'mike', 'complex_pass_456', 'normal_user'],
        ]
        
        with open('logs.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(sample_data)
        
        print("✅ Initial logs.csv created with sample data")

def create_initial_model():
    """Create initial machine learning model if it doesn't exist."""
    if not os.path.exists('honeypot_model.pkl'):
        print("🤖 Creating initial ML model...")
        
        # Load the sample data
        df = pd.read_csv('logs.csv')
        
        # Feature engineering
        def ip_to_int(ip):
            """Convert IP address to integer for ML processing."""
            try:
                parts = ip.split('.')
                return sum(int(part) * (256 ** (3 - i)) for i, part in enumerate(parts))
            except:
                return 0
        
        df['username_length'] = df['username'].str.len()
        df['password_length'] = df['password'].str.len()
        df['ip_numeric'] = df['ip'].apply(ip_to_int)
        
        # Prepare features
        features = ['username_length', 'password_length', 'ip_numeric']
        X = df[features].values
        
        # Normalize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train K-means model
        model = KMeans(n_clusters=2, random_state=42, n_init=10)
        model.fit(X_scaled)
        
        # Save model with metadata
        model_data = {
            'model': model,
            'scaler': scaler,
            'feature_names': features,
            'n_clusters': 2,
            'version': '1.0'
        }
        
        joblib.dump(model_data, 'honeypot_model.pkl')
        print("✅ Initial ML model created and saved")

def create_ip_cache():
    """Create initial IP cache file if it doesn't exist."""
    if not os.path.exists('ip_cache.json'):
        print("🌍 Creating initial IP cache...")
        
        # Sample cache data to prevent immediate API calls
        cache_data = {
            "192.168.1.100": {"lat": 40.7128, "lon": -74.0060, "country": "United States", "city": "New York"},
            "10.0.0.50": {"lat": 51.5074, "lon": -0.1278, "country": "United Kingdom", "city": "London"},
            "172.16.0.25": {"lat": 48.8566, "lon": 2.3522, "country": "France", "city": "Paris"},
            "203.0.113.45": {"lat": 35.6762, "lon": 139.6503, "country": "Japan", "city": "Tokyo"},
            "198.51.100.67": {"lat": -33.8688, "lon": 151.2093, "country": "Australia", "city": "Sydney"},
        }
        
        with open('ip_cache.json', 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print("✅ Initial IP cache created")

def create_log_count():
    """Create log count file to track model retraining."""
    if not os.path.exists('log_count.txt'):
        print("📊 Creating log count file...")
        with open('log_count.txt', 'w') as f:
            f.write('8')  # Number of initial sample records
        print("✅ Log count file created")

def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    if not os.path.exists('.env') and os.path.exists('.env.example'):
        print("⚙️ Creating .env file from template...")
        
        # Read .env.example and create .env
        with open('.env.example', 'r') as f:
            content = f.read()
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print("✅ .env file created from .env.example")
        print("🔧 Please review and update .env file with your preferred settings")

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask', 'scikit-learn', 'pandas', 'numpy', 
        'requests', 'joblib', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def main():
    """Main setup function."""
    print("🍯 Alpha - Honeypot Threat Intelligence Solution Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create necessary files
    create_env_file()
    create_initial_logs()
    create_initial_model()
    create_ip_cache()
    create_log_count()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Review and update .env file if needed")
    print("2. Run the application: python app.py")
    print("3. Access the honeypot at: http://localhost:5000")
    print("4. View the dashboard at: http://localhost:5000/dashboard")
    print("\n⚠️  Remember: This is for educational purposes only!")

if __name__ == "__main__":
    main()
