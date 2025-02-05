# Dockerfile.plot
FROM python:3.9-slim

WORKDIR /app

# Устанавливаем netcat
RUN apt-get update && apt-get install -y netcat-openbsd

# Копируем requirements.txt из корневой папки проекта
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# Копируем скрипт wait-for-rabbitmq.sh и делаем его исполнимым
COPY features/wait-for-rabbitmq.sh .
RUN chmod +x wait-for-rabbitmq.sh

CMD ["./wait-for-rabbitmq.sh", "rabbitmq:5672", "--", "python", "plot/plot.py"]
