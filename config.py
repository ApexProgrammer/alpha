"""
Alpha - Honeypot Threat Intelligence Solution
Configuration Management Module

This module handles all configuration settings for the honeypot system,
including security settings, file paths, and runtime parameters.
"""

import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class for the Alpha Honeypot system.
    
    All configuration values can be overridden via environment variables
    for secure deployment in different environments.
    """
    
    # Security Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # File Paths
    LOG_FILE = os.environ.get('LOG_FILE', 'logs.csv')
    MODEL_FILE = os.environ.get('MODEL_FILE', 'honeypot_model.pkl')
    IP_CACHE_FILE = os.environ.get('IP_CACHE_FILE', 'ip_cache.json')
    
    # Machine Learning Configuration
    RETRAIN_THRESHOLD = int(os.environ.get('RETRAIN_THRESHOLD', '10'))
    
    # Server Configuration
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '127.0.0.1')  # More secure default
    PORT = int(os.environ.get('PORT', '5000'))
    
    # API Configuration
    GEOLOCATION_API_URL = "http://ip-api.com/json/"
    REQUEST_TIMEOUT = 5  # seconds
    
    # Logging Configuration
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings."""
        if cls.DEBUG and cls.SECRET_KEY == 'dev-key-change-in-production':
            print("⚠️  WARNING: Using default secret key in debug mode!")
        
        if cls.HOST == '0.0.0.0' and not cls.DEBUG:
            print("⚠️  WARNING: Binding to all interfaces in production mode!")
        
        return True
