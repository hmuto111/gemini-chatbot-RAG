from fastapi import Request
from service.conversation_manager import ConversationManager
from service.chat import ChatService

def get_manager(request: Request) -> ConversationManager:
    return request.app.state.manager

def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service
