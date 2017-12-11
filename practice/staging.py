import json as js
import functools
import inspect
import nanohttp


class ControllerMeta(type):

    def __new__(mcs, name, parents, members):
        index = members['index']
        signature = inspect.signature(index)
        print(index.__http_methods__)
        print(signature.parameters)
        return type.__new__(mcs, name, parents, members)


def json(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return js.dumps(result)
    return wrapper


class Controller(metaclass=ControllerMeta):

    @nanohttp.json
    @json
    def index(self, identifier: int):
        return {'id': identifier}


if __name__ == '__main__':
    c = Controller()
    c.index(1)
