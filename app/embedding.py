import os
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
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
        vectors_config=VectorParams(size=4096, distance=Distance.COSINE),
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
index = VectorStoreIndex.from_documents(
    documents,
    vector_store=vector_store,
)
print("Index created and embeddings stored successfully.")



# --- コレクション確認 ---
count_resp = qdrant_client.count(collection_name=collection_name)
print(f"Collection '{collection_name}' point count: {count_resp}")