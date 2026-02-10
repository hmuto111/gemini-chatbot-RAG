from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from api.deps import get_manager, get_chat_service
from service.conversation_manager import ConversationManager
from service.chat import ChatService

router = APIRouter()

@router.get("/create/session")
async def create_session(manager: ConversationManager=Depends(get_manager)) -> dict:
    """
    ユーザーの会話セッションを作成し、セッションIDを返す関数
    """
    try:
        session_id = manager.generate_sequential_session_id()
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {e}")

class QueryRequest(BaseModel):
    session_id: str
    query: str

@router.post("/create/chat")
async def create_query(request: QueryRequest, chat_service: ChatService=Depends(get_chat_service)) -> dict:
    """
    ユーザーの質問を受け取り、回答を生成する関数
    """
    try:
        response = await chat_service.handle_query(session_id=request.session_id, query=request.query)

        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat: {e}")
