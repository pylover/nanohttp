
import pymlconf


settings = pymlconf.DeferredConfigManager()


BUILTIN_CONFIGURATION = """
debug: true
domain:
cookie:
  http_only: false
  secure: false
json:
  indent: 4
"""


def configure(*args, **kwargs):
    settings.load(*args, builtin=BUILTIN_CONFIGURATION, **kwargs)
