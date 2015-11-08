# Conversions of color values from RGB to LAB/LCH and back

import rgb2lab_common
from rgb2lab_common import *
from ctypes import CDLL, c_double

_makeRetOneFn, _ = rgb2lab_common._makeConversionFns(c_double) # discarding second return item

_lib = CDLL("librgb2lab.so")

labFromRgb = _makeRetOneFn(checkRgb01, _lib.labFromRgb)
rgbFromLab = _makeRetOneFn(checkLab  , _lib.rgbFromLab)
lchFromRgb = _makeRetOneFn(checkRgb01, _lib.lchFromRgb)
rgbFromLch = _makeRetOneFn(checkLch  , _lib.rgbFromLch)
lchFromLab = _makeRetOneFn(checkLab  , _lib.lchFromLab)
labFromLch = _makeRetOneFn(checkLch  , _lib.labFromLch)
