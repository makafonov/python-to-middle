import contextlib


class TempFile:
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        return contextlib.closing(instance)

    def __init__(self, path) -> None:
        super().__init__()
        self._f = open(path, 'wb')

    def close(self):
        self._f.close()
