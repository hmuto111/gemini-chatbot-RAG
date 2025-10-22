from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import redis
from dotenv import load_dotenv
from service.chat import get_chat_service
from service.conversation_manager import ConversationManager
from api.api import api_router

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

        # managerの初期化
        try:
            manager = ConversationManager(redis_client)
            print("✅ ConversationManager初期化完了")
        except Exception as e:
            print(f"❌ ConversationManager初期化失敗: {e}")
            raise RuntimeError(f"ConversationManager initialization failed: {e}")

        # chat_serviceの初期化
        try:
            chat_service = get_chat_service(manager)
            print("✅ ChatService初期化完了")
        except Exception as e:
            print(f"❌ ChatService初期化失敗: {e}")
            raise RuntimeError(f"ChatService initialization failed: {e}")

        app.state.redis_client = redis_client
        app.state.manager = manager
        app.state.chat_service = chat_service

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

app.add_middleware(
    CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"],)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_level="debug")