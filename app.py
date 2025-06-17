#!/usr/bin/env python3
"""
Alpha - Honeypot Threat Intelligence Solution
Main Flask Application

This is the core application file that implements a machine learning-powered
honeypot system for detecting and analyzing malicious login attempts.

Features:
- AI-powered threat detection using K-means clustering
- Real-time geolocation mapping of attacks
- Adaptive learning with automatic model retraining
- Deceptive admin panel for attacker engagement
- Comprehensive analytics dashboard

Author: Ryan Casey
License: MIT
"""

import csv
import joblib
import os
import json
import time
import requests
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, render_template, redirect, url_for, jsonify
from sklearn.cluster import KMeans
import numpy as np
from config import Config
import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime, timedelta

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Validate configuration
Config.validate_config()

if not app.debug:
    file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

MODEL_FILE = app.config['MODEL_FILE']
LOG_FILE = app.config['LOG_FILE']
IP_CACHE_FILE = app.config['IP_CACHE_FILE']
RETRAIN_THRESHOLD = app.config['RETRAIN_THRESHOLD']

# Initialize global variables for enhanced model
scaler = None
attacker_cluster = 2
feature_names = []

# Load or create model
if os.path.exists(MODEL_FILE):
    try:
        model_data = joblib.load(MODEL_FILE)
        if isinstance(model_data, dict):
            # New enhanced model format
            model = model_data['model']
            scaler = model_data.get('scaler')
            feature_names = model_data.get('feature_names', [])
            n_clusters = model_data.get('n_clusters', 2)
            
            # Find attacker cluster (highest threat indicators)
            attacker_cluster = 2  # Based on training results
        else:
            # Old simple model format
            model = model_data
            scaler = None
            attacker_cluster = 1
    except Exception as e:
        app.logger.error(f"Error loading model: {e}")
        model = KMeans(n_clusters=2)
        scaler = None
        attacker_cluster = 1
else:
    model = KMeans(n_clusters=2)
    scaler = None
    attacker_cluster = 1

# Track how many new logs since last training
if os.path.exists("log_count.txt"):
    with open("log_count.txt", "r") as f:
        new_logs_count = int(f.read())
else:
    new_logs_count = 0

# Load IP cache or create empty dict
if os.path.exists(IP_CACHE_FILE):
    with open(IP_CACHE_FILE, "r") as f:
        ip_cache = json.load(f)
else:
    ip_cache = {}

def extract_features_from_log_row(ip, username, password):
    """Extract enhanced features for better attack detection"""
    # Basic features
    username_len = len(username)
    password_len = len(password)
    ip_parts = ip.split('.')
    ip_score = sum(int(part) for part in ip_parts if part.isdigit())
    
    # Advanced features
    common_usernames = {"admin", "administrator", "root", "sa", "oracle", "test", "guest", "user"}
    weak_passwords = {"password", "123456", "admin", "password123", "12345", "qwerty", "abc123"}
    
    username_is_common = 1 if username.lower() in common_usernames else 0
    password_is_weak = 1 if password.lower() in weak_passwords else 0
    ip_entropy = len(set(ip_parts)) / 4.0  # IP diversity
    
    features = np.array([[
        username_len, password_len, ip_score,
        username_is_common, password_is_weak, ip_entropy
    ]])
    
    return features

def retrain_model():
    """Retrain the model with new data using enhanced features"""
    global model, new_logs_count, scaler, attacker_cluster

    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4:
                    timestamp, ip, username, password = row
                    features = extract_features_from_log_row(ip, username, password)
                    logs.append(features[0])  # Extract the array from the 2D array

    if len(logs) >= 10:
        try:
            from sklearn.preprocessing import StandardScaler
            
            X = np.array(logs)
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train model
            model = KMeans(n_clusters=5, random_state=42)
            model.fit(X_scaled)
            
            # Save enhanced model
            model_data = {
                'model': model,
                'scaler': scaler,
                'feature_names': ['username_length', 'password_length', 'ip_score', 
                                'username_is_common', 'password_is_weak', 'ip_entropy'],
                'n_clusters': 5
            }
            
            joblib.dump(model_data, MODEL_FILE)
            
            # Reset counter
            new_logs_count = 0
            with open("log_count.txt", "w") as f:
                f.write(str(new_logs_count))
                
            app.logger.info(f"Model retrained on {len(logs)} logs with enhanced features.")
            
        except Exception as e:
            app.logger.error(f"Retraining failed: {e}")
            # Fallback to simple retraining
            X = np.array(logs)
            model = KMeans(n_clusters=2, random_state=42)
            model.fit(X)
            joblib.dump(model, MODEL_FILE)

def log_attempt(ip, username, password):
    global new_logs_count
    timestamp = str(datetime.now())
    with open(LOG_FILE, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, ip, username, password])
    new_logs_count += 1
    with open("log_count.txt", "w") as f:
        f.write(str(new_logs_count))
    if new_logs_count >= RETRAIN_THRESHOLD:
        retrain_model()

def classify_with_model(ip, username, password):
    """Classify login attempt using enhanced ML model"""
    global model, scaler, attacker_cluster
    
    try:
        features = extract_features_from_log_row(ip, username, password)
        
        # Apply scaling if available
        if scaler is not None:
            features_scaled = scaler.transform(features)
        else:
            features_scaled = features
            
        prediction = model.predict(features_scaled)[0]
        
        # Check if this cluster is the attacker cluster
        is_attacker = (prediction == attacker_cluster)
        
        return "attacker" if is_attacker else "normal_user"
        
    except Exception as e:
        app.logger.error(f"Classification error: {e}")
        # Fallback to simple heuristic
        common_usernames = {"admin", "administrator", "root", "sa"}
        weak_passwords = {"password", "123456", "admin"}
        
        if username.lower() in common_usernames or password.lower() in weak_passwords:
            return "attacker"
        return "normal_user"

def get_ip_location(ip):
    if ip in ip_cache:
        return ip_cache[ip]

    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,lat,lon,query", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "success":
            ip_cache[ip] = {"lat": data["lat"], "lon": data["lon"], "country": data["country"]}
        else:
            app.logger.warning(f"Failed to get location for IP {ip}: {data.get('message', 'Unknown error')}")
            ip_cache[ip] = None
            
    except requests.RequestException as e:
        app.logger.error(f"Network error getting location for {ip}: {e}")
        ip_cache[ip] = None
    except Exception as e:
        app.logger.error(f"Unexpected error getting location for {ip}: {e}")
        ip_cache[ip] = None

    with open(IP_CACHE_FILE, "w") as f:
        json.dump(ip_cache, f)
    
    time.sleep(0.5)
    return ip_cache[ip]

def get_attackers_locations():
    ips = set()
    try:
        with open(LOG_FILE, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4:
                    _, ip, _, _ = row
                    ips.add(ip)
    except FileNotFoundError:
        pass

    locations = []
    for ip in ips:
        loc = get_ip_location(ip)
        if loc:
            locations.append({"ip": ip, "lat": loc["lat"], "lon": loc["lon"], "country": loc["country"]})
    return locations

def get_stats():
    # Example stats: total login attempts, total unique IPs, attackers count
    total_attempts = 0
    unique_ips = set()
    attacker_count = 0

    try:
        with open(LOG_FILE, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4:
                    total_attempts += 1
                    _, ip, username, password = row
                    unique_ips.add(ip)
                    if classify_with_model(ip, username, password) == "attacker":
                        attacker_count += 1
    except FileNotFoundError:
        pass

    return {
        "total_attempts": total_attempts,
        "unique_ips": len(unique_ips),
        "attacker_count": attacker_count
    }

def get_detailed_analytics():
    """Generate comprehensive analytics about attackers and attacks"""
    try:
        df = pd.read_csv(LOG_FILE, names=["timestamp", "ip", "username", "password"])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Basic stats
        total_attempts = len(df)
        unique_ips = df['ip'].nunique()
        
        # Classify all attempts
        attacker_attempts = []
        normal_attempts = []
        for _, row in df.iterrows():
            classification = classify_with_model(row['ip'], row['username'], row['password'])
            if classification == "attacker":
                attacker_attempts.append(row)
            else:
                normal_attempts.append(row)
        
        attacker_df = pd.DataFrame(attacker_attempts) if attacker_attempts else pd.DataFrame()
        
        analytics = {
            "basic_stats": {
                "total_attempts": total_attempts,
                "unique_ips": unique_ips,
                "attacker_count": len(attacker_attempts),
                "success_rate": round((len(attacker_attempts) / total_attempts * 100), 2) if total_attempts > 0 else 0
            },
            "top_usernames": dict(Counter(df["username"]).most_common(10)),
            "top_passwords": dict(Counter(df["password"]).most_common(10)),
            "top_attacker_ips": dict(Counter([a['ip'] for a in attacker_attempts]).most_common(10)),
            "attacks_by_hour": {},
            "attacks_by_day": {},
            "credential_patterns": {
                "avg_username_length": round(df['username'].str.len().mean(), 2),
                "avg_password_length": round(df['password'].str.len().mean(), 2),
                "common_username_patterns": [],
                "common_password_patterns": []
            },
            "recent_attacks": []
        }
          # Time-based analysis with complete hour coverage
        if not df.empty:
            df['hour'] = df['timestamp'].dt.hour
            df['date'] = df['timestamp'].dt.date
            
            # Ensure all 24 hours are represented
            hourly_counts = df.groupby('hour').size().to_dict()
            analytics["attacks_by_hour"] = {str(hour): hourly_counts.get(hour, 0) for hour in range(24)}
            
            # Daily analysis with last 7 days
            daily_counts = df.groupby('date').size().to_dict()
            analytics["attacks_by_day"] = {str(k): v for k, v in daily_counts.items()}
            
            # Add peak analysis
            if hourly_counts:
                peak_hour = max(hourly_counts.items(), key=lambda x: x[1])
                analytics["peak_hour"] = {
                    "hour": peak_hour[0],
                    "attacks": peak_hour[1]
                }
            
            # Add attack intensity analysis
            total_hours_with_attacks = len([h for h in hourly_counts.values() if h > 0])
            avg_attacks_per_active_hour = sum(hourly_counts.values()) / max(total_hours_with_attacks, 1)
            
            analytics["attack_intensity"] = {
                "active_hours": total_hours_with_attacks,
                "avg_per_active_hour": round(avg_attacks_per_active_hour, 1),
                "total_attacks_today": sum(hourly_counts.values())
            }
        else:
            # Initialize empty but complete hour structure
            analytics["attacks_by_hour"] = {str(hour): 0 for hour in range(24)}
            analytics["attacks_by_day"] = {}
            analytics["peak_hour"] = {"hour": 0, "attacks": 0}
            analytics["attack_intensity"] = {
                "active_hours": 0,
                "avg_per_active_hour": 0,
                "total_attacks_today": 0
            }
        
        # Pattern analysis
        usernames = df['username'].tolist()
        passwords = df['password'].tolist()
        
        # Common username patterns
        admin_variants = [u for u in usernames if 'admin' in u.lower()]
        root_variants = [u for u in usernames if 'root' in u.lower()]
        if admin_variants:
            analytics["credential_patterns"]["common_username_patterns"].append(f"Admin variants: {len(admin_variants)}")
        if root_variants:
            analytics["credential_patterns"]["common_username_patterns"].append(f"Root variants: {len(root_variants)}")
        
        # Common password patterns
        numeric_passwords = [p for p in passwords if p.isdigit()]
        simple_passwords = [p for p in passwords if p.lower() in ['password', '123456', 'admin', 'qwerty']]
        if numeric_passwords:
            analytics["credential_patterns"]["common_password_patterns"].append(f"Numeric only: {len(numeric_passwords)}")
        if simple_passwords:
            analytics["credential_patterns"]["common_password_patterns"].append(f"Common weak passwords: {len(simple_passwords)}")
        
        # Recent attacks (last 10)
        recent_df = df.tail(10)
        for _, row in recent_df.iterrows():
            location = get_ip_location(row['ip'])
            analytics["recent_attacks"].append({
                'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'ip': row['ip'],
                'username': row['username'],
                'password': row['password'],
                'classification': classify_with_model(row['ip'], row['username'], row['password']),
                'location': location['country'] if location else 'Unknown'
            })
        
        return analytics
    except Exception as e:
        app.logger.error(f"Error generating analytics: {e}")
        return {
            "basic_stats": {"total_attempts": 0, "unique_ips": 0, "attacker_count": 0, "success_rate": 0},
            "top_usernames": {}, "top_passwords": {}, "top_attacker_ips": {},
            "attacks_by_hour": {}, "attacks_by_day": {}, "credential_patterns": {},
            "recent_attacks": []
        }

def get_threat_intelligence():
    """Generate threat intelligence report"""
    try:
        with open(LOG_FILE, "r") as f:
            reader = csv.reader(f)
            attacks_by_country = defaultdict(int)
            repeated_ips = defaultdict(int)
            
            for row in reader:
                if len(row) >= 4:
                    _, ip, username, password = row
                    repeated_ips[ip] += 1
                    
                    if classify_with_model(ip, username, password) == "attacker":
                        location = get_ip_location(ip)
                        if location:
                            attacks_by_country[location['country']] += 1
        
        # Find persistent attackers (IPs with multiple attempts)
        persistent_attackers = {ip: count for ip, count in repeated_ips.items() if count > 1}
        
        return {
            "attacks_by_country": dict(attacks_by_country),
            "persistent_attackers": dict(sorted(persistent_attackers.items(), key=lambda x: x[1], reverse=True)[:10]),
            "total_countries": len(attacks_by_country),
            "most_active_country": max(attacks_by_country.items(), key=lambda x: x[1])[0] if attacks_by_country else "None"
        }
    except Exception as e:
        app.logger.error(f"Error generating threat intelligence: {e}")
        return {"attacks_by_country": {}, "persistent_attackers": {}, "total_countries": 0, "most_active_country": "None"}

@app.route("/api/stats")
def api_stats():
    stats = get_stats()
    return jsonify(stats)

@app.route("/api/analytics")
def api_analytics():
    analytics = get_detailed_analytics()
    return jsonify(analytics)

@app.route("/api/threat-intelligence")
def api_threat_intelligence():
    threat_data = get_threat_intelligence()
    return jsonify(threat_data)

@app.route("/api/recent-attempts")
def api_recent_attempts():
    attempts = []
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            for line in lines[-50:]:
                row = line.strip().split(',')
                if len(row) >= 4:
                    timestamp, ip, username, password = row
                    location = get_ip_location(ip)
                    attempts.append({
                        'timestamp': timestamp,
                        'ip': ip,
                        'username': username,
                        'classification': classify_with_model(ip, username, password),
                        'location': location
                    })
    except FileNotFoundError:
        pass
    
    return jsonify(attempts)

@app.route("/", methods=["GET", "POST"])
def login():
    ip = request.remote_addr

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        log_attempt(ip, username, password)

        user_type = classify_with_model(ip, username, password)

        if user_type == "attacker":
            return redirect(url_for("fake_admin_panel"))
        else:
            return "<h3>Login failed. Invalid credentials.</h3>"

    return render_template("login.html")

@app.route("/admin")
def fake_admin_panel():
    return render_template("admin.html")

@app.route("/dashboard")
def dashboard():
    stats = get_stats()
    attacker_locations = get_attackers_locations()
    return render_template("dashboard.html", stats=stats, attacker_locations=attacker_locations)

if __name__ == "__main__":
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
