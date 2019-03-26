"""An (unofficial) Python wrapper around xkcd APIs"""

from xxkcd.metadata import *
from xxkcd.xkcd import xkcd, load_xkcd_cache
from xxkcd.what_if import WhatIf

__all__ = ('xkcd', 'load_xkcd_cache', 'WhatIf')
