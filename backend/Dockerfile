FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Запуск uvicorn сервера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
