
from pymlconf import DeferredRoot


settings = DeferredRoot()


BUILTIN_CONFIGURATION = """
debug: true
domain:
cookie:
  http_only: false
  secure: false
"""


def configure(*args, **kwargs):
    """Load configurations

    .. seealso:: `pymlconf Documentations
                 <https://github.com/pylover/pymlconf#documentation>`_

    :param args: positional arguments pass into
                 ``pymlconf.DeferredRoot.load``
    :param kwargs: keyword arguments pass into
                   ``pymlconf.DeferredRoot.load``
    """

    settings.initialize(BUILTIN_CONFIGURATION, **kwargs)
    for a in args:
        settings.merge(a)


