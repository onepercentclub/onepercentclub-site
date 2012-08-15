# Default to local settings override, if available.
# If not, default to development settings.

try:
    from .local import *
except ImportError:
    from .development import *
