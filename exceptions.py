class SendingError(Exception):
    """Base class for Bot errors."""

    pass


class NotSendingError(Exception):
    """Base class for Other errors."""

    pass


class ResponseException(NotSendingError):
    """Ошибка запроса."""

    pass


class BotException(SendingError):
    """Ошибки работы бота."""

    pass


class ResponseApiTypeError(TypeError):
    """Ошибка ответа от API."""

    pass


class ParseKeyError(KeyError):
    """Ошибка ответа от API."""

    pass
