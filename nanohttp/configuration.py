
import pymlconf


settings = pymlconf.DeferredConfigManager()


BUILTIN_CONFIGURATION = """
debug: true
domain:
cookie:
  http_only: false
  secure: false
"""


def configure(*args, **kwargs):
    """ Load configurations

    .. seealso:: `pymlconf Documentations <https://github.com/pylover/pymlconf#documentation>`_

    :param args: positional arguments pass into ``pymlconf.DeferredConfigManager.load``
    :param kwargs: keyword arguments pass into ``pymlconf.DeferredConfigManager.load``
    """
    settings.load(*args, builtin=BUILTIN_CONFIGURATION, **kwargs)
