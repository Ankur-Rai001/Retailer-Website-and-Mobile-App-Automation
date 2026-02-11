from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime, timezone

from database import db
from models import User, Order
from deps import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=List[Order])
async def get_orders(user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        return []

    orders = await db.orders.find({"store_id": store["store_id"]}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for order in orders:
        if isinstance(order.get('created_at'), str):
            order['created_at'] = datetime.fromisoformat(order['created_at'])
    return [Order(**o) for o in orders]


@router.patch("/{order_id}")
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
