import os
import weakref


class TempFile:
    def __init__(self, path) -> None:
        super().__init__()
        self._f = open(path, 'wb')
        weakref.finalize(self, self._remove, self._f)

    @staticmethod
    def _remove(file):
        file.close()
        os.remove(file.name)
