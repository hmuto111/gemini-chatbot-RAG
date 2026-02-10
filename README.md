# gemini-chatbot-RAG

## 使用技術

- python 3.12.3
- node 23.11.0
- docker compose

## 環境構築

```bash
# python環境構築
python -m venv venv
#    or
python3 -m venv venv

# venvのアクティベート
source venv/bin/activate

pip install -r requirements.txt

# ベクトル DB へのデータの追加
cd app/tools

python3 embedding.py
```

## 起動方法

### frontend

```bash
cd frontend

pnpm i

pnpm run dev
```

### backend

```bash
cd app

uvicorn main:app --reload
```

### DB

```
docker compose up -d
```
