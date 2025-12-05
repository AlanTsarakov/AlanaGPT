FROM python:3.11-slim

WORKDIR /app

# Копируем requirements.txt в текущую рабочую директорию (/app)
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВСЕ файлы из текущей директории хоста в /app
COPY . .

# Запускаем main.py из AlanaGPT директории
CMD ["python", "AlanaGPT/main.py"]