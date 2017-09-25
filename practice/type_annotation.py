
import functools


def a(arg1, arg2, kw1=None, kw2=None, *args, kw3=None, **kw):
    ttttttt = 66


@functools.wraps(a, )
def w(*args, **kwargs):
    return a(*args, **kwargs)


def ann(a: int):
    pass


def describe(f):
    print(f.__name__)
    # code = f.__code__
    # for k in dir(code):
    #     if k.startswith('co_'):
    #         v = getattr(code, k)
    #         print(k, v)
    print('__annotations__', f.__annotations__)


def main():
    describe(a)
    describe(w)
    describe(ann)


if __name__ == '__main__':
    main()
