try:
    from .local import *
except ImportError as e:
    import sys
    sys.exit('local.py settings file not found. Please run `prepare.sh` to create one.')
