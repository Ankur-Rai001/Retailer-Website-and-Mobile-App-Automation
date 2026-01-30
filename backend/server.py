from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, Header
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import razorpay
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio
import requests
import zipfile
import io
import shutil

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Razorpay client
razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID", "test_key"), os.getenv("RAZORPAY_KEY_SECRET", "test_secret")))

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ============ MODELS ============

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: EmailStr
    name: str
    phone: Optional[str] = None
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Store(BaseModel):
    model_config = ConfigDict(extra="ignore")
    store_id: str = Field(default_factory=lambda: f"store_{uuid.uuid4().hex[:12]}")
    user_id: str
    store_name: str
    subdomain: str
    custom_domain: Optional[str] = None
    template_id: str = "default"
    logo_url: Optional[str] = None
    description: Optional[str] = None
    category: str = "general"
    language: str = "en"
    subscription_status: str = "trial"
    subscription_tier: str = "basic"
    gst_number: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    ondc_enabled: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    product_id: str = Field(default_factory=lambda: f"prod_{uuid.uuid4().hex[:12]}")
    store_id: str
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    images: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    variants: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    order_id: str = Field(default_factory=lambda: f"order_{uuid.uuid4().hex[:12]}")
    store_id: str
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    items: List[Dict[str, Any]]
    total_amount: float
    status: str = "pending"
    payment_status: str = "pending"
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Template(BaseModel):
    model_config = ConfigDict(extra="ignore")
    template_id: str
    name: str
    category: str
    preview_url: str
    description: str
    is_premium: bool = False
    price: int = 0

# ============ REQUEST/RESPONSE MODELS ============

class SessionRequest(BaseModel):
    session_id: str

class SendOTPRequest(BaseModel):
    phone_number: str

class VerifyOTPRequest(BaseModel):
    phone_number: str
    code: str

class StoreCreateRequest(BaseModel):
    store_name: str
    category: str
    language: str = "en"
    gst_number: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

class ProductCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    category: Optional[str] = None
    images: List[str] = Field(default_factory=list)

class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class OrderCreateRequest(BaseModel):
    store_id: str
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    items: List[Dict[str, Any]]

# ============ AUTH HELPERS ============

async def get_current_user(request: Request, authorization: Optional[str] = Header(None)) -> User:
    session_token = request.cookies.get("session_token")
    if not session_token and authorization:
        if authorization.startswith("Bearer "):
            session_token = authorization.replace("Bearer ", "")
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session_doc = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    if isinstance(user_doc.get('created_at'), str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    return User(**user_doc)

# ============ AUTH ROUTES ============

@api_router.post("/auth/session")
async def create_session(request: SessionRequest, response: Response):
    try:
        headers = {"X-Session-ID": request.session_id}
        resp = requests.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers=headers,
            timeout=10
        )
        
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        data = resp.json()
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        
        existing_user = await db.users.find_one({"email": data["email"]}, {"_id": 0})
        if existing_user:
            user_id = existing_user["user_id"]
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "name": data["name"],
                    "picture": data.get("picture")
                }}
            )
        else:
            user_doc = {
                "user_id": user_id,
                "email": data["email"],
                "name": data["name"],
                "picture": data.get("picture"),
                "phone": None,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.users.insert_one(user_doc)
        
        session_token = data["session_token"]
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        session_doc = {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.user_sessions.insert_one(session_doc)
        
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            path="/",
            max_age=7*24*60*60
        )
        
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
        
        return User(**user)
    except Exception as e:
        logging.error(f"Session creation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/auth/me")
async def get_me(user: User = Depends(get_current_user)):
    return user

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response, user: User = Depends(get_current_user)):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    response.delete_cookie("session_token", path="/", samesite="none", secure=True)
    return {"message": "Logged out successfully"}

# ============ STORE ROUTES ============

@api_router.post("/stores", response_model=Store)
async def create_store(request: StoreCreateRequest, user: User = Depends(get_current_user)):
    existing_store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if existing_store:
        raise HTTPException(status_code=400, detail="You already have a store. Please manage your existing store.")
    
    subdomain = request.store_name.lower().replace(" ", "").replace("'", "")[:20]
    subdomain_exists = await db.stores.find_one({"subdomain": subdomain})
    if subdomain_exists:
        subdomain = f"{subdomain}{uuid.uuid4().hex[:4]}"
    
    # AI-powered description generation
    try:
        chat = LlmChat(
            api_key=os.getenv("EMERGENT_LLM_KEY"),
            session_id=f"store_creation_{user.user_id}",
            system_message="You are a helpful assistant that creates engaging store descriptions for Indian retailers."
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"Create a short, engaging store description (2-3 sentences) for '{request.store_name}', a {request.category} store in India. Make it appealing to customers and highlight trustworthiness."
        user_message = UserMessage(text=prompt)
        ai_description = await chat.send_message(user_message)
        description = ai_description.strip()
    except Exception as e:
        logging.error(f"AI description generation failed: {e}")
        description = f"Welcome to {request.store_name}, your trusted {request.category} store."
    
    store_doc = {
        "store_id": f"store_{uuid.uuid4().hex[:12]}",
        "user_id": user.user_id,
        "store_name": request.store_name,
        "subdomain": subdomain,
        "custom_domain": None,
        "template_id": "default",
        "logo_url": None,
        "description": description,
        "category": request.category,
        "language": request.language,
        "subscription_status": "trial",
        "subscription_tier": "basic",
        "gst_number": request.gst_number,
        "address": request.address,
        "phone": request.phone,
        "ondc_enabled": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.stores.insert_one(store_doc)
    store_doc['created_at'] = datetime.fromisoformat(store_doc['created_at'])
    return Store(**store_doc)

@api_router.get("/stores/my-store", response_model=Store)
async def get_my_store(user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="No store found. Please create a store first.")
    
    if isinstance(store.get('created_at'), str):
        store['created_at'] = datetime.fromisoformat(store['created_at'])
    
    return Store(**store)

@api_router.patch("/stores/{store_id}")
async def update_store(store_id: str, updates: Dict[str, Any], user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"store_id": store_id, "user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    allowed_updates = {"store_name", "description", "logo_url", "template_id", "gst_number", "address", "phone", "ondc_enabled", "custom_domain", "language"}
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_updates}
    
    if filtered_updates:
        await db.stores.update_one({"store_id": store_id}, {"$set": filtered_updates})
    
    updated_store = await db.stores.find_one({"store_id": store_id}, {"_id": 0})
    if isinstance(updated_store.get('created_at'), str):
        updated_store['created_at'] = datetime.fromisoformat(updated_store['created_at'])
    return Store(**updated_store)

# ============ PRODUCT ROUTES ============

@api_router.post("/products", response_model=Product)
async def create_product(request: ProductCreateRequest, user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    product_doc = {
        "product_id": f"prod_{uuid.uuid4().hex[:12]}",
        "store_id": store["store_id"],
        "name": request.name,
        "description": request.description,
        "price": request.price,
        "stock": request.stock,
        "images": request.images,
        "category": request.category,
        "variants": [],
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.products.insert_one(product_doc)
    product_doc['created_at'] = datetime.fromisoformat(product_doc['created_at'])
    return Product(**product_doc)

@api_router.get("/products", response_model=List[Product])
async def get_products(user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        return []
    
    products = await db.products.find({"store_id": store["store_id"]}, {"_id": 0}).to_list(1000)
    for prod in products:
        if isinstance(prod.get('created_at'), str):
            prod['created_at'] = datetime.fromisoformat(prod['created_at'])
    return [Product(**p) for p in products]

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str, user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    product = await db.products.find_one({"product_id": product_id, "store_id": store["store_id"]}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if isinstance(product.get('created_at'), str):
        product['created_at'] = datetime.fromisoformat(product['created_at'])
    return Product(**product)

@api_router.patch("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, request: ProductUpdateRequest, user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    product = await db.products.find_one({"product_id": product_id, "store_id": store["store_id"]}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    updates = {k: v for k, v in request.model_dump(exclude_unset=True).items()}
    if updates:
        await db.products.update_one({"product_id": product_id}, {"$set": updates})
    
    updated_product = await db.products.find_one({"product_id": product_id}, {"_id": 0})
    if isinstance(updated_product.get('created_at'), str):
        updated_product['created_at'] = datetime.fromisoformat(updated_product['created_at'])
    return Product(**updated_product)

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    result = await db.products.delete_one({"product_id": product_id, "store_id": store["store_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted successfully"}

# ============ ORDER ROUTES ============

@api_router.get("/orders", response_model=List[Order])
async def get_orders(user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        return []
    
    orders = await db.orders.find({"store_id": store["store_id"]}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for order in orders:
        if isinstance(order.get('created_at'), str):
            order['created_at'] = datetime.fromisoformat(order['created_at'])
    return [Order(**o) for o in orders]

@api_router.patch("/orders/{order_id}")
async def update_order_status(order_id: str, status: str, user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    result = await db.orders.update_one(
        {"order_id": order_id, "store_id": store["store_id"]},
        {"$set": {"status": status}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Order status updated"}

# ============ TEMPLATE ROUTES ============

@api_router.get("/templates", response_model=List[Template])
async def get_templates():
    templates = [
        Template(
            template_id="modern_minimal",
            name="Modern Minimal",
            category="general",
            preview_url="https://images.unsplash.com/photo-1441986300917-64674bd600d8",
            description="Clean and minimal design perfect for any store",
            is_premium=False,
            price=0
        ),
        Template(
            template_id="grocery_fresh",
            name="Grocery Fresh",
            category="grocery",
            preview_url="https://images.unsplash.com/photo-1542838132-92c53300491e",
            description="Vibrant template for grocery and food stores",
            is_premium=False,
            price=0
        ),
        Template(
            template_id="fashion_boutique",
            name="Fashion Boutique",
            category="clothing",
            preview_url="https://images.unsplash.com/photo-1441984904996-e0b6ba687e04",
            description="Elegant template for clothing and fashion",
            is_premium=True,
            price=999
        ),
        Template(
            template_id="electronics_pro",
            name="Electronics Pro",
            category="electronics",
            preview_url="https://images.unsplash.com/photo-1498049794561-7780e7231661",
            description="Tech-focused design for electronics stores",
            is_premium=True,
            price=1499
        )
    ]
    return templates

# ============ ANALYTICS ROUTES ============

@api_router.get("/analytics/overview")
async def get_analytics_overview(user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        return {"total_products": 0, "total_orders": 0, "total_revenue": 0, "pending_orders": 0}
    
    total_products = await db.products.count_documents({"store_id": store["store_id"]})
    total_orders = await db.orders.count_documents({"store_id": store["store_id"]})
    pending_orders = await db.orders.count_documents({"store_id": store["store_id"], "status": "pending"})
    
    orders = await db.orders.find({"store_id": store["store_id"], "payment_status": "paid"}, {"_id": 0}).to_list(10000)
    total_revenue = sum(order.get("total_amount", 0) for order in orders)
    
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders
    }

# Health check
@api_router.get("/")
async def root():
    return {"message": "ShopSwift India API", "status": "running"}

# ============ MOBILE APP GENERATION ROUTES ============

@api_router.post("/mobile-app/generate")
async def generate_mobile_app(user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    try:
        # Import Flutter generator
        import sys
        sys.path.append(str(Path(__file__).parent / "utils"))
        from flutter_generator import FlutterAppGenerator
        
        # Generate Flutter code
        generator = FlutterAppGenerator(store)
        files = generator.generate_all_files()
        
        # Create ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path, content in files.items():
                zip_file.writestr(file_path, content)
            
            # Add publishing guide
            publishing_guide = generate_publishing_guide(store)
            zip_file.writestr('PUBLISHING_GUIDE.md', publishing_guide)
            
            # Add placeholder directories
            zip_file.writestr('lib/screens/product_detail_screen.dart', generate_product_detail_screen())
            zip_file.writestr('lib/screens/cart_screen.dart', generate_cart_screen())
            zip_file.writestr('assets/images/.gitkeep', '')
        
        zip_buffer.seek(0)
        
        # Save generation record
        app_record = {
            "app_id": f"app_{uuid.uuid4().hex[:12]}",
            "store_id": store["store_id"],
            "package_name": generator.package_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0"
        }
        await db.mobile_apps.insert_one(app_record)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={store['store_name'].replace(' ', '_')}_app.zip"
            }
        )
    except Exception as e:
        logging.error(f"Mobile app generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate app: {str(e)}")

@api_router.get("/mobile-app/status")
async def get_mobile_app_status(user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    app = await db.mobile_apps.find_one({"store_id": store["store_id"]}, {"_id": 0})
    
    return {
        "has_app": app is not None,
        "app_data": app if app else None,
        "package_name": f"com.shopswift.{store['subdomain'].lower().replace('-', '').replace('_', '')}",
        "app_name": store["store_name"]
    }

def generate_publishing_guide(store: Dict) -> str:
    package_name = f"com.shopswift.{store['subdomain'].lower().replace('-', '').replace('_', '')}"
    
    return f\"\"\"# Publishing Guide - {store['store_name']} Mobile App

## Centralized Publishing by ShopSwift India

Your app will be published under the **ShopSwift India** developer account on both platforms.

---

## App Details

- **App Name:** {store['store_name']}
- **Package Name:** {package_name}
- **Store ID:** {store['store_id']}
- **Version:** 1.0.0

---

## Build Instructions

### Prerequisites
1. Install Flutter SDK (3.0.0+): https://flutter.dev/docs/get-started/install
2. Install Android Studio (for Android builds)
3. Install Xcode (for iOS builds - Mac only)

### Build Android APK

```bash
# Navigate to project directory
cd {store['store_name'].replace(' ', '_')}_app

# Get dependencies
flutter pub get

# Build release APK
flutter build apk --release

# Output location
build/app/outputs/flutter-apk/app-release.apk
```

### Build iOS IPA

```bash
# Build iOS app
flutter build ios --release

# Archive in Xcode
open ios/Runner.xcworkspace

# In Xcode:
# 1. Select "Any iOS Device" as target
# 2. Product → Archive
# 3. Distribute App → App Store Connect
```

---

## Centralized Publishing Process

### Google Play Store (Android)

**Developer Account:** ShopSwift India (Centralized)
- **One-time fee:** $25 (already paid by platform)
- **Your app published as:** "{store['store_name']} by ShopSwift India"

**Steps to Submit:**
1. Send us the APK file: `app-release.apk`
2. Provide 2 screenshots (1080x1920 or 1080x2400)
3. Write a short description (80 words)
4. Write a full description (4000 characters max)
5. Choose category (e.g., Shopping, Business)

**We handle:**
- Store listing creation
- App signing and security
- Publishing and updates
- Play Store optimization

**Your listing:** https://play.google.com/store/apps/details?id={package_name}

### Apple App Store (iOS)

**Developer Account:** ShopSwift India (Centralized)
- **Annual fee:** $99/year (paid by platform)
- **Your app published as:** "{store['store_name']} by ShopSwift India"

**Steps to Submit:**
1. Send us the IPA file (from Xcode archive)
2. Provide 3 screenshots per device (iPhone 6.5", iPad 12.9")
3. App description (4000 characters)
4. Keywords (100 characters)
5. Privacy policy URL (required)

**We handle:**
- App Store Connect setup
- Provisioning profiles
- App review submission
- Publishing and updates

**Your listing:** https://apps.apple.com/app/{store['store_name'].lower().replace(' ', '-')}/{package_name}

---

## Assets Required for Publishing

### Screenshots (Important!)

**Android (Google Play):**
- Minimum 2 screenshots
- Size: 1080x1920 (portrait) or 1080x2400
- Format: PNG or JPEG
- Show: Home screen, Products page, Product detail

**iOS (App Store):**
- 3 screenshots per device type
- iPhone 6.5" (1284x2778)
- iPad Pro 12.9" (2048x2732)
- Format: PNG or JPEG

**Tips:**
- Use actual app running on device
- Show key features
- Add captions/text overlay
- Keep UI clean

### App Icons

**Already included in the Flutter project:**
- Android: `android/app/src/main/res/mipmap-*/ic_launcher.png`
- iOS: `ios/Runner/Assets.xcassets/AppIcon.appiconset/`

**Size:** 512x512 PNG (transparent or white background)

### Feature Graphic (Google Play only)

- Size: 1024x500
- Format: PNG or JPEG
- Showcase your store/products
- Include store name

### App Description Template

**Short Description (80 chars):**
"{store['store_name']} - Shop quality products online with easy ordering"

**Full Description:**
Welcome to {store['store_name']}!

Shop our complete range of products from the comfort of your home. Browse categories, add to cart, and place orders instantly.

Features:
✓ Browse all products
✓ View detailed product information
✓ Add products to cart
✓ Easy checkout process
✓ Order tracking
✓ Contact store directly
✓ Secure and fast

Download now and start shopping!

---

## Submission Checklist

### Before Sending to ShopSwift

- [ ] APK/IPA file built and tested
- [ ] 2+ app screenshots (high quality)
- [ ] App icon (512x512)
- [ ] Short description written
- [ ] Full description written
- [ ] Feature graphic created (Android)
- [ ] Privacy policy URL (if collecting data)
- [ ] Category selected
- [ ] Age rating: Everyone (default)

### Send to ShopSwift Team

**Email:** apps@shopswift.in

**Subject:** "App Submission - {store['store_name']}"

**Attach:**
1. APK file (Android)
2. IPA file (iOS) - if applicable
3. Screenshots (ZIP folder)
4. App icon
5. Feature graphic
6. Description document

**Include in email:**
- Store ID: {store['store_id']}
- Contact phone: {store.get('phone', 'N/A')}
- Preferred publication date
- Any special instructions

---

## Timeline

**Google Play:**
- Submission to review: 1-2 business days
- Review time: 1-7 days
- Total: ~3-10 days

**App Store:**
- Submission to review: 1-2 business days
- Review time: 1-3 days
- Total: ~2-5 days

---

## Updates

To update your app:
1. Increment version in `pubspec.yaml` (e.g., 1.0.0 → 1.0.1)
2. Rebuild APK/IPA
3. Send to ShopSwift team
4. We publish update (2-5 days)

---

## Pricing

**Publishing Service:**
- First app: FREE (included in subscription)
- Updates: FREE (unlimited)
- Play Store fee: Covered by ShopSwift
- App Store fee: Covered by ShopSwift

**Your responsibility:**
- Maintaining store data/products
- Providing content for listing
- Customer support for app users

---

## Support

**Technical Issues:**
- Email: support@shopswift.in
- Phone: +91 (available in dashboard)

**Publishing Questions:**
- Email: apps@shopswift.in
- Response time: 24-48 hours

---

## Important Notes

1. **Branding:** Apps published as "by ShopSwift India" with your store name
2. **Updates:** Send new APK/IPA for updates (we handle publishing)
3. **Analytics:** Access via Google Play Console / App Store Connect (shared access)
4. **Reviews:** Monitor and respond via our centralized dashboard
5. **Removal:** Request anytime (24-hour processing)

---

## Next Steps

1. ✅ Download this ZIP file
2. ✅ Extract and test the Flutter code
3. ✅ Build APK using instructions above
4. ✅ Prepare screenshots and assets
5. ✅ Email everything to apps@shopswift.in

**Congratulations on taking your store mobile!** 📱

---

Generated by ShopSwift India
https://shopswift.in
\"\"\"\n\ndef generate_product_detail_screen() -> str:\n    return \"\"\"import 'package:flutter/material.dart';\nimport 'package:cached_network_image/cached_network_image.dart';\nimport '../models/product.dart';\n\nclass ProductDetailScreen extends StatelessWidget {\n  final Product product;\n\n  const ProductDetailScreen({required this.product});\n\n  @override\n  Widget build(BuildContext context) {\n    return Scaffold(\n      appBar: AppBar(\n        title: Text('Product Details'),\n      ),\n      body: SingleChildScrollView(\n        child: Column(\n          crossAxisAlignment: CrossAxisAlignment.start,\n          children: [\n            // Product Image\n            if (product.images.isNotEmpty)\n              Container(\n                height: 300,\n                width: double.infinity,\n                color: Color(0xFFF1F5F9),\n                child: CachedNetworkImage(\n                  imageUrl: product.images.first,\n                  fit: BoxFit.cover,\n                  placeholder: (context, url) => Center(\n                    child: CircularProgressIndicator(),\n                  ),\n                  errorWidget: (context, url, error) => Icon(\n                    Icons.image_not_supported,\n                    size: 64,\n                    color: Colors.grey,\n                  ),\n                ),\n              ),\n\n            Padding(\n              padding: EdgeInsets.all(16),\n              child: Column(\n                crossAxisAlignment: CrossAxisAlignment.start,\n                children: [\n                  Text(\n                    product.name,\n                    style: TextStyle(\n                      fontSize: 24,\n                      fontWeight: FontWeight.bold,\n                      color: Color(0xFF0F172A),\n                    ),\n                  ),\n                  SizedBox(height: 8),\n                  Text(\n                    '₹${product.price.toStringAsFixed(2)}',\n                    style: TextStyle(\n                      fontSize: 32,\n                      fontWeight: FontWeight.bold,\n                      color: Color(0xFFF97316),\n                    ),\n                  ),\n                  SizedBox(height: 16),\n                  Row(\n                    children: [\n                      Icon(\n                        product.stock > 0 ? Icons.check_circle : Icons.cancel,\n                        color: product.stock > 0 ? Color(0xFF10B981) : Colors.red,\n                      ),\n                      SizedBox(width: 8),\n                      Text(\n                        product.stock > 0\n                            ? 'In Stock (${product.stock} available)'\n                            : 'Out of Stock',\n                        style: TextStyle(\n                          fontSize: 16,\n                          fontWeight: FontWeight.w500,\n                          color: product.stock > 0 ? Color(0xFF10B981) : Colors.red,\n                        ),\n                      ),\n                    ],\n                  ),\n                  if (product.description != null) ..[\n                    SizedBox(height: 24),\n                    Text(\n                      'Description',\n                      style: TextStyle(\n                        fontSize: 18,\n                        fontWeight: FontWeight.bold,\n                        color: Color(0xFF0F172A),\n                      ),\n                    ),\n                    SizedBox(height: 8),\n                    Text(\n                      product.description!,\n                      style: TextStyle(\n                        fontSize: 16,\n                        color: Color(0xFF64748B),\n                        height: 1.5,\n                      ),\n                    ),\n                  ],\n                ],\n              ),\n            ),\n          ],\n        ),\n      ),\n      bottomNavigationBar: Container(\n        padding: EdgeInsets.all(16),\n        decoration: BoxDecoration(\n          color: Colors.white,\n          boxShadow: [\n            BoxShadow(\n              color: Colors.black.withOpacity(0.05),\n              blurRadius: 10,\n              offset: Offset(0, -2),\n            ),\n          ],\n        ),\n        child: ElevatedButton(\n          onPressed: product.stock > 0 ? () {\n            // Add to cart functionality\n            ScaffoldMessenger.of(context).showSnackBar(\n              SnackBar(\n                content: Text('Added to cart!'),\n                backgroundColor: Color(0xFF10B981),\n              ),\n            );\n          } : null,\n          style: ElevatedButton.styleFrom(\n            backgroundColor: Color(0xFFF97316),\n            foregroundColor: Colors.white,\n            padding: EdgeInsets.symmetric(vertical: 16),\n            shape: RoundedRectangleBorder(\n              borderRadius: BorderRadius.circular(12),\n            ),\n            disabledBackgroundColor: Colors.grey,\n          ),\n          child: Text(\n            product.stock > 0 ? 'Add to Cart' : 'Out of Stock',\n            style: TextStyle(\n              fontSize: 18,\n              fontWeight: FontWeight.bold,\n            ),\n          ),\n        ),\n      ),\n    );\n  }\n}\n\"\"\"\n\ndef generate_cart_screen() -> str:\n    return \"\"\"import 'package:flutter/material.dart';\n\nclass CartScreen extends StatelessWidget {\n  @override\n  Widget build(BuildContext context) {\n    return Scaffold(\n      appBar: AppBar(\n        title: Text('Shopping Cart'),\n      ),\n      body: Center(\n        child: Column(\n          mainAxisAlignment: MainAxisAlignment.center,\n          children: [\n            Icon(\n              Icons.shopping_cart_outlined,\n              size: 80,\n              color: Colors.grey,\n            ),\n            SizedBox(height: 16),\n            Text(\n              'Your cart is empty',\n              style: TextStyle(\n                fontSize: 20,\n                fontWeight: FontWeight.bold,\n                color: Color(0xFF0F172A),\n              ),\n            ),\n            SizedBox(height: 8),\n            Text(\n              'Add products to get started',\n              style: TextStyle(\n                fontSize: 16,\n                color: Color(0xFF64748B),\n              ),\n            ),\n            SizedBox(height: 24),\n            ElevatedButton(\n              onPressed: () {\n                Navigator.pop(context);\n              },\n              style: ElevatedButton.styleFrom(\n                backgroundColor: Color(0xFFF97316),\n                foregroundColor: Colors.white,\n                padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),\n                shape: RoundedRectangleBorder(\n                  borderRadius: BorderRadius.circular(12),\n                ),\n              ),\n              child: Text(\n                'Continue Shopping',\n                style: TextStyle(\n                  fontSize: 16,\n                  fontWeight: FontWeight.bold,\n                ),\n              ),\n            ),\n          ],\n        ),\n      ),\n    );\n  }\n}\n\"\"\"

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
