from fastapi import APIRouter

from api.endpoints import chats

api_router = APIRouter()
api_router.include_router(chats.router, prefix="/api/v1", tags=["CHATBOT API v1"])
