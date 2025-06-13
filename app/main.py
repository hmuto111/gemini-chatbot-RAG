import os
from dotenv import load_dotenv
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

Settings.llm = Gemini(
    model_name="models/gemini-2.0-flash",
    temperature=0.22,
    api_key=GOOGLE_API_KEY
)

Settings.embed_model = GeminiEmbedding(
    model="models/text-embedding-004",
    api_key=GOOGLE_API_KEY,
    task_type="RETRIEVAL_DOCUMENT"
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


def main():
    while True:
      print("\nPlease enter your query, \nif you want to exit, type 'exit' or 'quit'")
      query = input("Query: ")

      if query.lower() in ['exit', 'quit']:
          print("Exiting the program.")
          break
      
      retriever = index.as_retriever(similarity_top_k=3, embed_model=Settings.embed_model)
      retrieved_nodes = retriever.retrieve(query)

      reference = ""
      if retrieved_nodes:
         print(f"Found {len(retrieved_nodes)} relevant source nodes.")
         for i, node in enumerate(retrieved_nodes):
            reference += f"## 参考情報 {i+1}\n"
            reference += f"{node.text}\n\n"
      else:
         print("No relevant source nodes found.")
         reference = "TUNAシステムの機能に関連する情報は見つかりませんでした。"

      prompt = f"""
以下の[命令]を絶対に守ってください。

[命令]
あなたはTUNAシステムの案内AIです。
あなたの役割は、ユーザーがTUNAシステムを効果的に利用できるようにサポートすることです。
あなたは、ユーザーの質問に対して、TUNAシステムの機能や操作方法についての情報を提供します。
以下の[解答例]、[参考情報]を参考にユーザーからの[質問]に答えてください。
また、該当する情報が見つからなかった場合は、絶対に空文字列を返してください

[質問]
{query}

[解答例]
# 投稿機能

## コメント

- **説明**: 自分や他アカウントの投稿にコメントができる機能。

## 投稿共有範囲の設定

- **説明**: 投稿ごとに任意で、グループ内・全体などで投稿を見れる他アカウントの制限を設定する機能。

[参考情報]
{reference}

"""

      # generate response
      response = Settings.llm.complete(prompt)
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

