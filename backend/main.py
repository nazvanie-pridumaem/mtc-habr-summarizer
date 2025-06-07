import asyncio
import json
import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from src.normalize_url import normalize_habr_url
from src.parser import parse_article
from src.summarizator import process_article_streaming

load_dotenv()
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
        # Нормализуем URL
        normalized_url = normalize_habr_url(link.link)    
        # Получаем контент статьи
        response = parse_article(normalized_url)  # Исправлена опечатка
        
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
        
        async def enhanced_stream():
            # Сначала отправляем метаданные
            metadata = {
                'type': 'metadata',
                'title': response.get('title', 'Без названия')
            }
            yield f"data: {json.dumps(metadata, ensure_ascii=False)}\n\n"
            
            # Затем передаем управление основному потоку обработки
            async for chunk in process_article_streaming(response["text_content"]):
                yield chunk
        
        # Возвращаем поток
        return StreamingResponse(
            enhanced_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        error_message = str(e)
        
        async def error_stream():
            yield f"data: {json.dumps({'type': 'error', 'message': error_message}, ensure_ascii=False)}\n\n"
        
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
    allow_origins=["http://localhost:3000", os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)