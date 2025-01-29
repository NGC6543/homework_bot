import logging
import os
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import EnvironmentVariablesIsEmpty, EmptyHomeworks

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d'
)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка на наличие данных в переменных окружения."""
    if (PRACTICUM_TOKEN is None
            or TELEGRAM_TOKEN is None or TELEGRAM_CHAT_ID is None):
        logging.critical('Отсутствуют переменные окружения.')
        raise EnvironmentVariablesIsEmpty


def send_message(bot, message):
    """Отправка сообщения пользователю."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text=message)
    except Exception as error:
        logging.error(f'Сбой при отправке сообщения. Ошибка: {error}')
        bot.send_message(TELEGRAM_CHAT_ID, text=f'Возникла ошибка {error}')
    else:
        logging.debug('Успешная отправка сообщения.')


def get_api_answer(timestamp):
    """Запрос к API и получение данных."""
    try:
        payload = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException as error:
        logging.error(f'Запрос недоступен. Ошибка: {error}')
    else:
        if response.status_code == HTTPStatus.OK:
            return response.json()
        else:
            logging.error(
                f'Неожиданный статус запроса: {response.status_code}'
            )
            raise requests.RequestException


def check_response(response):
    """Проверка ответа запроса."""
    if not isinstance(response, dict):
        raise TypeError
    get_homework = response.get('homeworks')
    if get_homework is None:
        logging.error('Запрошенный ключ неверен.')
        raise EmptyHomeworks
    if not isinstance(get_homework, list):
        raise TypeError
    if len(get_homework) == 0:
        logging.debug('Пустой список.')
        raise IndexError


def parse_status(homework):
    """Извлечение данных о домашней работе."""
    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_VERDICTS.get((homework.get('status')))
    if verdict is None or homework_name is None:
        logging.error('Неожиданный статус домашней работы.')
        raise TypeError
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()

    # Создаем объект класса бота
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            homework = response.get('homeworks')[0]
            message = parse_status(homework)
            send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.critical(message, exc_info=True)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
