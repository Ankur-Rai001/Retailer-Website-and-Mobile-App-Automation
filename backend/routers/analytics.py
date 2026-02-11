from fastapi import APIRouter, Depends

from database import db
from models import User
from deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
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
