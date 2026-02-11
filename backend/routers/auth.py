from fastapi import APIRouter, HTTPException, Response, Depends, Request
from datetime import datetime, timezone, timedelta
import uuid
import logging
import requests as http_requests

from database import db
from models import User, SessionRequest
from deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

DEMO_ACCOUNTS = {
    "demo_session_retailer_12345678901234567890": {
        "user_id": "user_demo_retailer",
        "email": "demo.retailer@shopswift.in",
        "name": "Demo Retailer",
        "role": "retailer"
    },
    "demo_session_admin_12345678901234567890": {
        "user_id": "user_demo_admin",
        "email": "demo.admin@shopswift.in",
        "name": "Demo Admin",
        "role": "admin"
    }
}


async def seed_demo_accounts():
    """Seed demo users, sessions, and a demo store on startup."""
    for token, account in DEMO_ACCOUNTS.items():
        existing = await db.users.find_one({"user_id": account["user_id"]}, {"_id": 0})
        if not existing:
            await db.users.insert_one({
                **account,
                "phone": None,
                "picture": None,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        await db.user_sessions.update_one(
            {"session_token": token},
            {"$set": {
                "user_id": account["user_id"],
                "session_token": token,
                "expires_at": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )

    # Seed demo store for the retailer
    demo_store = await db.stores.find_one({"user_id": "user_demo_retailer"}, {"_id": 0})
    if not demo_store:
        await db.stores.insert_one({
            "store_id": "store_demo_001",
            "user_id": "user_demo_retailer",
            "store_name": "Demo General Store",
            "subdomain": "demogeneralstore",
            "custom_domain": None,
            "template_id": "modern_minimal",
            "logo_url": None,
            "description": "Welcome to Demo General Store! Your one-stop shop for everyday essentials in India.",
            "category": "general",
            "language": "en",
            "subscription_status": "trial",
            "subscription_tier": "basic",
            "gst_number": None,
            "address": "MG Road, Bengaluru, Karnataka",
            "phone": "+91-9876543210",
            "ondc_enabled": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        })

    # Seed extra demo retailers for admin dashboard
    sample_retailers = [
        {"user_id": "user_seed_r1", "email": "priya.fashions@shopswift.in", "name": "Priya Fashions", "role": "retailer", "phone": "+91-9900112233",
         "store": {"store_id": "store_seed_001", "store_name": "Priya Fashions", "subdomain": "priyafashions", "category": "clothing", "subscription_status": "active", "subscription_tier": "pro", "ondc_enabled": True}},
        {"user_id": "user_seed_r2", "email": "ravi.electronics@shopswift.in", "name": "Ravi Electronics Hub", "role": "retailer", "phone": "+91-9988776655",
         "store": {"store_id": "store_seed_002", "store_name": "Ravi Electronics Hub", "subdomain": "ravielectronics", "category": "electronics", "subscription_status": "active", "subscription_tier": "premium", "ondc_enabled": True}},
        {"user_id": "user_seed_r3", "email": "anita.grocery@shopswift.in", "name": "Anita Fresh Mart", "role": "retailer", "phone": "+91-9871234567",
         "store": {"store_id": "store_seed_003", "store_name": "Anita Fresh Mart", "subdomain": "anitafreshmart", "category": "grocery", "subscription_status": "trial", "subscription_tier": "basic", "ondc_enabled": False}},
        {"user_id": "user_seed_r4", "email": "suresh.kirana@shopswift.in", "name": "Suresh Kirana Store", "role": "retailer", "phone": "+91-9123456789",
         "store": {"store_id": "store_seed_004", "store_name": "Suresh Kirana Store", "subdomain": "sureshkirana", "category": "grocery", "subscription_status": "expired", "subscription_tier": "basic", "ondc_enabled": False}},
        {"user_id": "user_seed_r5", "email": "meena.jewels@shopswift.in", "name": "Meena Jewellers", "role": "retailer", "phone": "+91-9876001234",
         "store": {"store_id": "store_seed_005", "store_name": "Meena Jewellers", "subdomain": "meenajewels", "category": "jewelry", "subscription_status": "active", "subscription_tier": "premium", "ondc_enabled": True}},
    ]

    for r in sample_retailers:
        if not await db.users.find_one({"user_id": r["user_id"]}):
            await db.users.insert_one({
                "user_id": r["user_id"], "email": r["email"], "name": r["name"],
                "role": r["role"], "phone": r.get("phone"), "picture": None,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        s = r["store"]
        if not await db.stores.find_one({"store_id": s["store_id"]}):
            await db.stores.insert_one({
                "store_id": s["store_id"], "user_id": r["user_id"],
                "store_name": s["store_name"], "subdomain": s["subdomain"],
                "custom_domain": None, "template_id": "modern_minimal",
                "logo_url": None, "description": f"Welcome to {s['store_name']}!",
                "category": s["category"], "language": "en",
                "subscription_status": s["subscription_status"],
                "subscription_tier": s["subscription_tier"],
                "gst_number": None, "address": "India",
                "phone": r.get("phone"), "ondc_enabled": s["ondc_enabled"],
                "created_at": datetime.now(timezone.utc).isoformat()
            })


@router.post("/session")
async def create_session(request: SessionRequest, response: Response):
    try:
        headers = {"X-Session-ID": request.session_id}
        resp = http_requests.get(
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
                {"$set": {"name": data["name"], "picture": data.get("picture")}}
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
            max_age=7 * 24 * 60 * 60
        )

        user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])

        return User(**user)
    except Exception as e:
        logging.error(f"Session creation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return user


@router.post("/logout")
async def logout(request: Request, response: Response, user: User = Depends(get_current_user)):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    response.delete_cookie("session_token", path="/", samesite="none", secure=True)
    return {"message": "Logged out successfully"}


@router.post("/demo-login")
async def demo_login(response: Response, role: str = "retailer"):
    """Quick demo login - creates session cookie for demo retailer or admin."""
    token_map = {
        "retailer": "demo_session_retailer_12345678901234567890",
        "admin": "demo_session_admin_12345678901234567890"
    }
    token = token_map.get(role, token_map["retailer"])
    account = DEMO_ACCOUNTS[token]

    await seed_demo_accounts()

    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=365 * 24 * 60 * 60
    )

    user = await db.users.find_one({"user_id": account["user_id"]}, {"_id": 0})
    if isinstance(user.get('created_at'), str):
        user['created_at'] = datetime.fromisoformat(user['created_at'])

    return User(**user)
