import os
from dotenv import load_dotenv
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from llama_index.vector_stores.qdrant import QdrantVectorStore

from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

Settings.embed_model = GeminiEmbedding(model="models/text-embedding-004", api_key=GOOGLE_API_KEY, task_type="RETRIEVAL_DOCUMENT")

qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"))
collection_name = "documents"

try:
    # コレクション作成
    qdrant_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    print(f"Collection '{collection_name}' created successfully.")
except Exception as e:
    print(f"Error creating collection '{collection_name}': {e}")

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=collection_name,
)

print("Loading documents...")
documents = SimpleDirectoryReader("../data").load_data()
print(f"Loaded {len(documents)} documents.")

print("Creating index and storing embeddings in Qdrant using Gemini Embedding...")
# index = VectorStoreIndex.from_documents(
#     documents,
#     vector_store=vector_store,
# )

points = []
for doc in documents:
    vec = Settings.embed_model.get_text_embedding(doc.text)
    # 一意のIDを振る
    points.append(PointStruct(
        id=str(uuid.uuid4()),
        vector=vec,
        payload={"text": doc.text},
    ))
# ここで明示的に upsert
qdrant_client.upsert(
    collection_name=collection_name,
    points=points,
)
print("Index created and embeddings stored successfully.")



# --- コレクション確認 ---
count_resp = qdrant_client.count(collection_name=collection_name)
print(f"Collection '{collection_name}' point count: {count_resp}")

# --- Qdrant 中身確認用スニペット ---
print("Dumping stored points…")
# 最大 100 件ずつスクロールで取得
points, next_page = qdrant_client.scroll(
    collection_name=collection_name,
    limit=100,
    with_payload=True,
    with_vectors=False,
)

print(f"total retrieved: {len(points)}")
for pt in points:
    print(f"id={pt.id}, payload={pt.payload}")