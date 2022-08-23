class ResponseException(Exception):
    """Errors in responses."""

    pass


class BotRunningException(Exception):
    """Errors in Bot's running."""

    pass


class APIResponseException(ResponseException):
    """An incorrect API response."""

    pass


class SendMessageException(BotRunningException):
    """Error while sending message."""

    pass
