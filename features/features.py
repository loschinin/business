import pika
import numpy as np
import json
from sklearn.datasets import load_diabetes
import time
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Создаём бесконечный цикл для отправки сообщений в очередь
while True:
    try:
        logging.debug("Загружаем датасет о диабете")
        # Загружаем датасет о диабете
        X, y = load_diabetes(return_X_y=True)

        # Формируем случайный индекс строки
        random_row = np.random.randint(0, X.shape[0]-1)

        # Генерируем уникальный идентификатор для сообщения
        message_id = datetime.timestamp(datetime.now())
        logging.debug(f"Сгенерирован уникальный идентификатор сообщения: {message_id}")

        # Создаём подключение к RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Создаём очередь y_true
        channel.queue_declare(queue='y_true', durable=True)
        # Создаём очередь features
        channel.queue_declare(queue='features', durable=True)
        logging.debug("Очереди y_true и features созданы")

        # Формируем сообщение для y_true с уникальным ID
        message_y_true = {
            'id': message_id,
            'body': y[random_row]
        }
        logging.debug(f"Отправляем сообщение в очередь y_true с id {message_id}")
        # Публикуем сообщение в очередь y_true
        channel.basic_publish(exchange='',
                              routing_key='y_true',
                              body=json.dumps(message_y_true))

        logging.debug(f"Сообщение с правильным ответом (ID: {message_id}) отправлено в очередь")

        # Формируем сообщение для features с уникальным ID
        message_features = {
            'id': message_id,
            'body': list(X[random_row])
        }
        logging.debug(f"Отправляем сообщение в очередь features с id {message_id}")
        # Публикуем сообщение в очередь features
        channel.basic_publish(exchange='',
                              routing_key='features',
                              body=json.dumps(message_features))

        logging.debug(f"Сообщение с вектором признаков (ID: {message_id}) отправлено в очередь")

        # Закрываем подключение
        connection.close()
        logging.debug(f"Подключение к RabbitMQ закрыто для сообщения с id {message_id}")

        # Задержка на 10 секунд
        time.sleep(10)

    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")
        time.sleep(5)  # Повторяем попытку через 5 секунд
