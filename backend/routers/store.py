from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import os

from emergentintegrations.llm.chat import LlmChat, UserMessage

from database import db
from models import User, Store, StoreCreateRequest
from deps import get_current_user

router = APIRouter(prefix="/stores", tags=["stores"])


@router.post("", response_model=Store)
async def create_store(request: StoreCreateRequest, user: User = Depends(get_current_user)):
    existing_store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if existing_store:
        raise HTTPException(status_code=400, detail="You already have a store. Please manage your existing store.")

    subdomain = request.store_name.lower().replace(" ", "").replace("'", "")[:20]
    subdomain_exists = await db.stores.find_one({"subdomain": subdomain})
    if subdomain_exists:
        subdomain = f"{subdomain}{uuid.uuid4().hex[:4]}"

    try:
        chat = LlmChat(
            api_key=os.getenv("EMERGENT_LLM_KEY"),
            session_id=f"store_creation_{user.user_id}",
            system_message="You are a helpful assistant that creates engaging store descriptions for Indian retailers."
        ).with_model("openai", "gpt-5.2")

        prompt = f"Create a short, engaging store description (2-3 sentences) for '{request.store_name}', a {request.category} store in India. Make it appealing to customers and highlight trustworthiness."
        ai_description = await chat.send_message(UserMessage(text=prompt))
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


@router.get("/my-store", response_model=Store)
async def get_my_store(user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="No store found. Please create a store first.")

    if isinstance(store.get('created_at'), str):
        store['created_at'] = datetime.fromisoformat(store['created_at'])

    return Store(**store)


@router.patch("/{store_id}")
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
