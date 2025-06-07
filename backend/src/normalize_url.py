import re
from urllib.parse import urlparse, urlunparse


def normalize_habr_url(url: str) -> str:
    """
    Нормализует URL статьи на Habr.com
    Преобразует различные форматы в стандартный: https://habr.com/{lang}/articles/{id}/
    """
    parsed = urlparse(url)
    
    # Проверяем, что это действительно habr.com
    if 'habr.com' not in parsed.netloc:
        return url
    
    path_parts = parsed.path.strip('/').split('/')
    
    # Ищем ID статьи в пути
    article_id = None
    
    # Проверяем различные паттерны URL
    if 'amp' in path_parts:
        # Формат: /ru/amp/publications/896594/
        for i, part in enumerate(path_parts):
            if part == 'publications' and i + 1 < len(path_parts):
                article_id = path_parts[i + 1]
                break
    elif 'articles' in path_parts:
        # Формат: /ru/articles/896594/
        for i, part in enumerate(path_parts):
            if part == 'articles' and i + 1 < len(path_parts):
                article_id = path_parts[i + 1]
                break
    elif 'post' in path_parts:
        # Старый формат: /ru/post/896594/
        for i, part in enumerate(path_parts):
            if part == 'post' and i + 1 < len(path_parts):
                article_id = path_parts[i + 1]
                break
    else:
        # Попробуем найти числовой ID в пути
        for part in path_parts:
            if part.isdigit():
                article_id = part
                break
    
    if not article_id:
        # Если не удалось найти ID, возвращаем исходный URL
        return url
    
    # Определяем язык (по умолчанию 'ru')
    lang = 'ru'
    for part in path_parts:
        if part in ['ru', 'en', 'es', 'zh']:  # Добавьте другие языки при необходимости
            lang = part
            break
    
    # Формируем нормализованный URL
    normalized_path = f"/{lang}/articles/{article_id}/"
    
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        normalized_path,
        '',
        '',
        ''
    ))
