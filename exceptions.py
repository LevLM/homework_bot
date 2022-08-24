from telegram.error import TelegramError
from requests.exceptions import ConnectionError


class ResponseException(Exception):
    """Ошибка запроса."""

    def __init__(self):
        """Базовый супер-класс."""
        super().__init__()


class BotException(Exception):
    """Ошибки работы бота."""

    def __init__(self):
        """Базовый супер-класс."""
        super().__init__()


class TelegramErrorException(TelegramError):
    """Ошибка запроса к Telegram."""

    pass


class ApiConnectionError(ConnectionError):
    """Ошибка запроса к API."""

    pass


class ResponseApiTypeError(TypeError):
    """Ошибка ответа от API."""

    pass


class ParseKeyError(KeyError):
    """Ошибка ответа от API."""

    pass
