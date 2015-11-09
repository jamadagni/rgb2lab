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
from ctypes import *

_makeRetOneFn, _makeRetTwoFn = rgb2lab_common._makeConversionFns(c_int)

_lib = CDLL("librgb2lab.so")

labFromRgbInt = _makeRetOneFn(checkRgb256, _lib.labFromRgbInt)
rgbFromLabInt = _makeRetOneFn(checkLab   , _lib.rgbFromLabInt)
lchFromRgbInt = _makeRetOneFn(checkRgb256, _lib.lchFromRgbInt)
rgbFromLchInt = _makeRetOneFn(checkLch   , _lib.rgbFromLchInt)
lchFromLabInt = _makeRetOneFn(checkLab   , _lib.lchFromLabInt)
labFromLchInt = _makeRetOneFn(checkLch   , _lib.labFromLchInt)

labLchFromRgbInt = _makeRetTwoFn(checkRgb256, _lib.labLchFromRgbInt)
rgbLchFromLabInt = _makeRetTwoFn(checkLab   , _lib.rgbLchFromLabInt)
rgbLabFromLchInt = _makeRetTwoFn(checkLch   , _lib.rgbLabFromLchInt)

def _makeMakeTableFn(fillTableFn, var1Span, var2Span):
    class TinyRgb(Structure):
        _fields_ = tuple((f, c_ubyte) for f in ("valid", "r", "g", "b"))
    TinyRgbTable = TinyRgb * var2Span * var1Span
    # NOTE: order of multiplying type by dimension sizes above is opposite to declaring array in C
    fillTableFn.argtypes = [TinyRgbTable, c_int]
    fillTableFn.restype = c_int # number of validRGBs found
    def fn(v):
        table = TinyRgbTable()
        table.inGamutCount = fillTableFn(table, v)
        if table.inGamutCount == -1:
            raise ValueError("Bad value {} provided for function {}".format(v, fillTableFn))
        return table
    return fn

makeTableL_AB = _makeMakeTableFn(_lib.fillTableL_AB, 257, 257)
makeTableA_BL = _makeMakeTableFn(_lib.fillTableA_BL, 257, 101)
makeTableB_AL = _makeMakeTableFn(_lib.fillTableB_AL, 257, 101)
makeTableL_HC = _makeMakeTableFn(_lib.fillTableL_HC, 360, 181)
makeTableC_HL = _makeMakeTableFn(_lib.fillTableC_HL, 360, 101)
makeTableH_CL = _makeMakeTableFn(_lib.fillTableH_CL, 181, 101)
