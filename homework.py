import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# Укажем proxy, чтобы телеграм не болел
proxy = telegram.utils.request.Request(proxy_url='https://103.58.74.2:8080')


def parse_homework_status(homework):
    # Получим имя домашней работы
    homework_name = homework['homework_name']
    # Проверим статус. Определим, какое сообщение отправлять
    if homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    # В параметры запишем дату для отсчета
    params = {
        'from_date': current_timestamp
    }
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    response = requests.get('https://praktikum.yandex.ru/api/user_api/homework_statuses/', headers=headers, params=params)
    homework_statuses = response
    return homework_statuses.json()


def send_message(message):
    chat_id = os.getenv('CHAT_ID')
    bot = telegram.Bot(token=TELEGRAM_TOKEN, request=proxy)
    return bot.send_message(chat_id = chat_id, text = message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(1200)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()

