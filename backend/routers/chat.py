from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timezone
import uuid
import logging

import socketio

from database import db
from models import User, ChatSendRequest
from deps import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

# Socket.io server - shared with main app
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=False,
    engineio_logger=False
)
sio_app = socketio.ASGIApp(sio, socketio_path="")


@router.post("/send")
async def send_chat_message(request: ChatSendRequest):
    try:
        msg_doc = {
            "message_id": f"msg_{uuid.uuid4().hex[:12]}",
            "store_id": request.store_id,
            "customer_id": request.customer_id,
            "customer_name": request.customer_name,
            "sender": request.sender,
            "message": request.message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read": False
        }

        await db.chat_messages.insert_one(msg_doc)

        # Remove _id before emitting
        msg_doc.pop("_id", None)
        await sio.emit("new_message", msg_doc, room=f"store_{request.store_id}")

        return {"success": True, "message_id": msg_doc["message_id"]}
    except Exception as e:
        logging.error(f"Chat send error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{store_id}")
async def get_chat_messages(store_id: str, customer_id: Optional[str] = None):
    try:
        query = {"store_id": store_id}
        if customer_id:
            query["customer_id"] = customer_id

        messages = await db.chat_messages.find(query, {"_id": 0}).sort("timestamp", 1).to_list(1000)
        return messages
    except Exception as e:
        logging.error(f"Chat fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{store_id}")
async def get_chat_conversations(store_id: str, user: User = Depends(get_current_user)):
    try:
        store = await db.stores.find_one({"user_id": user.user_id, "store_id": store_id}, {"_id": 0})
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")

        pipeline = [
            {"$match": {"store_id": store_id}},
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$customer_id",
                "customer_name": {"$first": "$customer_name"},
                "last_message": {"$first": "$message"},
                "last_timestamp": {"$first": "$timestamp"},
                "unread_count": {
                    "$sum": {
                        "$cond": [
                            {"$and": [{"$eq": ["$sender", "customer"]}, {"$eq": ["$read", False]}]},
                            1, 0
                        ]
                    }
                }
            }},
            {"$sort": {"last_timestamp": -1}}
        ]

        conversations = await db.chat_messages.aggregate(pipeline).to_list(100)

        return [{
            "customer_id": conv["_id"],
            "customer_name": conv["customer_name"],
            "last_message": conv["last_message"],
            "last_timestamp": conv["last_timestamp"],
            "unread_count": conv["unread_count"]
        } for conv in conversations]
    except Exception as e:
        logging.error(f"Conversations fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-read")
async def mark_messages_read(store_id: str, customer_id: str, user: User = Depends(get_current_user)):
    try:
        await db.chat_messages.update_many(
            {"store_id": store_id, "customer_id": customer_id, "sender": "customer", "read": False},
            {"$set": {"read": True}}
        )
        return {"success": True}
    except Exception as e:
        logging.error(f"Mark read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---- Socket.io Event Handlers ----

@sio.event
async def connect(sid, environ):
    logging.info(f"Socket.io client connected: {sid}")
    await sio.emit('connection_established', {'sid': sid}, room=sid)


@sio.event
async def disconnect(sid):
    logging.info(f"Socket.io client disconnected: {sid}")


@sio.event
async def join_store(sid, data):
    store_id = data.get('store_id')
    if store_id:
        await sio.enter_room(sid, f"store_{store_id}")
        await sio.emit('joined_store', {'store_id': store_id}, room=sid)


@sio.event
async def leave_store(sid, data):
    store_id = data.get('store_id')
    if store_id:
        await sio.leave_room(sid, f"store_{store_id}")


@sio.event
async def send_message(sid, data):
    try:
        store_id = data.get('store_id')
        msg_doc = {
            "message_id": f"msg_{uuid.uuid4().hex[:12]}",
            "store_id": store_id,
            "customer_id": data.get('customer_id'),
            "customer_name": data.get('customer_name', 'Customer'),
            "sender": data.get('sender', 'customer'),
            "message": data.get('message'),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read": False
        }

        await db.chat_messages.insert_one(msg_doc)
        msg_doc.pop("_id", None)
        await sio.emit('new_message', msg_doc, room=f"store_{store_id}")
    except Exception as e:
        logging.error(f"Socket.io send_message error: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)


@sio.event
async def typing(sid, data):
    store_id = data.get('store_id')
    await sio.emit('user_typing', {
        'customer_name': data.get('customer_name', 'Someone'),
        'sender': data.get('sender', 'customer')
    }, room=f"store_{store_id}", skip_sid=sid)
