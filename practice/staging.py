import functools
import inspect
import nanohttp


def dummy(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


class ControllerMeta(type):

    def __new__(mcs, name, parents, members):
        index = members['index']
        signature = inspect.signature(index)
        for name, parameter in signature.parameters.items():
            print(name, parameter)
        print(signature.parameters)
        new_type = type.__new__(mcs, name, parents, members)
        return new_type


class Controller(metaclass=ControllerMeta):

    @nanohttp.json
    @dummy
    def index(self, identifier: int, *, option1=None, option2: int=3):
        return {'id': identifier, 'option1': option1, 'option2': option2}


if __name__ == '__main__':
    c = Controller()
    c.index(1)
