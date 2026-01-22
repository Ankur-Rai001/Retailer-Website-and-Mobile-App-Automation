from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, Header
from fastapi.responses import JSONResponse
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
