import pandas as pd
import matplotlib.pyplot as plt
import time

# Путь к файлу лога
metric_log_path = './logs/metric_log.csv'

while True:
    # Чтение данных из CSV
    df = pd.read_csv(metric_log_path)

    # Построение гистограммы
    plt.figure(figsize=(10, 6))
    plt.hist(df['absolute_error'], bins=30, color='skyblue', edgecolor='black')
    plt.title('Распределение абсолютных ошибок')
    plt.xlabel('Абсолютная ошибка')
    plt.ylabel('Частота')

    # Сохранение графика
    plt.savefig('./logs/error_distribution.png')
    plt.close()

    # Задержка для обновления графика
    time.sleep(10)
