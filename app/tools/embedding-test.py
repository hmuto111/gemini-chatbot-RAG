import os
from dotenv import load_dotenv

import qdrant_client
from qdrant_client.http.models import Distance, VectorParams
from llama_index.vector_stores.qdrant import QdrantVectorStore

from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from google.genai.types import EmbedContentConfig
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter,MarkdownNodeParser,MarkdownNodeParser

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# google-genai embed model 
embed_model = GoogleGenAIEmbedding(
    api_key=GOOGLE_API_KEY,
    model_name="models/text-embedding-004",
    embed_config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    query_embed_config=EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
)

# qdrant client
client = qdrant_client.QdrantClient(url=os.getenv("QDRANT_URL"))
vector_store = QdrantVectorStore(
    collection_name="documents", client=client
)

# if collection exists, recreate collection
COLLECTION_NAME = "documents"
VECTOR_SIZE = 768

try:
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"collection '{COLLECTION_NAME}' is recreated.")
except Exception as e:
    print(f"collection recreation failed. : {e}")

# configure the destination vector store 
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# load documents data
reader = SimpleDirectoryReader(input_dir="../data", encoding="utf-8")
documents = reader.load_data()

splitter = SentenceSplitter(chunk_size=512, chunk_overlap=128)

index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    embed_model=embed_model,
    transformations=[splitter]
)

print(index)

embeddings = embed_model.get_text_embedding("Google Gemini Embeddings.")
print(embeddings[:5])
print(f"Dimension of embeddings: {len(embeddings)}")