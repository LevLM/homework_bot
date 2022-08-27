class SendingError(Exception):
    """Базовый класс для ошибок Бота."""

    pass


class NotSendingError(Exception):
    """Базовый класс для прочих ошибок."""

    pass


class ResponseException(NotSendingError):
    """Ошибка запроса."""

    pass


class BotException(SendingError):
    """Ошибки работы бота."""

    pass


class ResponseApiTypeError(TypeError, NotSendingError):
    """Ошибка ответа от API."""

    pass


class ParseKeyError(KeyError, NotSendingError):
    """Ошибка ответа от API."""

    pass
