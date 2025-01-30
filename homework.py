import logging
import os
import time
import sys
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import EnvironmentVariablesIsEmpty, KeyHomeworksAbsence

load_dotenv()


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
    """Проверка на наличие переменных окружения."""
    tokens = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')
    missing_tokens = [token for token in tokens if not globals()[token]]
    if missing_tokens:
        missing_tokens_to_str = ', '.join(missing_tokens)
        logging.critical(
            f'Отсутствуют переменные окружения: {missing_tokens_to_str}'
        )
        raise EnvironmentVariablesIsEmpty(
            f'Отсутствуют переменные окружения: {missing_tokens_to_str}'
        )


def send_message(bot, message):
    """Отправка сообщения пользователю."""
    logging.info(f'Отправка сообщения: {message}')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text=message)
    except (telebot.apihelper.ApiException,
            requests.RequestException) as error:
        logging.error(f'Сбой при отправке сообщения. Ошибка: {error}')
    else:
        logging.debug('Успешная отправка сообщения.')


def get_api_answer(timestamp):
    """Запрос к API и получение данных."""
    payload = {'from_date': timestamp}
    logging.info(
        'Начало запроса к {} с параметрами from_date: {}'.format(
            ENDPOINT, payload.get('from_date')
        )
    )
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException as error:
        raise ConnectionError(
            f'При подключении к {ENDPOINT} с параметрами from_date: ',
            f'{payload['from_date']} возникла ошибка: {error}')
    else:
        if response.status_code != HTTPStatus.OK:
            raise ValueError('Неожиданный статус запроса: ',
                             f'{response.status_code} - {response.reason}')
        return response.json()


def check_response(response):
    """Функция для проверки ответа запроса."""
    logging.info('Начало проверки ответа сервера.')
    if not isinstance(response, dict):
        raise TypeError('Неверный тип данных запроса. Должен быть словарь.')
    if 'homeworks' not in response:
        raise KeyHomeworksAbsence('Ключ homeworks отсутствует.')
    get_homeworks = response.get('homeworks')
    if not isinstance(get_homeworks, list):
        raise TypeError('Тип данных ключа homeworks должен быть списком.')
    if not get_homeworks:
        logging.debug('Пустой список.')
    logging.info('Проверка успешно пройдена.')


def parse_status(homework):
    """Функция для извлечения данных о домашней работе."""
    logging.info('Начало извелечения данных о домашней работе.')
    if 'homework_name' not in homework:
        raise KeyHomeworksAbsence(
            'Ключ homework_name в словаре homeworks отсутствует.'
        )
    if 'status' not in homework:
        raise KeyHomeworksAbsence(
            'Ключ status в словаре homeworks отсутствует.'
        )
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise KeyHomeworksAbsence(
            f'Ключ {status} в словаре HOMEWORK_VERDICTS отсутствует.'
        )
    verdict = HOMEWORK_VERDICTS.get(status)
    if verdict is None:
        raise ValueError(f'Отсутствует значение {status}',
                         'в словаре HOMEWORK_VERDICTS.')
    logging.info('Успешное извлечение данных о домашней работе.')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()

    # Создаем объект класса бота
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_message = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            homework = response.get('homeworks')
            if homework:
                message = parse_status(homework[0])
                send_message(bot, message)
            timestamp = response.get('current_date')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message, exc_info=True)
            if message != last_message:
                send_message(bot, message)
            last_message = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[logging.StreamHandler(sys.stdout)],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
