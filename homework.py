import logging
import os
import sys
import time
from http import HTTPStatus

import exceptions
import requests
import telegram
from dotenv import load_dotenv
from requests.exceptions import ConnectionError

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

logging.basicConfig(
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    level=logging.INFO,
    filename='homework.log', filemode='w'
)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)


def send_message(bot, message):
    """Send message."""
    try:
        logger.info('Sending message')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError as error:
        raise exceptions.SendMessageException(
            f'Message sent failure, {error}'
        )


def get_api_answer(current_timestamp):
    """Get API answer."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        logger.info('Getting the API answer')
        homework_status = requests.get(
            ENDPOINT, headers=HEADERS, params=params
        )
    except ConnectionError as error:
        raise exceptions.APIResponseException(f'Error in the request {error}')
    if homework_status.status_code != HTTPStatus.OK:
        raise exceptions.APIResponseException(
            f'Код ответа API не 200 {homework_status.status_code}')
    homework = homework_status.json()
    return homework


def check_response(response):
    """Check response."""
    logger.info('Getting homeworks')
    if not isinstance(response, dict):
        raise TypeError('Response is not a dict')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Homeworks is not a list')
    return homeworks


def parse_status(homework):
    """Parse status."""
    logger.info('Getting the status of a homework')
    try:
        homework_name = homework.get('homework_name')
    except KeyError as error:
        raise KeyError(f'Failure getting "homework_name" key: {error}')
    try:
        homework_status = homework.get('status')
    except KeyError:
        raise KeyError('Unknown status')
    verdict = HOMEWORK_STATUSES[homework_status]
    if verdict is None:
        raise KeyError('Unknown verdict\'s status')
    return (
        f'Изменился статус проверки работы "{homework_name}".{verdict}'
    )


def check_tokens():
    """Check tokens."""
    return all([
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ])


def main():
    """Основная логика работы бота."""
    logger.debug('Spectacular appearance')
    status_upd = ''
    error_message = ''

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        if not check_tokens():
            logger.critical('Token error')
            sys.exit('Token error')
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date', current_timestamp)
            homeworks = check_response(response)
            hw_status = homeworks[0].get('status')
            if hw_status != status_upd and hw_status is not None:
                status_upd = homeworks
                send_message(bot, parse_status(hw_status[0]))
                logger.debug('Brace yourself: updates are coming')
        except exceptions.BotRunningException as error:
            logger.error(f'Failure while getting the answer {error}')
        except Exception as error:
            logger.error(error)
            message = f'Programm failure: {error}'
            if message != error_message:
                error_message = message
                send_message(bot, message)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
