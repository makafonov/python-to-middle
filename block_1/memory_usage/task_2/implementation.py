import weakref


class MyObject:

    def __init__(self, name) -> None:
        super().__init__()
        self.name = name


def cache(func):
    def inner(name):
        if name not in _cache:
            _cache[name] = _tmp = func(name)
        return _cache[name]
    return inner


@cache
def create_object(name):
    return MyObject(name)


_cache = weakref.WeakValueDictionary()
create_object._cache = _cache
