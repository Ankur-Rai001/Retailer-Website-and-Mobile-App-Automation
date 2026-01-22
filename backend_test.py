import requests
import sys
import json
from datetime import datetime, timezone, timedelta
import uuid

class ShopSwiftAPITester:
    def __init__(self, base_url="https://retail-connect-40.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = None
        self.user_id = None
        self.store_id = None
        self.product_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.session_token:
            test_headers['Authorization'] = f'Bearer {self.session_token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                details += f", Expected: {expected_status}"
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details += f", Response: {response.text[:100]}"

            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json()
                except:
                    return {}
            return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_health_check(self):
        """Test API health check"""
        result = self.run_test("API Health Check", "GET", "", 200)
        return result is not None

    def create_test_session(self):
        """Create test user and session in MongoDB"""
        try:
            # Create test user and session directly in MongoDB
            import pymongo
            client = pymongo.MongoClient("mongodb://localhost:27017")
            db = client["shopswift_db"]
            
            # Generate test user
            self.user_id = f"test_user_{uuid.uuid4().hex[:12]}"
            self.session_token = f"test_session_{uuid.uuid4().hex[:16]}"
            
            # Insert test user
            user_doc = {
                "user_id": self.user_id,
                "email": f"test.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                "name": "Test User",
                "picture": "https://via.placeholder.com/150",
                "phone": None,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            db.users.insert_one(user_doc)
            
            # Insert test session with proper timezone
            from datetime import timezone, timedelta
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)
            session_doc = {
                "user_id": self.user_id,
                "session_token": self.session_token,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            db.user_sessions.insert_one(session_doc)
            
            print(f"✅ Created test user: {self.user_id}")
            print(f"✅ Created test session: {self.session_token}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create test session: {e}")
            return False

    def test_auth_me(self):
        """Test /api/auth/me endpoint"""
        result = self.run_test("Get Current User", "GET", "auth/me", 200)
        if result and result.get('user_id') == self.user_id:
            return True
        return False

    def test_create_store(self):
        """Test store creation with AI description"""
        store_data = {
            "store_name": f"Test Kirana Store {datetime.now().strftime('%H%M%S')}",
            "category": "grocery",
            "language": "en",
            "phone": "+91 9876543210",
            "address": "Test Address, Mumbai",
            "gst_number": "22AAAAA0000A1Z5"
        }
        
        result = self.run_test("Create Store", "POST", "stores", 201, store_data)
        if result and result.get('store_id'):
            self.store_id = result['store_id']
            # Check if AI description was generated
            if result.get('description') and len(result['description']) > 20:
                print(f"✅ AI Description Generated: {result['description'][:50]}...")
            return True
        return False

    def test_get_my_store(self):
        """Test get my store endpoint"""
        result = self.run_test("Get My Store", "GET", "stores/my-store", 200)
        return result is not None and result.get('store_id') == self.store_id

    def test_create_product(self):
        """Test product creation"""
        product_data = {
            "name": "Test Product - Tata Salt 1kg",
            "description": "Premium quality salt for daily cooking",
            "price": 25.50,
            "stock": 100,
            "category": "Groceries",
            "images": []
        }
        
        result = self.run_test("Create Product", "POST", "products", 201, product_data)
        if result and result.get('product_id'):
            self.product_id = result['product_id']
            return True
        return False

    def test_get_products(self):
        """Test get products endpoint"""
        result = self.run_test("Get Products", "GET", "products", 200)
        return result is not None and isinstance(result, list)

    def test_update_product(self):
        """Test product update"""
        if not self.product_id:
            return False
            
        update_data = {
            "price": 30.00,
            "stock": 150
        }
        
        result = self.run_test("Update Product", "PATCH", f"products/{self.product_id}", 200, update_data)
        return result is not None

    def test_get_orders(self):
        """Test get orders endpoint"""
        result = self.run_test("Get Orders", "GET", "orders", 200)
        return result is not None and isinstance(result, list)

    def test_get_analytics(self):
        """Test analytics overview endpoint"""
        result = self.run_test("Get Analytics Overview", "GET", "analytics/overview", 200)
        if result is not None:
            required_fields = ['total_products', 'total_orders', 'total_revenue', 'pending_orders']
            return all(field in result for field in required_fields)
        return False

    def test_get_templates(self):
        """Test get templates endpoint"""
        result = self.run_test("Get Templates", "GET", "templates", 200)
        return result is not None and isinstance(result, list) and len(result) > 0

    def test_update_store_settings(self):
        """Test store settings update"""
        if not self.store_id:
            return False
            
        update_data = {
            "ondc_enabled": True,
            "template_id": "modern_minimal"
        }
        
        result = self.run_test("Update Store Settings", "PATCH", f"stores/{self.store_id}", 200, update_data)
        return result is not None

    def test_logout(self):
        """Test logout endpoint"""
        result = self.run_test("Logout", "POST", "auth/logout", 200, {})
        return result is not None

    def cleanup_test_data(self):
        """Clean up test data from MongoDB"""
        try:
            import pymongo
            client = pymongo.MongoClient("mongodb://localhost:27017")
            db = client["shopswift_db"]
            
            # Clean up test data
            db.users.delete_many({"user_id": self.user_id})
            db.user_sessions.delete_many({"user_id": self.user_id})
            if self.store_id:
                db.stores.delete_many({"store_id": self.store_id})
                db.products.delete_many({"store_id": self.store_id})
            
            print(f"✅ Cleaned up test data for user: {self.user_id}")
            
        except Exception as e:
            print(f"⚠️ Failed to cleanup test data: {e}")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting ShopSwift India API Tests")
        print("=" * 50)
        
        # Test basic connectivity
        if not self.test_health_check():
            print("❌ API health check failed. Stopping tests.")
            return False
        
        # Create test session
        if not self.create_test_session():
            print("❌ Failed to create test session. Stopping tests.")
            return False
        
        # Run authentication tests
        self.test_auth_me()
        
        # Run store tests
        self.test_create_store()
        self.test_get_my_store()
        
        # Run product tests
        self.test_create_product()
        self.test_get_products()
        self.test_update_product()
        
        # Run other endpoint tests
        self.test_get_orders()
        self.test_get_analytics()
        self.test_get_templates()
        self.test_update_store_settings()
        
        # Test logout
        self.test_logout()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print results
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️ Some tests failed. Check details above.")
            return False

def main():
    tester = ShopSwiftAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())