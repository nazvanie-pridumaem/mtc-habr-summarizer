from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from typing import AsyncGenerator

from src.parser import parse_article
from src.summarizator import process_article, process_article_streaming

app = FastAPI()

class Link(BaseModel):
    link: str

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI backend!"}

@app.post("/summarize")
async def summarize_stream(link: Link):
    """Эндпоинт для потоковой суммаризации"""
    try:
        # Получаем контент статьи
        response = parse_article(link.link)
        
        if not response or 'text_content' not in response:
            async def error_stream():
                yield f"data: {json.dumps({'type': 'error', 'message': 'Не удалось получить контент статьи'})}\n\n"
            
            return StreamingResponse(
                error_stream(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream",
                }
            )
        
        # Возвращаем поток
        return StreamingResponse(
            process_article_streaming(response["text_content"]),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        async def error_stream():
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)