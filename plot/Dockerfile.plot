# Dockerfile.plot
FROM python:3.9-slim

WORKDIR /app

# Копируем requirements.txt из корневой папки проекта
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "plot/plot.py"]
