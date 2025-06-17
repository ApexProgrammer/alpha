"""
Test Configuration for Alpha Honeypot Tests
"""

import os
import tempfile
import pytest
from app import app
from config import Config

class TestConfig(Config):
    """Test configuration class with safe defaults."""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    DEBUG = False
    LOG_FILE = 'test_logs.csv'
    MODEL_FILE = 'test_model.pkl'
    IP_CACHE_FILE = 'test_cache.json'
    RETRAIN_THRESHOLD = 5

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config.from_object(TestConfig)
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_log_data():
    """Sample CSV data for testing."""
    return [
        ['timestamp', 'ip', 'username', 'password', 'classification'],
        ['2025-06-15 10:00:00', '192.168.1.100', 'admin', 'password123', 'normal_user'],
        ['2025-06-15 10:05:00', '203.0.113.45', 'admin', 'admin', 'attacker'],
        ['2025-06-15 10:10:00', '198.51.100.67', 'root', '123456', 'attacker'],
    ]

@pytest.fixture
def sample_ip_cache():
    """Sample IP cache data for testing."""
    return {
        "192.168.1.100": {
            "lat": 40.7128,
            "lon": -74.0060,
            "country": "United States",
            "city": "New York"
        },
        "203.0.113.45": {
            "lat": 35.6762,
            "lon": 139.6503,
            "country": "Japan",
            "city": "Tokyo"
        }
    }
