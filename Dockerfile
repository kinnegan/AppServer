# Используем официальный Python образ
FROM python:3.11-slim

# Установим рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY /src/modules/. /app/
COPY requirements.txt /app/
COPY setup.py /app/
COPY pyproject.toml /app/

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn uvicorn

# Открываем порт для приложения
EXPOSE 8000

# Команда для запуска приложения с gunicorn и uvicorn worker
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "apis:app", "--bind", "0.0.0.0:8000"]
