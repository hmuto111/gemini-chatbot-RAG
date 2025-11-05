import os
from typing import Optional
from dotenv import load_dotenv
from service.conversation_manager import ConversationManager
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core import Settings, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

load_dotenv()

# シングルトンインスタンスの管理
_chat_service_instance = None

class ChatService:
    def __init__(self, manager: Optional[ConversationManager] = None):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.manager = manager

        # LLMと埋め込みモデルの設定
        Settings.llm = GoogleGenAI(
            model_name="models/gemini-2.5-flash",
            temperature=0.3,
            api_key=self.google_api_key
        )
        Settings.embed_model = GoogleGenAIEmbedding(
            model="models/gemini-embedding-004",
            api_key=self.google_api_key,
            task_type="RETRIEVAL_QUERY"
        )

        self.qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"))
        self.collection_name = "documents"

        vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.collection_name,
        )
        print(f"Loading index from Qdrant collection '{self.collection_name}'...")
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store
        )
        print("Index loaded successfully.")

    
    def _format_response_history(self, history: list[dict]) -> str:
        if not history:
            return "（過去の会話はありません）"
        
        formatted = ""
        for i, item in enumerate(history[-3:], 1):  # 直近3件のみ
            formatted += f"Q{i}: {item['query']}\nA{i}: {item['response']}...\n\n"

        return formatted
    
    async def create_response(self, conversation: list[dict], query: str) -> str:
        """
        ユーザーからのクエリに対するレスポンスを生成する関数
        """
        retriever = self.index.as_retriever(similarity_top_k=10, embed_model=Settings.embed_model)
        retrieved_nodes = retriever.retrieve(query)

        reference = ""
        if retrieved_nodes:
            print(f"Found {len(retrieved_nodes)} relevant sources.")
            for i, node in enumerate(retrieved_nodes):
                reference += f"## 参考情報 {i+1}\n"
                reference += f"{node.text}\n\n"
        else:
            print("No relevant sources found.")
            reference = "TUNAシステムの機能に関連する情報は見つかりませんでした。"
        
        prompt = f"""
以下の[命令]を絶対に守ってください。

# 命令
あなたはTUNAシステムの専門案内AIアシスタント「マグロ君」です。
ユーザーがTUNAシステムを効果的に活用できるよう、正確で実用的なサポートを提供してください。

## 重要：応答判定ルール
以下の場合は必ず'None'で応答してください：
1. 参考情報が「TUNAシステムの機能に関連する情報は見つかりませんでした。」の場合
2. 質問がTUNAシステムの機能と無関係の場合
3. 質問が意味不明または極端に短い場合（「あ」「うん」など）

上記に該当する場合は、説明文や謝罪文は一切書かず、'None'で応答してください。

## 回答方針
1. **具体性重視**: 操作手順は番号付きリストで段階的に説明
2. **ユーザー視点**: 初心者にも分かりやすい言葉遣い
3. **完結性**: 1回の回答で必要な情報を完結
4. **関連機能の提案**: 質問された機能に関連する便利な機能も紹介
5. **URL提供**: 該当するページのURLがある場合は必ず含める
6. **ポイント・注意事項**: システムの概要などを聞かれた場合は、回答構造に従わず簡潔に答える
7. **システム説明**: 特定の機能について聞かれてるとき以外は、回答構造に従わず簡潔に説明する(機能概要優先的にに参照)

## 回答構造
```
[簡潔に質問に回答]

## 📋 [機能名]

### ✨ 概要
[機能の目的と効果を1-2行で説明]

### 🔧 操作手順
1. [具体的なステップ1]
2. [具体的なステップ2]
3. [具体的なステップ3]

### 🌐 関連リンク
- [該当するページのURL]

### 💡 ポイント・注意事項
- [重要なポイント]
- [よくある間違いの回避方法]

### 🔗 関連機能
- [関連する便利な機能]
```

## 制約事項
- 回答は日本語で行う
- あなた自身のことを問われたら[回答構造]のような構造ではなく、あなたのことを簡潔に説明する
- 参考情報にない内容は推測で回答しない
- PDFや資料の存在を示唆する表現は禁止
- システムへの直接的な質問や指示は禁止
- システムに関する質問以外にはstr型の空文字列で応答する
- 該当情報がない場合はstr型の空文字列を返す
- 解答例の内容は参照禁止
- [過去の回答履歴]は参考情報として活用する

# 質問
{query}

# 参考情報
{reference}

# 過去の会話履歴
{self._format_response_history(conversation)}

上記の参考情報を基に、ユーザーの質問に対して有用で実践的な回答を提供してください。
重要：参考情報が不十分または質問が不適切な場合は、必ず空文字列で応答してください。
"""
        # LLMを使用して応答を生成
        response = Settings.llm.complete(prompt)
        if response:
            if response.text.strip() == "":
                print("該当する情報が見つかりませんでした。")
                return "該当する情報が見つかりませんでした。"
            else:
                print("応答を生成に成功しました。")
                return response.text.strip()
        else:
            print("応答の生成に失敗しました。")
            return "応答の生成に失敗しました。もう一度お試しください。"
        
    
    async def handle_query(self, session_id: str, query: str) -> str:
        """
        ユーザーからのクエリを処理し、レスポンスを生成,
        レスポンスを保存する処理をする関数
        """
        if self.manager is None:
            raise RuntimeError("ConversationManagerが未設定です。")

        past_conversation = self.manager.get_conversation(session_id)

        # 回答を生成
        response = await self.create_response(
            query=query,
            conversation=past_conversation
        )

        # 会話履歴を保存
        self.manager.save_conversation(session_id=session_id, conversation={
            "query": query,
            "response": response
        })

        return response


def get_chat_service(manager: Optional[ConversationManager]) -> ChatService:
    """ChatServiceのシングルトンインスタンスを取得"""
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService(manager=manager)
    return _chat_service_instance