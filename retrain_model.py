"""
Retrain the honeypot ML model with realistic attack data
This will create a much better classifier for detecting real attacks
"""

import csv
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib
import matplotlib.pyplot as plt

def analyze_and_retrain():
    """Analyze the log data and retrain the model with better features"""
    
    print("🧠 Advanced ML Model Training for Honeypot")
    print("=" * 50)
      # Load the logs
    try:
        df = pd.read_csv("logs.csv", names=["timestamp", "ip", "username", "password"])
        print(f"📊 Loaded {len(df)} log entries for training")
    except FileNotFoundError:
        print("❌ No logs.csv found. Run the setup script first!")
        return
    
    # Extract enhanced features
    features = []
    feature_names = [
        "username_length", "password_length", "ip_score", 
        "username_is_common", "password_is_weak", "ip_entropy"
    ]
    
    # Common attacker indicators
    common_usernames = {"admin", "administrator", "root", "sa", "oracle", "test", "guest", "user"}
    weak_passwords = {"password", "123456", "admin", "password123", "12345", "qwerty", "abc123"}
    
    print("🔍 Extracting advanced features...")
    
    for _, row in df.iterrows():
        ip, username, password = row["ip"], row["username"], row["password"]
        
        # Basic features
        username_len = len(username)
        password_len = len(password)
        ip_parts = ip.split('.')
        ip_score = sum(int(part) for part in ip_parts if part.isdigit())
        
        # Advanced features
        username_is_common = 1 if username.lower() in common_usernames else 0
        password_is_weak = 1 if password.lower() in weak_passwords else 0
        
        # IP entropy (randomness indicator)
        ip_entropy = len(set(ip_parts)) / 4.0  # Diversity of IP octets
        
        features.append([
            username_len, password_len, ip_score,
            username_is_common, password_is_weak, ip_entropy
        ])
    
    # Convert to numpy array and scale features
    X = np.array(features)
    
    # Standardize features for better clustering
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Find optimal number of clusters
    print("🎯 Finding optimal clustering parameters...")
    silhouette_scores = []
    K_range = range(2, 6)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X_scaled)
        silhouette_avg = silhouette_score(X_scaled, cluster_labels)
        silhouette_scores.append(silhouette_avg)
        print(f"   K={k}: Silhouette Score = {silhouette_avg:.3f}")
    
    # Use the best K
    best_k = K_range[np.argmax(silhouette_scores)]
    print(f"✅ Best number of clusters: {best_k}")
    
    # Train final model
    final_model = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    cluster_labels = final_model.fit_predict(X_scaled)
    
    # Analyze clusters to identify attacker vs normal patterns
    print("\n📈 Cluster Analysis:")
    for i in range(best_k):
        cluster_mask = cluster_labels == i
        cluster_data = X[cluster_mask]
        
        avg_username_len = np.mean(cluster_data[:, 0])
        avg_password_len = np.mean(cluster_data[:, 1])
        common_username_rate = np.mean(cluster_data[:, 3])
        weak_password_rate = np.mean(cluster_data[:, 4])
        
        cluster_size = np.sum(cluster_mask)
        
        print(f"   Cluster {i} ({cluster_size} entries):")
        print(f"      Avg username length: {avg_username_len:.1f}")
        print(f"      Avg password length: {avg_password_len:.1f}")
        print(f"      Common username rate: {common_username_rate:.2%}")
        print(f"      Weak password rate: {weak_password_rate:.2%}")
        
        # Heuristic: cluster with higher rates of common usernames and weak passwords = attackers
        if common_username_rate > 0.3 or weak_password_rate > 0.3:
            print(f"      🚨 LIKELY ATTACKERS")
        else:
            print(f"      👤 Likely normal users")
        print()
    
    # Save the trained model and scaler
    model_data = {
        'model': final_model,
        'scaler': scaler,
        'feature_names': feature_names,
        'n_clusters': best_k
    }
    
    joblib.dump(model_data, "honeypot_model.pkl")
    print("💾 Saved enhanced model to honeypot_model.pkl")
    
    # Create a simple classification function for the main app
    print("🔧 Creating classification rules...")
    
    # Analyze which cluster has more attacker characteristics
    attacker_cluster = -1
    max_attacker_score = 0
    
    for i in range(best_k):
        cluster_mask = cluster_labels == i
        cluster_data = X[cluster_mask]
        
        common_rate = np.mean(cluster_data[:, 3])
        weak_rate = np.mean(cluster_data[:, 4])
        attacker_score = common_rate + weak_rate
        
        if attacker_score > max_attacker_score:
            max_attacker_score = attacker_score
            attacker_cluster = i
    
    print(f"🎯 Cluster {attacker_cluster} identified as primary attacker cluster")
    
    # Test the model
    print("\n🧪 Testing model on sample data:")
    test_cases = [
        ("192.168.1.100", "admin", "password", "Should be: ATTACKER"),
        ("76.125.32.45", "john.smith", "MySecureP@ssw0rd2025", "Should be: NORMAL"),
        ("45.95.168.123", "root", "123456", "Should be: ATTACKER"),
        ("10.0.0.50", "sarah.wilson", "FamilyVacation2025", "Should be: NORMAL")
    ]
    
    for ip, username, password, expected in test_cases:
        # Extract features
        ip_parts = ip.split('.')
        ip_score = sum(int(part) for part in ip_parts if part.isdigit())
        username_is_common = 1 if username.lower() in common_usernames else 0
        password_is_weak = 1 if password.lower() in weak_passwords else 0
        ip_entropy = len(set(ip_parts)) / 4.0
        
        test_features = np.array([[
            len(username), len(password), ip_score,
            username_is_common, password_is_weak, ip_entropy
        ]])
        
        test_scaled = scaler.transform(test_features)
        prediction = final_model.predict(test_scaled)[0]
        
        result = "ATTACKER" if prediction == attacker_cluster else "NORMAL USER"
        print(f"   {username}@{ip}: {result} ({expected})")
    
    print(f"\n🎉 Model training complete!")
    print(f"   • Used {len(df)} training samples")
    print(f"   • {best_k} clusters identified")
    print(f"   • Enhanced features for better detection")
    print(f"   • Ready for real-time threat detection!")

if __name__ == "__main__":
    analyze_and_retrain()
