#!/bin/bash
set -e
host="rabbitmq"
shift
until nc -z "$host" 5672; do
  >&2 echo "RabbitMQ is unavailable - sleeping"
  sleep 1
done
>&2 echo "RabbitMQ is up - executing command"
exec "$@"