from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime, timezone
import uuid

from database import db
from models import User, Product, ProductCreateRequest, ProductUpdateRequest
from deps import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=Product)
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


@router.get("", response_model=List[Product])
async def get_products(user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        return []

    products = await db.products.find({"store_id": store["store_id"]}, {"_id": 0}).to_list(1000)
    for prod in products:
        if isinstance(prod.get('created_at'), str):
            prod['created_at'] = datetime.fromisoformat(prod['created_at'])
    return [Product(**p) for p in products]


@router.get("/{product_id}", response_model=Product)
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


@router.patch("/{product_id}", response_model=Product)
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


@router.delete("/{product_id}")
async def delete_product(product_id: str, user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    result = await db.products.delete_one({"product_id": product_id, "store_id": store["store_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}
