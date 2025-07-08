from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def handle_query(request: QueryRequest):
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0", port=8000, log_level="debug")