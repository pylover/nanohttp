
import functools


def a(arg1, arg2, kw1=None, kw2=None, *args, kw3=None, **kw):
    ttttttt = 66


@functools.wraps(a, )
def w(*args, **kwargs):
    return a(*args, **kwargs)


def describe(f):
    print(f.__name__)
    code = f.__code__
    for k in dir(code):
        if k.startswith('co_'):
            v = getattr(code, k)
            print(k, v)


def main():
    describe(a)
    describe(w)


if __name__ == '__main__':
    main()
