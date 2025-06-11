from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Создаем базовый класс для моделей
Base = declarative_base()

# Получаем URL базы данных из переменных окружения или используем SQLite по умолчанию
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./article_ratings.db")

# Создаем движок базы данных
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ArticleRating(Base):
    """Модель для хранения оценок статей"""
    __tablename__ = "article_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    article_url = Column(Text, nullable=False)
    summarized_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)  # от 1 до 5

# Создаем таблицы
Base.metadata.create_all(bind=engine)

def get_db():
    """Функция для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()