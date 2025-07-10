from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import uvicorn
import redis
from dotenv import load_dotenv
from service.chat import get_chat_service
from service.conversation_manager import ConversationManager

load_dotenv()

chat_service = None
manager = None
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    global chat_service, manager, redis_client
    print("🚀 アプリケーションの起動中...")
    try:
        # Redisの接続設定
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, max_connections=10 )
        if not redis_client.ping():
            print("❌ Redis接続失敗")
            raise RuntimeError("Redis connection failed")        
        else:
            print("✅ Redis接続成功")

        # chat_serviceの初期化
        try:
            chat_service = get_chat_service()
            print("✅ ChatService初期化完了")
        except Exception as e:
            print(f"❌ ChatService初期化失敗: {e}")
            raise RuntimeError(f"ChatService initialization failed: {e}")

        # managerの初期化
        try:
            manager = ConversationManager(redis_client)
            print("✅ ConversationManager初期化完了")
        except Exception as e:
            print(f"❌ ConversationManager初期化失敗: {e}")
            raise RuntimeError(f"ConversationManager initialization failed: {e}")

    except redis.ConnectionError as e:
        print(f"❌ redis接続エラーが発生しました: {e}")
        raise RuntimeError(f"Redis connection failed: {e}")

    except Exception as e:
        print(f"❌ アプリケーションの起動中にエラーが発生しました: {e}")
        raise RuntimeError(f"Application startup failed: {e}")

    yield

    # shutdown
    print("🛑 アプリケーションのシャットダウン中...")
    try:
        if redis_client:
            redis_client.close()
            print("✅ Redis接続を閉じました")
        else:
            print("❌ Redisクライアントが初期化されていません")
    except Exception as e:
        print(f"❌ Redis接続のシャットダウン中にエラーが発生しました: {e}")

# FastAPIアプリケーション作成
app = FastAPI(title="TUNA RAG ChatBot API", lifespan=lifespan)

api_router = APIRouter(prefix="/api/v1", tags=["CHATBOT API v1"])

@api_router.get("/create/session")
async def create_session() -> dict:
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

@api_router.post("/create/chat/{session_id}")
async def create_query(request: QueryRequest):
    """
    ユーザーの質問を受け取り、回答を生成する関数
    """
    try:
        past_conversation = manager.get_conversation(request.session_id)
        # 回答を生成
        response = await chat_service.create_response(
            query=request.query,
            conversation=past_conversation
        )

        # 会話履歴を保存
        manager.save_conversation(session_id=request.session_id, conversation={
            "query": request.query,
            "response": response
        })

        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat: {e}")

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_level="debug")