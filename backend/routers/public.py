from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from database import db
from models import Product

router = APIRouter(tags=["public"])


@router.get("/store-public/{store_id}")
async def get_store_public(store_id: str):
    store = await db.stores.find_one({"store_id": store_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    return {
        "store_id": store["store_id"],
        "store_name": store["store_name"],
        "description": store.get("description"),
        "phone": store.get("phone"),
        "address": store.get("address"),
        "category": store["category"]
    }


@router.get("/products-public/{store_id}")
async def get_products_public(store_id: str):
    store = await db.stores.find_one({"store_id": store_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    products = await db.products.find(
        {"store_id": store_id, "is_active": True}, {"_id": 0}
    ).to_list(1000)

    for prod in products:
        if isinstance(prod.get('created_at'), str):
            prod['created_at'] = datetime.fromisoformat(prod['created_at'])

    return [Product(**p).model_dump() for p in products]
