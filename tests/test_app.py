"""
Basic Tests for Alpha Honeypot Flask Application
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestBasicRoutes:
    """Test basic Flask routes."""
    
    def test_index_route(self, client):
        """Test the main index route returns login page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_dashboard_route(self, client):
        """Test the dashboard route is accessible."""
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'dashboard' in response.data.lower()
    
    def test_admin_route(self, client):
        """Test the admin route is accessible."""
        response = client.get('/admin')
        assert response.status_code == 200
        assert b'admin' in response.data.lower()


class TestLoginFunctionality:
    """Test login attempt processing."""
    
    @patch('app.log_attempt')
    @patch('app.classify_user')
    def test_login_normal_user(self, mock_classify, mock_log, client):
        """Test login with normal user classification."""
        mock_classify.return_value = 'normal_user'
        mock_log.return_value = None
        
        response = client.post('/', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        assert response.status_code == 200
        mock_classify.assert_called_once()
        mock_log.assert_called_once()
    
    @patch('app.log_attempt')
    @patch('app.classify_user')
    def test_login_attacker(self, mock_classify, mock_log, client):
        """Test login with attacker classification."""
        mock_classify.return_value = 'attacker'
        mock_log.return_value = None
        
        response = client.post('/', data={
            'username': 'admin',
            'password': 'admin'
        })
        
        # Should redirect to admin panel
        assert response.status_code == 302
        mock_classify.assert_called_once()
        mock_log.assert_called_once()


class TestAPIEndpoints:
    """Test API endpoints."""
    
    @patch('app.get_stats')
    def test_api_stats(self, mock_stats, client):
        """Test the stats API endpoint."""
        mock_stats.return_value = {
            'total_attempts': 100,
            'unique_ips': 50,
            'attackers_detected': 25
        }
        
        response = client.get('/api/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'total_attempts' in data
        assert data['total_attempts'] == 100


class TestSecurityFeatures:
    """Test security-related functionality."""
    
    def test_input_sanitization(self, client):
        """Test that dangerous inputs are handled safely."""
        dangerous_inputs = [
            '<script>alert("xss")</script>',
            '../../etc/passwd',
            "'; DROP TABLE users; --",
            '\x00\x01\x02'
        ]
        
        for dangerous_input in dangerous_inputs:
            response = client.post('/', data={
                'username': dangerous_input,
                'password': dangerous_input
            })
            # Should not crash and should return a valid response
            assert response.status_code in [200, 302]
    
    def test_empty_inputs(self, client):
        """Test handling of empty inputs."""
        response = client.post('/', data={
            'username': '',
            'password': ''
        })
        assert response.status_code in [200, 302]
    
    def test_large_inputs(self, client):
        """Test handling of unusually large inputs."""
        large_input = 'A' * 10000
        response = client.post('/', data={
            'username': large_input,
            'password': large_input
        })
        assert response.status_code in [200, 302]


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_missing_form_data(self, client):
        """Test POST request without form data."""
        response = client.post('/')
        assert response.status_code in [200, 400, 302]
    
    def test_invalid_methods(self, client):
        """Test unsupported HTTP methods."""
        response = client.put('/')
        assert response.status_code == 405
        
        response = client.delete('/')
        assert response.status_code == 405
    
    def test_nonexistent_routes(self, client):
        """Test accessing non-existent routes."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
