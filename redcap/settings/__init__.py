try:
    from .local import *
except ImportError:
    from .settings import *