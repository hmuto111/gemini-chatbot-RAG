import os
from dotenv import load_dotenv
import uuid
import glob

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from llama_index.vector_stores.qdrant import QdrantVectorStore

from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.readers.file import PDFReader

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

Settings.embed_model = GoogleGenAIEmbedding(model="models/gemini-embedding-exp-03-07", api_key=GOOGLE_API_KEY, task_type="RETRIEVAL_DOCUMENT")

qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"))
collection_name = "documents"

try:
    # コレクションの存在確認と作成
    if qdrant_client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' already exists. Deleting...")
        qdrant_client.delete_collection(collection_name=collection_name)
        print(f"Collection '{collection_name}' deleted. Recreating...")
    else:
        print(f"Collection '{collection_name}' creating...")
    
    qdrant_client.create_collection(
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

# PDF読み込み処理を追加
pdf_reader = PDFReader()
pdf_files = glob.glob("../data/pdf/*.pdf")
pdf_documents = []

for pdf_file in pdf_files:
    try:
        pdf_docs = pdf_reader.load_data(file=pdf_file)
        pdf_documents.extend(pdf_docs)
        print(f"Loaded PDF: {pdf_file} ({len(pdf_docs)} pages)")
    except Exception as e:
        print(f"Error loading PDF {pdf_file}: {e}")

# PDFドキュメントをメインドキュメントリストに追加
documents.extend(pdf_documents)
print(f"Total loaded: {len(documents)} documents (including PDFs)")

print("Creating index and storing embeddings in Qdrant using Gemini Embedding...")

points = []
for doc in documents:
    vec = Settings.embed_model.get_text_embedding(doc.text)
    
    # PDFかMarkdownかを判定
    is_pdf = doc in pdf_documents
    source_type = "pdf" if is_pdf else "markdown"

    file_name = "unknown"
    if hasattr(doc, 'metadata') and doc.metadata:
        file_name = doc.metadata.get('file_name', doc.metadata.get('file_path', 'unknown'))
        if file_name != 'unknown':
            file_name = os.path.basename(file_name)
            
    # 一意のIDを振る
    points.append(PointStruct(
        id=str(uuid.uuid4()),
        vector=vec,
        payload={"text": doc.text, "file_name": file_name, "source_type": source_type},
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