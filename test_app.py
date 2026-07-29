import pytest
import json
from app import app  # Imports your Flask app from app.py

@pytest.fixture
def client():
    """
    Setup the Flask test client. This runs before every test.
    It configures the app for testing so exceptions are caught properly.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_valid_login(client):
    """
    Test the Login API with CORRECT credentials.
    Expected: Returns HTTP 200, success = True, and includes a balance.
    """
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    response = client.post('/', data=json.dumps(payload), content_type='application/json')
    
    assert response.status_code == 200, "Should return a 200 OK status"
    
    data = json.loads(response.data)
    assert data.get('success') is True, "Login should be successful"
    assert 'balance' in data, "Successful login should return the user's balance"

def test_invalid_login(client):
    """
    Test the Login API with WRONG credentials.
    Expected: Returns success = False or a 401 Unauthorized status.
    """
    payload = {
        "username": "hacker",
        "password": "wrongpassword"
    }
    response = client.post('/', data=json.dumps(payload), content_type='application/json')
    
    data = json.loads(response.data)
    assert data.get('success') is False, "Login should fail for invalid credentials"

def test_get_transactions(client):
    """
    Test fetching the transaction history.
    Expected: Returns HTTP 200 and a JSON list (array) of transactions.
    """
    response = client.get('/api/transactions')
    
    assert response.status_code == 200, "Should return 200 OK status"
    
    data = json.loads(response.data)
    assert isinstance(data, list), "Transactions should be returned as a JSON list"

def test_create_transaction(client):
    """
    Test making a new payment via the Transactions API.
    Expected: Returns HTTP 200 or 201, and success = True.
    """
    payload = {
        "name": "Test Postman Transfer",
        "upi": "postman@upi",
        "amount": 500
    }
    response = client.post('/api/transactions', data=json.dumps(payload), content_type='application/json')
    
    assert response.status_code in [200, 201], "Should return success status code"
    
    data = json.loads(response.data)
    # Some APIs might just return HTTP status codes, but your frontend expects this JSON:
    assert data.get('success') is True or data.get('message') is not None, "API should confirm transaction creation"

def test_empty_transaction(client):
    """
    Test making a payment with NO amount.
    Expected: API should reject it with a 400 Bad Request.
    """
    payload = {
        "name": "Invalid Transfer",
        "upi": "invalid@upi",
        "amount": 0
    }
    response = client.post('/api/transactions', data=json.dumps(payload), content_type='application/json')
    
    # Ideally, your backend should block this and return 400
    assert response.status_code == 400 or json.loads(response.data).get('success') is False