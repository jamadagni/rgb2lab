# librgb2lab
# ==========
# Convert color values from RGB to/from CIE LAB/LCH
# for sRGB gamut, D65 illuminant, 2° observer
#
# Copyright (C) 2015, Shriramana Sharma
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
