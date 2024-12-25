#!/bin/bash
while ! nc -z rabbitmq 5672; do
  echo "Waiting for RabbitMQ..."
  sleep 2
done
echo "RabbitMQ is up and running!"