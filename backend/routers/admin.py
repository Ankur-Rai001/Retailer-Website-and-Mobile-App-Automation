from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timezone
import logging

from database import db
from models import User, SubscriptionUpdateRequest
from deps import get_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/metrics")
async def get_platform_metrics(admin: User = Depends(get_admin_user)):
    total_retailers = await db.users.count_documents({"role": {"$ne": "admin"}})
    total_stores = await db.stores.count_documents({})
    total_products = await db.products.count_documents({})
    total_orders = await db.orders.count_documents({})

    orders = await db.orders.find({"payment_status": "paid"}, {"_id": 0, "total_amount": 1}).to_list(10000)
    total_revenue = sum(o.get("total_amount", 0) for o in orders)

    active_subs = await db.stores.count_documents({"subscription_status": {"$in": ["active", "trial"]}})
    expired_subs = await db.stores.count_documents({"subscription_status": "expired"})
    cancelled_subs = await db.stores.count_documents({"subscription_status": "cancelled"})

    # Stores by tier
    basic_count = await db.stores.count_documents({"subscription_tier": "basic"})
    pro_count = await db.stores.count_documents({"subscription_tier": "pro"})
    premium_count = await db.stores.count_documents({"subscription_tier": "premium"})

    # ONDC stats
    ondc_enabled = await db.stores.count_documents({"ondc_enabled": True})

    # Chat stats
    total_messages = await db.chat_messages.count_documents({})

    return {
        "total_retailers": total_retailers,
        "total_stores": total_stores,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "subscriptions": {
            "active": active_subs,
            "expired": expired_subs,
            "cancelled": cancelled_subs,
        },
        "tiers": {
            "basic": basic_count,
            "pro": pro_count,
            "premium": premium_count,
        },
        "ondc_enabled_stores": ondc_enabled,
        "total_chat_messages": total_messages,
    }


@router.get("/retailers")
async def list_retailers(
    search: Optional[str] = None,
    status: Optional[str] = None,
    tier: Optional[str] = None,
    admin: User = Depends(get_admin_user),
):
    user_filter = {"role": {"$ne": "admin"}}
    if search:
        user_filter["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
        ]

    users = await db.users.find(user_filter, {"_id": 0}).to_list(500)

    results = []
    for u in users:
        store_filter = {"user_id": u["user_id"]}
        store = await db.stores.find_one(store_filter, {"_id": 0})

        if status and store and store.get("subscription_status") != status:
            continue
        if tier and store and store.get("subscription_tier") != tier:
            continue
        if (status or tier) and not store:
            continue

        product_count = 0
        order_count = 0
        if store:
            product_count = await db.products.count_documents({"store_id": store["store_id"]})
            order_count = await db.orders.count_documents({"store_id": store["store_id"]})

        results.append({
            "user_id": u["user_id"],
            "name": u.get("name", ""),
            "email": u.get("email", ""),
            "phone": u.get("phone"),
            "created_at": u.get("created_at"),
            "has_store": store is not None,
            "store_name": store["store_name"] if store else None,
            "store_id": store["store_id"] if store else None,
            "subdomain": store["subdomain"] if store else None,
            "subscription_status": store["subscription_status"] if store else None,
            "subscription_tier": store["subscription_tier"] if store else None,
            "category": store["category"] if store else None,
            "product_count": product_count,
            "order_count": order_count,
        })

    return results


@router.get("/retailers/{user_id}")
async def get_retailer_detail(user_id: str, admin: User = Depends(get_admin_user)):
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Retailer not found")

    store = await db.stores.find_one({"user_id": user_id}, {"_id": 0})
    products = []
    orders = []
    revenue = 0
    kyc = None

    if store:
        products = await db.products.find({"store_id": store["store_id"]}, {"_id": 0}).to_list(100)
        orders = await db.orders.find({"store_id": store["store_id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
        paid = await db.orders.find({"store_id": store["store_id"], "payment_status": "paid"}, {"_id": 0}).to_list(10000)
        revenue = sum(o.get("total_amount", 0) for o in paid)
        kyc = await db.ondc_kyc.find_one({"store_id": store["store_id"]}, {"_id": 0})

    return {
        "user": user,
        "store": store,
        "products": products,
        "recent_orders": orders[:20],
        "total_revenue": revenue,
        "product_count": len(products),
        "order_count": len(orders),
        "kyc": kyc,
    }


@router.patch("/retailers/{user_id}/subscription")
async def update_subscription(
    user_id: str,
    body: SubscriptionUpdateRequest,
    admin: User = Depends(get_admin_user),
):
    store = await db.stores.find_one({"user_id": user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found for this retailer")

    await db.stores.update_one(
        {"store_id": store["store_id"]},
        {"$set": {
            "subscription_status": body.subscription_status,
            "subscription_tier": body.subscription_tier,
        }}
    )

    updated = await db.stores.find_one({"store_id": store["store_id"]}, {"_id": 0})
    return {
        "message": "Subscription updated",
        "store_id": updated["store_id"],
        "subscription_status": updated["subscription_status"],
        "subscription_tier": updated["subscription_tier"],
    }
