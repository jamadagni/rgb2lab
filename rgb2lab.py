# librgb2lab
# ==========
#
# Convert color values from RGB to/from CIE LAB/LCH
# for sRGB gamut, D65 illuminant, 2° observer
#
# Copyright (C) 2015, Shriramana Sharma, samjnaa-at-gmail-dot-com
#
# Use, modification and distribution are permitted subject to the
# "BSD-2-Clause"-type license stated in the accompanying file LICENSE.txt

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
