class RouterError(Exception):
    title: str
    status_code: int

    def __init__(self, details: str | None) -> None:
        self._details = details
