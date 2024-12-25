import pika
import json
import time
import logging
import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Словари для хранения y_true и y_pred по уникальному ID
y_true_dict = {}
y_pred_dict = {}

# Путь к файлу лога
metric_log_path = './logs/metric_log.csv'

# Функция callback для обработки сообщений
def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        logging.debug(f"Получено сообщение: {message}")
        # Проверка, что данные приходят правильно
        logging.debug(f"ch: {ch}")
        logging.debug(f"method: {method}")
        logging.debug(f"properties: {properties}")
        logging.debug(f"Сообщение в raw формате: {body}")

        message_id = message['id']
        if method.routing_key == 'y_true':
            y_true_dict[message_id] = message['body']
            logging.debug(f"Сохранено значение y_true для id {message_id}")
        elif method.routing_key == 'y_pred':
            y_pred_dict[message_id] = message['body']
            logging.debug(f"Сохранено значение y_pred для id {message_id}")

        # Если есть и y_true, и y_pred для одного id, считаем абсолютную ошибку
        if message_id in y_true_dict and message_id in y_pred_dict:
            y_true_value = y_true_dict[message_id]
            y_pred_value = y_pred_dict[message_id]
            absolute_error = abs(y_true_value - y_pred_value)
            logging.debug(f"Абсолютная ошибка для id {message_id}: {absolute_error}")

            # Записываем в CSV
            df = pd.DataFrame({
                'id': [message_id],
                'y_true': [y_true_value],
                'y_pred': [y_pred_value],
                'absolute_error': [absolute_error]
            })

            df.to_csv(metric_log_path, mode='a', header=not pd.io.common.file_exists(metric_log_path), index=False)
            logging.debug(f"Данные для id {message_id} записаны в metric_log.csv")

    except Exception as e:
        logging.error(f"Ошибка при подключении к RabbitMQ: {e}")
        time.sleep(5)

# Подключение к RabbitMQ
while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Объявляем очереди
        channel.queue_declare(queue='y_true', durable=True)
        channel.queue_declare(queue='y_pred', durable=True)
        logging.debug("Очереди y_true и y_pred объявлены")

        # Извлекаем сообщения из очередей
        channel.basic_consume(queue='y_true', on_message_callback=callback, auto_ack=True)
        channel.basic_consume(queue='y_pred', on_message_callback=callback, auto_ack=True)

        logging.debug('Ожидание сообщений, для выхода нажмите CTRL+C')
        channel.start_consuming()
        break

    except Exception as e:
        logging.error(f"Ошибка при подключении к RabbitMQ: {e}")
        time.sleep(5)
