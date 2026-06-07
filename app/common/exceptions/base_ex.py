class RouterError(Exception):
    """Базовый класс для всех ошибок"""

    status_code: int = 400
    title: str = 'Router error'

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail

        super().__init__()
