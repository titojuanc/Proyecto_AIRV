"""Asyncio interface to the Pulseaudio and Pipewire pulse library."""

import sys

__version__ = '0.7'
MIN_PYTHON_VERSION = (3, 8)

_version = sys.version_info[:2]
if _version < MIN_PYTHON_VERSION:
    print(f'error: the python version must be at least'
          f' {MIN_PYTHON_VERSION}', file=sys.stderr)
    sys.exit(1)
