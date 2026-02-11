from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
from pathlib import Path
import uuid
import logging
import os

from database import db
from models import User, Product, ONDCKYCRequest
from deps import get_current_user

router = APIRouter(prefix="/ondc", tags=["ondc"])


@router.post("/kyc")
async def submit_ondc_kyc(request: ONDCKYCRequest, user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    kyc_doc = {
        "store_id": store["store_id"],
        "gstin": request.gstin,
        "pan": request.pan,
        "bank_account": request.bank_account,
        "bank_ifsc": request.bank_ifsc,
        "bank_name": request.bank_name,
        "account_holder_name": request.account_holder_name,
        "status": "pending",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "verified_at": None
    }

    await db.ondc_kyc.update_one(
        {"store_id": store["store_id"]},
        {"$set": kyc_doc},
        upsert=True
    )

    return {"message": "KYC submitted successfully", "status": "pending"}


@router.get("/kyc-status")
async def get_ondc_kyc_status(user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    kyc = await db.ondc_kyc.find_one({"store_id": store["store_id"]}, {"_id": 0})

    return {
        "has_kyc": kyc is not None,
        "kyc_data": kyc if kyc else None,
        "ondc_enabled": store.get("ondc_enabled", False)
    }


@router.post("/sync-catalog")
async def sync_catalog_to_ondc(user: User = Depends(get_current_user)):
    try:
        store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")

        if not store.get("ondc_enabled", False):
            raise HTTPException(status_code=400, detail="ONDC not enabled for this store")

        kyc = await db.ondc_kyc.find_one({"store_id": store["store_id"]}, {"_id": 0})
        if not kyc or kyc.get("status") != "verified":
            raise HTTPException(status_code=400, detail="KYC not verified. Please complete KYC first.")

        products = await db.products.find(
            {"store_id": store["store_id"], "is_active": True}, {"_id": 0}
        ).to_list(1000)

        from utils.ondc_integration import ONDCIntegration

        ondc = ONDCIntegration(
            subscriber_id=f"shopswift.{store['subdomain']}.in",
            subscriber_url=f"https://{store['subdomain']}.shopswift.in/ondc/webhooks",
            signing_key=os.getenv("ONDC_SIGNING_KEY", "dummy_key_for_staging")
        )

        result = ondc.sync_catalog_to_ondc(store, products)

        if result.get("success"):
            sync_record = {
                "store_id": store["store_id"],
                "synced_at": datetime.now(timezone.utc).isoformat(),
                "product_count": len(products),
                "status": "synced",
                "ondc_payload": result.get("payload")
            }
            await db.ondc_syncs.insert_one(sync_record)

            return {
                "message": "Catalog synced successfully",
                "product_count": len(products),
                "synced_at": sync_record["synced_at"]
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Sync failed"))

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"ONDC sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync-status")
async def get_ondc_sync_status(user: User = Depends(get_current_user)):
    store = await db.stores.find_one({"user_id": user.user_id}, {"_id": 0})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    last_sync = await db.ondc_syncs.find_one(
        {"store_id": store["store_id"]}, {"_id": 0}, sort=[("synced_at", -1)]
    )

    return {
        "has_synced": last_sync is not None,
        "last_sync": last_sync,
        "ondc_enabled": store.get("ondc_enabled", False)
    }


# ---- ONDC Beckn Protocol Webhooks ----

@router.post("/webhooks/search")
async def ondc_search_webhook(request: Request):
    try:
        payload = await request.json()
        from utils.ondc_integration import ONDCIntegration

        ondc = ONDCIntegration("", "", "")
        search_params = ondc.handle_search_request(payload)

        search_filter = {}
        if search_params.get("search_string"):
            search_filter["name"] = {"$regex": search_params["search_string"], "$options": "i"}
        if search_params.get("category"):
            search_filter["category"] = search_params["category"]

        stores = await db.stores.find({"ondc_enabled": True}, {"_id": 0}).to_list(100)

        all_providers = []
        for store in stores:
            products = await db.products.find(
                {"store_id": store["store_id"], "is_active": True, **search_filter}, {"_id": 0}
            ).to_list(100)

            if products:
                ondc_instance = ONDCIntegration(
                    f"shopswift.{store['subdomain']}.in",
                    f"https://{store['subdomain']}.shopswift.in/ondc/webhooks",
                    ""
                )
                provider = ondc_instance.create_catalog_payload(store, products)
                all_providers.append(provider)

        context = payload.get("context", {})
        context["action"] = "on_search"

        return {"context": context, "message": {"catalog": {"bpp/providers": all_providers}}}
    except Exception as e:
        logging.error(f"ONDC search webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/select")
async def ondc_select_webhook(request: Request):
    try:
        payload = await request.json()
        order = payload.get("message", {}).get("order", {})
        provider_id = order.get("provider", {}).get("id")
        store = await db.stores.find_one({"store_id": provider_id}, {"_id": 0})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")

        from utils.ondc_integration import ONDCIntegration
        ondc = ONDCIntegration(
            f"shopswift.{store['subdomain']}.in",
            f"https://{store['subdomain']}.shopswift.in/ondc/webhooks", ""
        )
        return ondc.create_select_response(order.get("items", []), store)
    except Exception as e:
        logging.error(f"ONDC select webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/init")
async def ondc_init_webhook(request: Request):
    try:
        payload = await request.json()
        order = payload.get("message", {}).get("order", {})
        provider_id = order.get("provider", {}).get("id")
        store = await db.stores.find_one({"store_id": provider_id}, {"_id": 0})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")

        from utils.ondc_integration import ONDCIntegration
        ondc = ONDCIntegration(
            f"shopswift.{store['subdomain']}.in",
            f"https://{store['subdomain']}.shopswift.in/ondc/webhooks", ""
        )
        return ondc.create_init_response(order, order.get("billing", {}))
    except Exception as e:
        logging.error(f"ONDC init webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/confirm")
async def ondc_confirm_webhook(request: Request):
    try:
        payload = await request.json()
        order = payload.get("message", {}).get("order", {})
        provider_id = order.get("provider", {}).get("id")
        store = await db.stores.find_one({"store_id": provider_id}, {"_id": 0})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")

        order_id = f"ondc_{uuid.uuid4().hex[:12]}"
        order_doc = {
            "order_id": order_id,
            "store_id": store["store_id"],
            "source": "ondc",
            "ondc_order_id": order.get("id"),
            "customer_name": order.get("billing", {}).get("name", "ONDC Customer"),
            "customer_phone": order.get("billing", {}).get("phone", ""),
            "customer_email": order.get("billing", {}).get("email", ""),
            "items": order.get("items", []),
            "total_amount": float(order.get("quote", {}).get("price", {}).get("value", 0)),
            "status": "pending",
            "payment_status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.orders.insert_one(order_doc)

        from utils.ondc_integration import ONDCIntegration
        ondc = ONDCIntegration(
            f"shopswift.{store['subdomain']}.in",
            f"https://{store['subdomain']}.shopswift.in/ondc/webhooks", ""
        )
        return ondc.create_confirm_response(order_id, order)
    except Exception as e:
        logging.error(f"ONDC confirm webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
