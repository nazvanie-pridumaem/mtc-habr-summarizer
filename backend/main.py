from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.parser import parse_article

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI backend!"}

@app.post("/summarize")
async def summarize(url: str, description="Суммаризировать статью через этот эндпоинт"):
    response = parse_article(url)

    return JSONResponse(content=response, status_code=200)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)