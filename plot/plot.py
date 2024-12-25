import pandas as pd
import matplotlib.pyplot as plt
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Путь к файлу лога
metric_log_path = './logs/metric_log.csv'

# Функция для чтения первых 5 строк из CSV
def read_first_5_lines():
    try:
        df = pd.read_csv(metric_log_path)
        logging.debug("Первые 5 строк из metric_log.csv:")
        logging.debug(df.head())  # Вывод первых 5 строк
    except Exception as e:
        logging.error(f"Ошибка при чтении metric_log.csv: {e}")

while True:
    try:
        logging.debug("Чтение данных из metric_log.csv")
        # Чтение данных из CSV
        df = pd.read_csv(metric_log_path)

        # Выводим первые 5 строк
        read_first_5_lines()

        # Построение гистограммы
        plt.figure(figsize=(10, 6))
        plt.hist(df['absolute_error'], bins=30, color='skyblue', edgecolor='black')
        plt.title('Распределение абсолютных ошибок')
        plt.xlabel('Абсолютная ошибка')
        plt.ylabel('Частота')

        # Сохранение графика
        plt.savefig('./logs/error_distribution.png')
        logging.debug("График сохранён в logs/error_distribution.png")
        plt.close()

        # Задержка для обновления графика
        time.sleep(10)

    except Exception as e:
        logging.error(f"Ошибка при построении графика: {e}")
        time.sleep(5)  # Повторить попытку через 5 секунд
