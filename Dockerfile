# Используем официальный Python-образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn uvicorn

# Копируем исходный код приложения
COPY . .

ENV PYTHONPATH=/app/src:$PYTHONPATH

# Открываем порт приложения
EXPOSE 8000

# Команда для запуска приложения
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "modules.apis:app", "--bind", "0.0.0.0:8000"]
