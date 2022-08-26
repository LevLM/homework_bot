import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)


def send_message(bot, message):
    """Отправка сообщения со статусом в Telegram чат."""
    try:
        logger.info('Sending message to Telegram chat')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError as error:
        raise exceptions.SendingError(
            f'Sending message failure: {error}'
        )


def get_api_answer(current_timestamp):
    """Запрос к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        logger.info('Getting API answer')
        homework_status = requests.get(
            ENDPOINT, headers=HEADERS, params=params
        )
    except ConnectionError as error:
        raise exceptions.NotSendingError(
            f'Getting API answer failure: {error}'
        )
    if homework_status.status_code != HTTPStatus.OK:
        raise exceptions.NotSendingError(
            f'API answer is not 200: {homework_status.status_code}')
    homework = homework_status.json()
    return homework


def check_response(response):
    """Проверяка ответа API на корректность."""
    logger.info('Checking response')
    if not isinstance(response, dict):
        raise exceptions.ResponseApiTypeError(
            'Ответ API не является типом данных "Словарь"'
        )
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise exceptions.ResponseApiTypeError(
            'Ошибка преобразования ответа API в тип данных Python "Список"'
        )
    return homeworks


def parse_status(homework):
    """Извлечение статус домашней работы."""
    logger.info('Parsing status of homework')
    try:
        homework_name = homework['homework_name']
    except exceptions.ParseKeyError as error:
        raise exceptions.ParseKeyError(
            f'Parsing key "homework_name" failure: {error}'
        )
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    if verdict is None:
        raise exceptions.ParseKeyError('Unknown homework status')
    return (
        f'Изменился статус проверки работы "{homework_name}".{verdict}'
    )


def check_tokens():
    """Проверка наличия переменных окружения."""
    return all([
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ])


def main():
    """Основная логика работы программы."""
    status_upd = {'name': '', 'state': ''}
    homework_status = {'name': '', 'state': ''}
    error_message = ''
    if not check_tokens():
        logger.critical('Checking tokens error')
        sys.exit('Checking tokens erro')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time() - 300000)

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)[0]
            message = parse_status(homeworks)
            current_timestamp = response.get('current_date')
            homework_status[response.get('homework_name')] = response.get(
                'status')
            if homework_status != status_upd and homework_status is not None:
                status_upd = homework_status
                send_message(bot, message)
            else:
                logger.debug('There is not update status')
        except exceptions.NotSendingError as error:
            logger.error(error)
            message = f'Main code: {error}'
            if message != error_message:
                send_message(bot, message)
                error_message = message
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
        level=logging.INFO,
        filename='homework.log', filemode='w'
    )
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.debug('Working of main code')
    main()
