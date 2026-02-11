from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


# ============ DB MODELS ============

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: EmailStr
    name: str
    phone: Optional[str] = None
    picture: Optional[str] = None
    role: str = "retailer"
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


class ChatMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    store_id: str
    customer_id: str
    customer_name: str
    sender: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read: bool = False


# ============ REQUEST MODELS ============

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


class ONDCKYCRequest(BaseModel):
    gstin: str
    pan: str
    bank_account: str
    bank_ifsc: str
    bank_name: str
    account_holder_name: str


class ChatSendRequest(BaseModel):
    store_id: str
    customer_id: str
    customer_name: str = "Customer"
    message: str
    sender: str = "customer"


class SubscriptionUpdateRequest(BaseModel):
    subscription_status: str
    subscription_tier: str
