import re
import json
import asyncio
from typing import Any, Dict, List, AsyncGenerator

import torch
from bs4 import BeautifulSoup
from transformers import T5ForConditionalGeneration, T5Tokenizer

# Загрузка токенизатора и модели
model = T5ForConditionalGeneration.from_pretrained("ghostbim21/ru_text_summary", trust_remote_code=False)
tokenizer = T5Tokenizer.from_pretrained("ghostbim21/ru_text_summary", trust_remote_code=False)

# Определяем устройство (GPU если доступен)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
model.eval()  # Переводим в режим инференса

# Параметры батчинга
BATCH_SIZE = 8
MAX_INPUT_LENGTH = 512
MAX_OUTPUT_LENGTH = 350
MIN_OUTPUT_LENGTH = 150
CHUNK_SIZE = 450

def basic_clean(text):
    if not isinstance(text, str):
        return text
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def advanced_clean(text):
    if not isinstance(text, str):
        return ''
    
    text = basic_clean(text)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\s+([.,!?:;])', r'\1', text)
    text = re.sub(r'([.,!?:;])\s+', r'\1 ', text)
    
    return re.sub(r'\s+', ' ', text).strip()

def clean_text(text, advanced=False):
    if not isinstance(text, str):
        return text
    return advanced_clean(text) if advanced else basic_clean(text)

def split_text_into_chunks(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """Разбивает текст на чанки с учетом границ предложений"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += 1
        
        # Проверяем, является ли слово концом предложения
        if current_size >= chunk_size and word.endswith(('.', '!', '?')):
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
    
    # Добавляем оставшийся текст
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def batch_summarize(texts: List[str], model, tokenizer, batch_size: int = BATCH_SIZE) -> List[str]:
    """Батчевая суммаризация текстов"""
    summaries = []
    
    # Обрабатываем тексты батчами
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        
        # Добавляем префикс "summarize: " к каждому тексту
        batch_texts = ["summarize: " + text for text in batch_texts]
        
        # Токенизация батча
        inputs = tokenizer(
            batch_texts,
            return_tensors="pt",
            max_length=MAX_INPUT_LENGTH,
            truncation=True,
            padding=True
        ).to(device)
        
        # Генерация суммаризаций
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=MAX_OUTPUT_LENGTH,
                min_length=MIN_OUTPUT_LENGTH,
                num_beams=5,
                length_penalty=2.0,
                no_repeat_ngram_size=2,
                early_stopping=True
            )
        
        # Декодирование результатов
        batch_summaries = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        summaries.extend(batch_summaries)
    
    return summaries

def summarize_long_text(text: str, model, tokenizer) -> str:
    """Суммаризация длинного текста с использованием чанков и батчинга"""
    # Если текст короткий, обрабатываем как обычно
    if len(text.split()) <= CHUNK_SIZE:
        return batch_summarize([text], model, tokenizer)[0]
    
    # Разбиваем на чанки
    chunks = split_text_into_chunks(text, CHUNK_SIZE)
    
    # Батчевая суммаризация чанков
    chunk_summaries = batch_summarize(chunks, model, tokenizer)
    
    # Объединяем суммаризации чанков
    combined_summary = " ".join(chunk_summaries)
    
    # Если объединенная суммаризация все еще слишком длинная, суммаризируем еще раз
    if len(combined_summary.split()) > CHUNK_SIZE:
        return summarize_long_text(combined_summary, model, tokenizer)
    
    return combined_summary

def parse_html_content(html_content: str):
    soup = BeautifulSoup(html_content, 'html.parser')
    result = []
    current_header = None
    current_content = []
    
    def process_element(element):
        nonlocal current_content
        
        if element.name in ['h1', 'h2', 'h3']:
            return element.get_text(strip=True)
        elif element.name == 'blockquote':
            parts = []
            current_part = []
            
            for child in element.children:
                if child.name == 'br':
                    if current_part:
                        parts.append(' '.join(current_part))
                        current_part = []
                else:
                    text = child.get_text(strip=True)
                    if text:
                        current_part.append(text)
            
            if current_part:
                parts.append(' '.join(current_part))
            
            if parts:
                current_content.append(parts)
        elif element.name == 'ul':
            list_items = [li.get_text(strip=True) for li in element.find_all('li', recursive=False)]
            if list_items:
                current_content.append(list_items)
        elif element.name is None or element.name not in ['br', 'b']:
            text = element.get_text(strip=True)
            if text:
                current_content.append(text)
    
    for element in soup.children:
        if element.name in ['h1', 'h2', 'h3']:
            if current_content:
                result.append({
                    'header': current_header,
                    'content': current_content.copy()
                })
                current_content = []
            
            current_header = element.get_text(strip=True)
        else:
            process_element(element)
    
    if current_content:
        result.append({
            'header': current_header,
            'content': current_content.copy()
        })
    
    return result

def summarize_structure_optimized(structure: List[Dict[str, Any]], model, tokenizer) -> List[Dict[str, Any]]:
    """Оптимизированная суммаризация структуры с батчингом"""
    
    def process_item(item):
        if isinstance(item, str):
            return item
        elif isinstance(item, list):
            processed_items = []
            for subitem in item:
                processed_items.append(process_item(subitem))
            return " ".join(processed_items)
        return str(item)
    
    def combine_content(section):
        text_parts = []
        for item in section['content']:
            text_parts.append(process_item(item))
        return " ".join(text_parts) if text_parts else ""
    
    # Собираем все тексты для суммаризации
    texts_to_summarize = []
    section_indices = []
    
    for idx, section in enumerate(structure):
        full_text = combine_content(section)
        if full_text:
            texts_to_summarize.append(full_text)
            section_indices.append(idx)
    
    # Обрабатываем длинные тексты
    processed_texts = []
    for text in texts_to_summarize:
        if len(text.split()) > CHUNK_SIZE:
            # Для очень длинных текстов используем чанкинг
            summary = summarize_long_text(text, model, tokenizer)
            processed_texts.append(summary)
        else:
            processed_texts.append(text)
    
    # Батчевая суммаризация всех текстов
    if processed_texts:
        summaries = batch_summarize(processed_texts, model, tokenizer)
        
        # Обновляем структуру
        for idx, section_idx in enumerate(section_indices):
            structure[section_idx]['content'] = [summaries[idx]]
    
    # Очищаем пустые секции
    for section in structure:
        if section not in [structure[i] for i in section_indices]:
            section['content'] = []
    
    return structure

async def summarize_structure_streaming(structure: List[Dict[str, Any]], model, tokenizer) -> AsyncGenerator[str, None]:
    """Потоковая суммаризация структуры с отправкой результатов по мере готовности"""
    
    def process_item(item):
        if isinstance(item, str):
            return item
        elif isinstance(item, list):
            processed_items = []
            for subitem in item:
                processed_items.append(process_item(subitem))
            return " ".join(processed_items)
        return str(item)
    
    def combine_content(section):
        text_parts = []
        for item in section['content']:
            text_parts.append(process_item(item))
        return " ".join(text_parts) if text_parts else ""
    
    # Отправляем начальное сообщение
    yield f"data: {json.dumps({'type': 'start', 'total_sections': len(structure)})}\n\n"
    
    # Обрабатываем каждую секцию отдельно
    processed_sections = []
    
    for idx, section in enumerate(structure):
        full_text = combine_content(section)
        
        if full_text:
            # Отправляем уведомление о начале обработки секции
            section_name = section.get('header', f'Раздел {idx + 1}')
            yield f"data: {json.dumps({'type': 'processing', 'section_index': idx, 'header': section_name})}\n\n"
            
            # Суммаризируем секцию
            if len(full_text.split()) > CHUNK_SIZE:
                summary = summarize_long_text(full_text, model, tokenizer)
            else:
                summary = batch_summarize([full_text], model, tokenizer)[0]
            
            # Создаем обработанную секцию
            processed_section = {
                'header': section['header'],
                'content': [summary]
            }
            processed_sections.append(processed_section)
            
            # Отправляем результат секции
            yield f"data: {json.dumps({'type': 'section_complete', 'section_index': idx, 'section': processed_section})}\n\n"
            
        else:
            # Пустая секция
            processed_section = {
                'header': section['header'],
                'content': []
            }
            processed_sections.append(processed_section)
            
            yield f"data: {json.dumps({'type': 'section_complete', 'section_index': idx, 'section': processed_section})}\n\n"
        
        # Небольшая пауза для избежания блокировки
        await asyncio.sleep(0.1)
    
    # Отправляем финальное сообщение
    yield f"data: {json.dumps({'type': 'complete', 'result': processed_sections})}\n\n"

async def process_article_streaming(html_content: str, model=model, tokenizer=tokenizer) -> AsyncGenerator[str, None]:
    """Главная функция для потоковой обработки статей"""
    try:
        # Базовая очистка с сохранением HTML
        cleaned_basic = clean_text(html_content)
        
        # Парсинг HTML
        parsed_content = parse_html_content(cleaned_basic)
        
        # Потоковая суммаризация
        async for chunk in summarize_structure_streaming(parsed_content, model, tokenizer):
            yield chunk
            
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': f'Ошибка обработки: {str(e)}'})}\n\n"
