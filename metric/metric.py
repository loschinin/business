import pika
import json
import time
import logging
import pandas as pd
import numpy as np
import os
import pandas as pd
import json
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

metric_log_path = './logs/metric_log.csv'

# Проверка существования файла и его создание, если нужно
if not os.path.exists(metric_log_path):
    logging.debug(f"Файл {metric_log_path} не существует, создаём новый.")

# Функция для записи в CSV
def write_to_csv(message_id, y_true_value, y_pred_value, absolute_error):
    try:
        # Записываем данные в DataFrame
        df = pd.DataFrame({
            'id': [message_id],
            'y_true': [y_true_value],
            'y_pred': [y_pred_value],
            'absolute_error': [absolute_error]
        })

        # Логирование данных перед записью
        logging.debug(f"Записываем в CSV: {df}")

        # Проверка, если файл уже существует
        file_exists = os.path.exists(metric_log_path)

        # Записываем данные
        df.to_csv(metric_log_path, mode='a', header=not file_exists, index=False)
        logging.debug(f"Данные для id {message_id} записаны в {metric_log_path}")

    except Exception as e:
        logging.error(f"Ошибка при записи в CSV: {e}")

# Пример вызова функции
# write_to_csv('example_id', 100.0, 95.0, 5.0)


# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Словари для хранения y_true и y_pred по уникальному ID
y_true_dict = {}
y_pred_dict = {}

# Путь к файлу лога
metric_log_path = './logs/metric_log.csv'

# Функция для чтения первых 5 строк из CSV
def read_first_5_lines():
    try:
        df = pd.read_csv(metric_log_path)
        logging.debug("metric: Первые 5 строк из metric_log.csv:")
        logging.debug(df.head())  # Вывод первых 5 строк
    except Exception as e:
        logging.error(f"Ошибка при чтении metric_log.csv: {e}")

# Функция callback для обработки сообщений
def callback(ch, method, properties, body):
    logging.debug(f"Callback function вызвана. Получено сообщение с body: {body}")
    logging.debug(f'Из очереди {method.routing_key} получено значение {json.loads(body)}')
    try:
        message = json.loads(body)
        logging.debug(f"Получено сообщение: {message}")
        # Проверка, что данные приходят правильно
        logging.debug(f"ch: {ch}")
        logging.debug(f"method: {method}")
        logging.debug(f"properties: {properties}")
        logging.debug(f"Сообщение в raw формате: {body}")
        # Выводим первые 5 строк
        read_first_5_lines()

        message_id = message['id']
        if method.routing_key == 'y_true':
            y_true_dict[message_id] = message['body']
            logging.debug(f"Сохранено значение y_true для id {message_id}")
        elif method.routing_key == 'y_pred':
            y_pred_dict[message_id] = message['body']
            logging.debug(f"Сохранено значение y_pred для id {message_id}")

        logging.debug(f"y_true_dict[message_id] {y_true_dict[message_id]}")
        logging.debug(f"y_pred_dict {y_pred_dict}")

        y_pred_value = np.random.randint(100, 301)
        y_pred_dict[message_id] = y_pred_value
        abs_err = abs(y_true_dict[message_id] - y_pred_dict[message_id])
        logging.debug(f"abs(y_true_value - y_pred_value) {abs_err}")
        write_to_csv(message_id, y_true_dict[message_id], y_pred_value, abs_err)

        # Если есть и y_true, и y_pred для одного id, считаем абсолютную ошибку
        if message_id in y_true_dict and message_id in y_pred_dict:
            y_true_value = y_true_dict[message_id]
            y_pred_value = y_pred_dict[message_id]
            absolute_error = abs(y_true_value - y_pred_value)
            logging.debug(f"Абсолютная ошибка для id {message_id}: {absolute_error}")

            # Проверка существования файла и его создание, если нужно
            if not os.path.exists(metric_log_path):
                logging.debug(f"Файл {metric_log_path} не существует, создаём новый.")

            # Проверка, если файл уже существует
            file_exists = os.path.exists(metric_log_path)

            # Записываем в CSV
            df = pd.DataFrame({
                'id': [message_id],
                'y_true': [y_true_value],
                'y_pred': [y_pred_value],
                'absolute_error': [absolute_error]
            })

            logging.debug(f"Записываем в CSV: {df.head()}")

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
        y_true_result = channel.queue_declare(queue='y_true', durable=True)
        y_pred_result = channel.queue_declare(queue='y_pred', durable=True)
        logging.debug("Очереди y_true и y_pred объявлены")
        logging.debug(f"Объявляем очереди y_true_result: {y_true_result}")
        logging.debug(f"Объявляем очереди y_pred_result: {y_pred_result}")
        # Логирование состояния очередей
        logging.debug(f"Очередь y_true объявлена: consumer_count={y_true_result.method.consumer_count}, message_count={y_true_result.method.message_count}")
        logging.debug(f"Очередь y_pred объявлена: consumer_count={y_pred_result.method.consumer_count}, message_count={y_pred_result.method.message_count}")


        # Извлекаем сообщения из очередей
        channel.basic_consume(queue='y_true', on_message_callback=callback, auto_ack=True)
        channel.basic_consume(queue='y_pred', on_message_callback=callback, auto_ack=True)

        logging.debug('Ожидание сообщений, для выхода нажмите CTRL+C')
        channel.start_consuming()
        break

    except Exception as e:
        logging.error(f"Ошибка при подключении к RabbitMQ: {e}")
        time.sleep(5)
