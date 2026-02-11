"""
ShopSwift India Admin API Tests
Tests: Admin metrics, retailers listing, search/filter, detail, subscription management, admin guard
Tokens:
  - Admin: demo_session_admin_12345678901234567890
  - Retailer: demo_session_retailer_12345678901234567890
Seeded retailers: user_seed_r1 (Priya Fashions), user_seed_r4 (Suresh Kirana)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Demo session credentials
ADMIN_SESSION_TOKEN = "demo_session_admin_12345678901234567890"
RETAILER_SESSION_TOKEN = "demo_session_retailer_12345678901234567890"

# Seeded test data
TEST_RETAILER_ID = "user_seed_r1"  # Priya Fashions
TEST_RETAILER_ID_2 = "user_seed_r4"  # Suresh Kirana


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_client(api_client):
    """Session with admin auth cookie"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    session.cookies.set("session_token", ADMIN_SESSION_TOKEN)
    return session


@pytest.fixture(scope="module")
def retailer_client(api_client):
    """Session with retailer auth cookie (for admin guard tests)"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    session.cookies.set("session_token", RETAILER_SESSION_TOKEN)
    return session


class TestAdminDemoLogin:
    """Admin demo login tests"""
    
    def test_demo_login_with_admin_role(self, api_client):
        """POST /api/auth/demo-login?role=admin should return admin user"""
        response = api_client.post(f"{BASE_URL}/api/auth/demo-login?role=admin")
        assert response.status_code == 200
        data = response.json()
        
        # Validate admin user data
        assert data["user_id"] == "user_demo_admin"
        assert data["email"] == "demo.admin@shopswift.in"
        assert data["name"] == "Demo Admin"
        assert data["role"] == "admin"
        
        # Check session cookie was set
        assert "session_token" in response.cookies or ADMIN_SESSION_TOKEN in str(response.cookies)
        print(f"✓ Admin demo login successful: {data['name']} (role={data['role']})")
    
    def test_demo_login_default_is_retailer(self, api_client):
        """POST /api/auth/demo-login without role should default to retailer"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/demo-login")
        assert response.status_code == 200
        data = response.json()
        
        # Default should be retailer
        assert data["role"] == "retailer"
        print(f"✓ Default demo login is retailer: {data['name']} (role={data['role']})")


class TestAuthMeWithAdmin:
    """GET /api/auth/me with admin user"""
    
    def test_auth_me_returns_admin_role(self, admin_client):
        """GET /api/auth/me should return user with role=admin"""
        response = admin_client.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == "user_demo_admin"
        assert data["role"] == "admin"
        assert data["email"] == "demo.admin@shopswift.in"
        print(f"✓ Auth me returns admin: {data['name']} (role={data['role']})")


class TestAdminMetrics:
    """GET /api/admin/metrics tests"""
    
    def test_get_platform_metrics(self, admin_client):
        """GET /api/admin/metrics should return platform-wide metrics"""
        response = admin_client.get(f"{BASE_URL}/api/admin/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Validate all required fields exist
        assert "total_retailers" in data
        assert "total_stores" in data
        assert "total_products" in data
        assert "total_orders" in data
        assert "total_revenue" in data
        assert "subscriptions" in data
        assert "tiers" in data
        assert "ondc_enabled_stores" in data
        assert "total_chat_messages" in data
        
        # Validate subscription breakdown
        assert "active" in data["subscriptions"]
        assert "expired" in data["subscriptions"]
        assert "cancelled" in data["subscriptions"]
        
        # Validate tier breakdown
        assert "basic" in data["tiers"]
        assert "pro" in data["tiers"]
        assert "premium" in data["tiers"]
        
        # Validate types
        assert isinstance(data["total_retailers"], int)
        assert isinstance(data["total_stores"], int)
        assert data["total_retailers"] > 0  # Should have seeded retailers
        
        print(f"✓ Platform metrics: {data['total_retailers']} retailers, {data['total_stores']} stores")
        print(f"  Subscriptions: active={data['subscriptions']['active']}, expired={data['subscriptions']['expired']}")
        print(f"  Tiers: basic={data['tiers']['basic']}, pro={data['tiers']['pro']}, premium={data['tiers']['premium']}")


class TestAdminGuard:
    """Admin guard (403 for non-admin users) tests"""
    
    def test_metrics_returns_403_for_retailer(self, retailer_client):
        """GET /api/admin/metrics with retailer token should return 403"""
        response = retailer_client.get(f"{BASE_URL}/api/admin/metrics")
        assert response.status_code == 403
        data = response.json()
        assert "Admin access required" in data["detail"]
        print("✓ Admin guard blocks retailer: 403 returned")
    
    def test_retailers_list_returns_403_for_retailer(self, retailer_client):
        """GET /api/admin/retailers with retailer token should return 403"""
        response = retailer_client.get(f"{BASE_URL}/api/admin/retailers")
        assert response.status_code == 403
        print("✓ Admin guard blocks retailer from retailers list: 403 returned")
    
    def test_metrics_returns_401_without_auth(self):
        """GET /api/admin/metrics without auth should return 401"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/admin/metrics")
        assert response.status_code == 401
        print("✓ Admin metrics returns 401 without auth")


class TestAdminRetailersList:
    """GET /api/admin/retailers tests"""
    
    def test_list_retailers_returns_non_admin_users(self, admin_client):
        """GET /api/admin/retailers should return list of non-admin retailers"""
        response = admin_client.get(f"{BASE_URL}/api/admin/retailers")
        assert response.status_code == 200
        data = response.json()
        
        # Should be a list
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Validate first retailer structure
        retailer = data[0]
        assert "user_id" in retailer
        assert "name" in retailer
        assert "email" in retailer
        assert "has_store" in retailer
        assert "store_name" in retailer
        assert "subscription_status" in retailer
        assert "subscription_tier" in retailer
        assert "product_count" in retailer
        assert "order_count" in retailer
        
        print(f"✓ Retailers list: {len(data)} retailers")
    
    def test_search_retailers_by_name(self, admin_client):
        """GET /api/admin/retailers?search=priya should filter by name"""
        response = admin_client.get(f"{BASE_URL}/api/admin/retailers?search=priya")
        assert response.status_code == 200
        data = response.json()
        
        # Should find Priya Fashions
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify search result
        found = any("priya" in r["name"].lower() or "priya" in r["email"].lower() for r in data)
        assert found, "Priya Fashions not found in search results"
        
        print(f"✓ Search by name 'priya': found {len(data)} result(s)")
    
    def test_filter_retailers_by_status(self, admin_client):
        """GET /api/admin/retailers?status=active should filter by subscription status"""
        response = admin_client.get(f"{BASE_URL}/api/admin/retailers?status=active")
        assert response.status_code == 200
        data = response.json()
        
        # All returned retailers should have active status
        assert isinstance(data, list)
        for r in data:
            assert r["subscription_status"] == "active", f"Non-active retailer found: {r['name']}"
        
        print(f"✓ Filter by status 'active': {len(data)} retailers")
    
    def test_filter_retailers_by_tier(self, admin_client):
        """GET /api/admin/retailers?tier=premium should filter by subscription tier"""
        response = admin_client.get(f"{BASE_URL}/api/admin/retailers?tier=premium")
        assert response.status_code == 200
        data = response.json()
        
        # All returned retailers should have premium tier
        assert isinstance(data, list)
        for r in data:
            assert r["subscription_tier"] == "premium", f"Non-premium retailer found: {r['name']}"
        
        print(f"✓ Filter by tier 'premium': {len(data)} retailers")


class TestAdminRetailerDetail:
    """GET /api/admin/retailers/{user_id} tests"""
    
    def test_get_retailer_detail(self, admin_client):
        """GET /api/admin/retailers/{user_id} should return full detail with products, orders, revenue"""
        response = admin_client.get(f"{BASE_URL}/api/admin/retailers/{TEST_RETAILER_ID}")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "user" in data
        assert "store" in data
        assert "products" in data
        assert "recent_orders" in data
        assert "total_revenue" in data
        assert "product_count" in data
        assert "order_count" in data
        
        # Validate user data
        assert data["user"]["user_id"] == TEST_RETAILER_ID
        assert data["user"]["name"] == "Priya Fashions"
        
        # Validate store data
        assert data["store"]["store_id"] == "store_seed_001"
        assert data["store"]["subscription_tier"] == "pro"
        
        print(f"✓ Retailer detail: {data['user']['name']}")
        print(f"  Store: {data['store']['store_name']} ({data['store']['subscription_status']})")
        print(f"  Stats: {data['product_count']} products, {data['order_count']} orders, ₹{data['total_revenue']} revenue")
    
    def test_get_nonexistent_retailer_returns_404(self, admin_client):
        """GET /api/admin/retailers/nonexistent should return 404"""
        response = admin_client.get(f"{BASE_URL}/api/admin/retailers/nonexistent_user_id")
        assert response.status_code == 404
        print("✓ Nonexistent retailer returns 404")


class TestAdminSubscriptionUpdate:
    """PATCH /api/admin/retailers/{user_id}/subscription tests"""
    
    def test_update_subscription_status_and_tier(self, admin_client):
        """PATCH /api/admin/retailers/{user_id}/subscription should update status and tier"""
        # Update subscription
        payload = {
            "subscription_status": "active",
            "subscription_tier": "premium"
        }
        response = admin_client.patch(
            f"{BASE_URL}/api/admin/retailers/{TEST_RETAILER_ID_2}/subscription",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        # Validate response
        assert data["message"] == "Subscription updated"
        assert data["subscription_status"] == "active"
        assert data["subscription_tier"] == "premium"
        
        print(f"✓ Subscription updated: {data['store_id']} -> {data['subscription_status']}, {data['subscription_tier']}")
        
        # Verify with GET
        verify_response = admin_client.get(f"{BASE_URL}/api/admin/retailers/{TEST_RETAILER_ID_2}")
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["store"]["subscription_status"] == "active"
        assert verify_data["store"]["subscription_tier"] == "premium"
        print(f"✓ Verified subscription change persisted")
    
    def test_update_subscription_invalid_user_returns_404(self, admin_client):
        """PATCH /api/admin/retailers/nonexistent/subscription should return 404"""
        payload = {"subscription_status": "active", "subscription_tier": "basic"}
        response = admin_client.patch(
            f"{BASE_URL}/api/admin/retailers/nonexistent_user/subscription",
            json=payload
        )
        assert response.status_code == 404
        print("✓ Update subscription for nonexistent user returns 404")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
