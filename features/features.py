import pika
import numpy as np
import json
from sklearn.datasets import load_diabetes
import time
from datetime import datetime

# Создаём бесконечный цикл для отправки сообщений в очередь
while True:
    try:
        # Загружаем датасет о диабете
        X, y = load_diabetes(return_X_y=True)
        # Формируем случайный индекс строки
        random_row = np.random.randint(0, X.shape[0]-1)

        # Генерируем уникальный идентификатор для сообщения
        message_id = datetime.timestamp(datetime.now())

        # Создаём подключение по адресу rabbitmq:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Создаём очередь y_true
        channel.queue_declare(queue='y_true')
        # Создаём очередь features
        channel.queue_declare(queue='features')

        # Формируем сообщение для y_true с уникальным ID
        message_y_true = {
            'id': message_id,
            'body': y[random_row]
        }
        # Публикуем сообщение в очередь y_true
        channel.basic_publish(exchange='',
                            routing_key='y_true',
                            body=json.dumps(message_y_true))
        print(f"Сообщение с правильным ответом (ID: {message_id}) отправлено в очередь")

        # Формируем сообщение для features с уникальным ID
        message_features = {
            'id': message_id,
            'body': list(X[random_row])
        }
        # Публикуем сообщение в очередь features
        channel.basic_publish(exchange='',
                            routing_key='features',
                            body=json.dumps(message_features))
        print(f"Сообщение с вектором признаков (ID: {message_id}) отправлено в очередь")

        # Закрываем подключение
        connection.close()

        # Задержка на 10 секунд
        time.sleep(10)
    except Exception as e:
        print(f'Features: Не удалось подключиться к очереди: {e}')
