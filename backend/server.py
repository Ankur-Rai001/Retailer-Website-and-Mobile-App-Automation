from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
import os
import logging

from database import db, client
from routers import auth, store, products, orders, templates, analytics, mobile_app, ondc, chat, public, admin

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="ShopSwift India API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.io ASGI app for real-time chat
app.mount('/socket.io', chat.sio_app)

# API router with /api prefix
api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(store.router)
api_router.include_router(products.router)
api_router.include_router(orders.router)
api_router.include_router(templates.router)
api_router.include_router(analytics.router)
api_router.include_router(mobile_app.router)
api_router.include_router(ondc.router)
api_router.include_router(chat.router)
api_router.include_router(public.router)
api_router.include_router(admin.router)


@api_router.get("/")
async def root():
    return {"message": "ShopSwift India API", "status": "running"}


app.include_router(api_router)


@app.on_event("startup")
async def startup():
    from routers.auth import seed_demo_accounts
    await seed_demo_accounts()


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
