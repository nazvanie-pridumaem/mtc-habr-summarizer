import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.normalize_url import normalize_habr_url
from src.parser import parse_article
from src.summarizator import process_article_streaming
from src.models import get_db, ArticleRating

load_dotenv()
app = FastAPI()

class Link(BaseModel):
    link: str

class RatingRequest(BaseModel):
    article_url: str
    summarized_text: str
    rating: int

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
        response = parse_article(normalized_url)
        
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

@app.post("/rate")
async def rate_article(rating_request: RatingRequest, db: Session = Depends(get_db)):
    """Эндпоинт для сохранения оценки статьи"""
    try:
        # Валидация рейтинга
        if rating_request.rating < 1 or rating_request.rating > 5:
            raise HTTPException(status_code=400, detail="Рейтинг должен быть от 1 до 5")
        
        # Создаем новую запись в БД
        article_rating = ArticleRating(
            article_url=rating_request.article_url,
            summarized_text=rating_request.summarized_text,
            rating=rating_request.rating
        )
        
        db.add(article_rating)
        db.commit()
        db.refresh(article_rating)
        
        return {
            "success": True,
            "message": "Спасибо за вашу оценку!",
            "rating_id": article_rating.id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении оценки: {str(e)}")

@app.get("/ratings/stats")
async def get_ratings_stats(db: Session = Depends(get_db)):
    """Эндпоинт для получения статистики оценок"""
    try:
        total_ratings = db.query(ArticleRating).count()
        if total_ratings == 0:
            return {"total_ratings": 0, "average_rating": 0}
        
        # Вычисляем среднюю оценку
        avg_rating = db.query(
            func.avg(ArticleRating.rating)
        ).scalar()
        
        return {
            "total_ratings": total_ratings,
            "average_rating": round(float(avg_rating or 0), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении статистики: {str(e)}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)