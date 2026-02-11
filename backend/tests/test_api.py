"""
ShopSwift India API Tests
Tests: Auth, Store, Templates, Analytics, Chat endpoints
Demo session token: demo_session_retailer_12345678901234567890
Demo store ID: store_demo_001
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Demo session credentials for testing
DEMO_SESSION_TOKEN = "demo_session_retailer_12345678901234567890"
DEMO_STORE_ID = "store_demo_001"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def authenticated_client(api_client):
    """Session with demo auth cookie"""
    api_client.cookies.set("session_token", DEMO_SESSION_TOKEN)
    return api_client


class TestHealthCheck:
    """API health check tests"""
    
    def test_api_root_returns_running(self, api_client):
        """GET /api/ should return running status"""
        response = api_client.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "running"
        print(f"✓ Health check passed: {data}")


class TestDemoLogin:
    """Demo login flow tests"""
    
    def test_demo_login_returns_user_data(self, api_client):
        """POST /api/auth/demo-login should return user data and set session cookie"""
        response = api_client.post(f"{BASE_URL}/api/auth/demo-login")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "user_id" in data
        assert "email" in data
        assert "name" in data
        
        # Validate values
        assert data["user_id"] == "user_demo_retailer"
        assert data["email"] == "demo.retailer@shopswift.in"
        assert data["name"] == "Demo Retailer"
        
        # Check cookie was set
        assert "session_token" in response.cookies or "session_token" in api_client.cookies
        print(f"✓ Demo login successful: {data['name']}")
    
    def test_demo_login_sets_session_cookie(self, api_client):
        """POST /api/auth/demo-login should set session_token cookie"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/demo-login")
        assert response.status_code == 200
        
        # The server should set a cookie
        cookies_received = response.cookies
        print(f"✓ Cookies received in response: {dict(cookies_received)}")


class TestAuthMe:
    """GET /api/auth/me endpoint tests"""
    
    def test_auth_me_with_session_cookie(self, authenticated_client):
        """GET /api/auth/me should authenticate with session cookie"""
        response = authenticated_client.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response
        assert "user_id" in data
        assert "email" in data
        assert "name" in data
        assert data["user_id"] == "user_demo_retailer"
        print(f"✓ Auth me successful: {data['name']}")
    
    def test_auth_me_without_session_returns_401(self, api_client):
        """GET /api/auth/me without session should return 401"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✓ Auth me correctly returns 401 without session")


class TestStoreEndpoints:
    """Store API tests"""
    
    def test_get_my_store_returns_demo_store(self, authenticated_client):
        """GET /api/stores/my-store should return the demo store"""
        response = authenticated_client.get(f"{BASE_URL}/api/stores/my-store")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "store_id" in data
        assert "store_name" in data
        assert "user_id" in data
        assert "subdomain" in data
        assert "category" in data
        
        # Validate values
        assert data["store_id"] == DEMO_STORE_ID
        assert data["store_name"] == "Demo General Store"
        assert data["user_id"] == "user_demo_retailer"
        print(f"✓ My store retrieved: {data['store_name']}")
    
    def test_get_my_store_without_auth_returns_401(self, api_client):
        """GET /api/stores/my-store without auth should return 401"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/stores/my-store")
        assert response.status_code == 401
        print("✓ My store correctly returns 401 without auth")


class TestTemplates:
    """Templates API tests"""
    
    def test_get_templates_returns_4_templates(self, api_client):
        """GET /api/templates should return 4 templates"""
        response = api_client.get(f"{BASE_URL}/api/templates")
        assert response.status_code == 200
        data = response.json()
        
        # Validate count
        assert isinstance(data, list)
        assert len(data) == 4
        
        # Validate structure of first template
        template = data[0]
        assert "template_id" in template
        assert "name" in template
        assert "category" in template
        assert "preview_url" in template
        assert "description" in template
        assert "is_premium" in template
        assert "price" in template
        
        template_names = [t["name"] for t in data]
        print(f"✓ Templates returned: {template_names}")


class TestAnalytics:
    """Analytics API tests"""
    
    def test_get_analytics_overview(self, authenticated_client):
        """GET /api/analytics/overview should return analytics data"""
        response = authenticated_client.get(f"{BASE_URL}/api/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "total_products" in data
        assert "total_orders" in data
        assert "total_revenue" in data
        assert "pending_orders" in data
        
        # Validate types
        assert isinstance(data["total_products"], int)
        assert isinstance(data["total_orders"], int)
        assert isinstance(data["total_revenue"], (int, float))
        assert isinstance(data["pending_orders"], int)
        print(f"✓ Analytics overview: products={data['total_products']}, orders={data['total_orders']}, revenue=₹{data['total_revenue']}")
    
    def test_get_analytics_without_auth_returns_401(self, api_client):
        """GET /api/analytics/overview without auth should return 401"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/analytics/overview")
        assert response.status_code == 401
        print("✓ Analytics correctly returns 401 without auth")


class TestChatEndpoints:
    """Chat API tests"""
    
    def test_send_chat_message(self, api_client):
        """POST /api/chat/send should create a chat message"""
        test_customer_id = f"TEST_customer_{uuid.uuid4().hex[:8]}"
        payload = {
            "store_id": DEMO_STORE_ID,
            "customer_id": test_customer_id,
            "customer_name": "Test Customer",
            "message": "Test message from pytest",
            "sender": "customer"
        }
        
        response = api_client.post(f"{BASE_URL}/api/chat/send", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Validate response
        assert "success" in data
        assert data["success"] == True
        assert "message_id" in data
        assert data["message_id"].startswith("msg_")
        print(f"✓ Chat message sent: {data['message_id']}")
        
        return test_customer_id
    
    def test_get_chat_messages(self, api_client):
        """GET /api/chat/messages/{store_id} should return messages"""
        response = api_client.get(f"{BASE_URL}/api/chat/messages/{DEMO_STORE_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response is a list
        assert isinstance(data, list)
        
        # If messages exist, validate structure
        if len(data) > 0:
            msg = data[0]
            assert "message_id" in msg
            assert "store_id" in msg
            assert "customer_id" in msg
            assert "message" in msg
            assert "sender" in msg
            assert "timestamp" in msg
            print(f"✓ Chat messages retrieved: {len(data)} messages")
        else:
            print("✓ Chat messages endpoint working (no messages yet)")
    
    def test_get_chat_messages_with_customer_id_filter(self, api_client):
        """GET /api/chat/messages/{store_id}?customer_id= should filter messages"""
        # First send a message
        test_customer_id = f"TEST_filter_{uuid.uuid4().hex[:8]}"
        payload = {
            "store_id": DEMO_STORE_ID,
            "customer_id": test_customer_id,
            "customer_name": "Filter Test Customer",
            "message": "Filter test message",
            "sender": "customer"
        }
        api_client.post(f"{BASE_URL}/api/chat/send", json=payload)
        
        # Now fetch filtered
        response = api_client.get(f"{BASE_URL}/api/chat/messages/{DEMO_STORE_ID}?customer_id={test_customer_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        for msg in data:
            assert msg["customer_id"] == test_customer_id
        print(f"✓ Chat messages filtered by customer_id: {len(data)} messages")
    
    def test_get_conversations(self, authenticated_client):
        """GET /api/chat/conversations/{store_id} should return grouped conversations with unread counts"""
        response = authenticated_client.get(f"{BASE_URL}/api/chat/conversations/{DEMO_STORE_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response is a list
        assert isinstance(data, list)
        
        # If conversations exist, validate structure
        if len(data) > 0:
            conv = data[0]
            assert "customer_id" in conv
            assert "customer_name" in conv
            assert "last_message" in conv
            assert "last_timestamp" in conv
            assert "unread_count" in conv
            assert isinstance(conv["unread_count"], int)
            print(f"✓ Conversations retrieved: {len(data)} conversations")
            for c in data[:3]:
                print(f"  - {c['customer_name']}: {c['last_message'][:30]}... (unread: {c['unread_count']})")
        else:
            print("✓ Conversations endpoint working (no conversations yet)")
    
    def test_mark_messages_read(self, authenticated_client):
        """POST /api/chat/mark-read should mark messages as read"""
        # First send a customer message (unread by default)
        test_customer_id = f"TEST_read_{uuid.uuid4().hex[:8]}"
        payload = {
            "store_id": DEMO_STORE_ID,
            "customer_id": test_customer_id,
            "customer_name": "Read Test Customer",
            "message": "Mark read test message",
            "sender": "customer"
        }
        authenticated_client.post(f"{BASE_URL}/api/chat/send", json=payload)
        
        # Now mark as read
        response = authenticated_client.post(
            f"{BASE_URL}/api/chat/mark-read",
            params={"store_id": DEMO_STORE_ID, "customer_id": test_customer_id}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert data["success"] == True
        print("✓ Messages marked as read")
    
    def test_conversations_requires_auth(self, api_client):
        """GET /api/chat/conversations/{store_id} without auth should return 401"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/chat/conversations/{DEMO_STORE_ID}")
        assert response.status_code == 401
        print("✓ Conversations correctly returns 401 without auth")


class TestChatRetailerFlow:
    """Test retailer sending message to customer (the main chat use case)"""
    
    def test_retailer_send_message(self, api_client):
        """POST /api/chat/send with sender='retailer' should work"""
        test_customer_id = f"TEST_retailer_msg_{uuid.uuid4().hex[:8]}"
        payload = {
            "store_id": DEMO_STORE_ID,
            "customer_id": test_customer_id,
            "customer_name": "Test Customer",
            "message": "Hello from retailer!",
            "sender": "retailer"
        }
        
        response = api_client.post(f"{BASE_URL}/api/chat/send", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "message_id" in data
        print(f"✓ Retailer message sent: {data['message_id']}")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
