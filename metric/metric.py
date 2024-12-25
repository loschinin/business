import pika
import json
import time

# Попытка подключиться к RabbitMQ
while True:
    try:
        # Подключение к серверу RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        # Объявляем очереди
        channel.queue_declare(queue='y_true')
        channel.queue_declare(queue='y_pred')

        # Функция callback для обработки сообщений
        def callback(ch, method, properties, body):
            print(f'Из очереди {method.routing_key} получено значение {json.loads(body)}')

        # Извлекаем сообщения из очереди y_true
        channel.basic_consume(queue='y_true', on_message_callback=callback, auto_ack=True)
        # Извлекаем сообщения из очереди y_pred
        channel.basic_consume(queue='y_pred', on_message_callback=callback, auto_ack=True)

        # Запуск ожидания сообщений
        print('...Ожидание сообщений, для выхода нажмите CTRL+C')
        channel.start_consuming()
        break  # Если соединение прошло успешно, выходим из цикла
    except Exception as e:
        # Если не удалось подключиться, ждем 5 секунд и пробуем снова
        print(f'Metric: Не удалось подключиться к очереди: {e}')
        time.sleep(5)
