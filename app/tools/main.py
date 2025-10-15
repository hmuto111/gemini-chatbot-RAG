import os
from dotenv import load_dotenv
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core import Settings, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

Settings.llm = GoogleGenAI(
    model_name="models/gemini-2.0-flash",
    temperature=0.22,
    api_key=GOOGLE_API_KEY
)

Settings.embed_model = GoogleGenAIEmbedding(
    model="models/gemini-embedding-exp-03-07",
    api_key=GOOGLE_API_KEY,
    task_type="RETRIEVAL_QUERY"
)

qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"))
collection_name = "documents"

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=collection_name,
)

print(f"Loading index from Qdrant collection '{collection_name}'...")
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store
)
print("Index loaded successfully.")

def format_response_history(history):
    if not history:
        return "（過去の会話はありません）"
    
    formatted = ""
    for i, item in enumerate(history[-3:], 1):  # 直近3件のみ
        formatted += f"Q{i}: {item['query']}\nA{i}: {item['response']}...\n\n"

    return formatted

def main():
    response_history = []
    while True:
      print("\nPlease enter your query, \nif you want to exit, type 'exit' or 'quit'")
      query = input("Query: ")

      if query.lower() in ['exit', 'quit']:
          print("Exiting the program.")
          break
      
      retriever = index.as_retriever(similarity_top_k=10, embed_model=Settings.embed_model)
      retrieved_nodes = retriever.retrieve(query)

      reference = ""
      if retrieved_nodes:
         print(f"Found {len(retrieved_nodes)} relevant source nodes.")
         for i, node in enumerate(retrieved_nodes):
            score = getattr(node, 'score', 'N/A')
            print(f"類似度スコア: {score}\nテキスト概要: {node.text[:100]}...")  # 最初の50文字を表示
            reference += f"## 参考情報 {i+1}\n"
            reference += f"{node.text}\n\n"
      else:
         print("No relevant source nodes found.")
         reference = "TUNAシステムの機能に関連する情報は見つかりませんでした。"

      prompt = f"""
以下の[命令]を絶対に守ってください。

# 命令
あなたはTUNAシステムの専門案内AIアシスタント「マグロ君」です。
ユーザーがTUNAシステムを効果的に活用できるよう、正確で実用的なサポートを提供してください。

## 重要：応答判定ルール
以下の場合は必ず空の文字列（何も書かない状態）で応答してください：
1. 参考情報が「TUNAシステムの機能に関連する情報は見つかりませんでした。」の場合
2. 質問がTUNAシステムの機能と無関係の場合
3. 質問が意味不明または極端に短い場合（「あ」「うん」など）

上記に該当する場合は、説明文や謝罪文は一切書かず、完全に空の状態で応答してください。

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
{format_response_history(response_history)}

上記の参考情報を基に、ユーザーの質問に対して有用で実践的な回答を提供してください。
重要：参考情報が不十分または質問が不適切な場合は、必ず空文字列で応答してください。
"""
      # generate response
      response = Settings.llm.complete(prompt)
      response_history.append({"response": response.text, "query": query})
      if response:
        if response.text == "":
          print("該当する情報が見つかりませんでした.")
        else:
          print(len(response.text))
          print("\nResponse\n")
          print(response.text)
      else:
        print("Failed to generate response...")


if __name__ == "__main__":
    main()

