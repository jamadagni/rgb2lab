# librgb2lab
# ==========
#
# Convert color values from RGB to/from CIE LAB/LCH
# for sRGB gamut, D65 illuminant, 2° observer
#
# Copyright (C) 2019, Shriramana Sharma, samjnaa-at-gmail-dot-com
#
# Use, modification and distribution are permitted subject to the
# "BSD-2-Clause"-type license stated in the accompanying file LICENSE.txt


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

def _makeMake1DTableFn(fillTableFn, varSpan):
    class TinyRgb(Structure):
        _fields_ = tuple((f, c_ubyte) for f in ("valid", "r", "g", "b"))
    TinyRgbTable = TinyRgb * varSpan
    fillTableFn.argtypes = [TinyRgbTable, c_int, c_int]
    fillTableFn.restype = c_int # number of validRGBs found
    def fn(var1, var2):
        table = TinyRgbTable()
        table.inGamutCount = fillTableFn(table, var1, var2)
        if table.inGamutCount == -1:
            raise ValueError("Bad values {},{} provided for function {}".format(var1, var2, fillTableFn))
        return table
    return fn

makeTable_LforAB = _makeMake1DTableFn(_lib.fillTable_LforAB, 101)
makeTable_AforBL = _makeMake1DTableFn(_lib.fillTable_AforBL, 257)
makeTable_BforAL = _makeMake1DTableFn(_lib.fillTable_BforAL, 257)
makeTable_LforHC = _makeMake1DTableFn(_lib.fillTable_LforHC, 101)
makeTable_CforHL = _makeMake1DTableFn(_lib.fillTable_CforHL, 181)
makeTable_HforCL = _makeMake1DTableFn(_lib.fillTable_HforCL, 360)

def _makeMake2DTableFn(fillTableFn, var1Span, var2Span):
    class TinyRgb(Structure):
        _fields_ = tuple((f, c_ubyte) for f in ("valid", "r", "g", "b"))
    TinyRgbTable = TinyRgb * var2Span * var1Span
    # NOTE: order of multiplying type by dimension sizes above is opposite to declaring array in C
    fillTableFn.argtypes = [TinyRgbTable, c_int]
    fillTableFn.restype = c_int # number of validRGBs found
    def fn(var):
        table = TinyRgbTable()
        table.inGamutCount = fillTableFn(table, var)
        if table.inGamutCount == -1:
            raise ValueError("Bad value {} provided for function {}".format(var, fillTableFn))
        return table
    return fn

makeTable_ABforL = _makeMake2DTableFn(_lib.fillTable_ABforL, 257, 257)
makeTable_BLforA = _makeMake2DTableFn(_lib.fillTable_BLforA, 257, 101)
makeTable_ALforB = _makeMake2DTableFn(_lib.fillTable_ALforB, 257, 101)
makeTable_HCforL = _makeMake2DTableFn(_lib.fillTable_HCforL, 360, 181)
makeTable_HLforC = _makeMake2DTableFn(_lib.fillTable_HLforC, 360, 101)
makeTable_CLforH = _makeMake2DTableFn(_lib.fillTable_CLforH, 181, 101)
