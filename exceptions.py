class ResponseException(Exception):
    """Ошибка запроса."""

    pass


class BotException(Exception):
    """Ошибки работы бота."""

    pass


class ResponseApiTypeError(TypeError):
    """Ошибка ответа от API."""

    pass


class ParseKeyError(KeyError):
    """Ошибка ответа от API."""

    pass
