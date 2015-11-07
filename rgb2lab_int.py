# Conversions of color values from RGB to LAB/LCH and back

from rgb2lab_check import *
from ctypes import *

#
# preliminaries
#

def _makeFields(s): return tuple([(f, c_int) for f in s])
class _RGB(Structure): _fields_ = _makeFields("rgb")
class _LAB(Structure): _fields_ = _makeFields("LAB")
class _LCH(Structure): _fields_ = _makeFields("lch")

# main types used
Int3Array = c_int * 3
class IntTriplet(Union):
    _anonymous_ = ["rgb", "LAB", "lch"]
    _fields_ = [("data", Int3Array),
                ("rgb", _RGB),
                ("LAB", _LAB),
                ("lch", _LCH)]
IntTripletPtr = POINTER(IntTriplet)
class TinyRgb(Structure):
    _fields_ = tuple((f, c_ubyte) for f in ("valid", "r", "g", "b"))

def _toIntTriplet(a, b, c): return IntTriplet(Int3Array(a, b, c))

_lib = CDLL("librgb2lab.so")

#
# main functions
#

for fn in _lib.labFromRgbInt, _lib.rgbFromLabInt, _lib.lchFromRgbInt, _lib.rgbFromLchInt, _lib.lchFromLabInt, _lib.labFromLchInt:
    fn.argtypes = [IntTriplet]
    fn.restype = IntTriplet

def labFromRgbInt(r, g, b):
    checkRgb256(r, g, b)
    return tuple(_lib.labFromRgbInt(_toIntTriplet(r, g, b)).data)

def rgbFromLabInt(l, a, b):
    checkLab(l, a, b)
    return tuple(_lib.rgbFromLabInt(_toIntTriplet(l, a, b)).data)

def lchFromRgbInt(r, g, b):
    checkRgb256(r, g, b)
    return tuple(_lib.lchFromRgbInt(_toIntTriplet(r, g, b)).data)

def rgbFromLchInt(l, c, h):
    checkLch(l, c, h)
    return tuple(_lib.rgbFromLchInt(_toIntTriplet(l, c, h)).data)

def lchFromLabInt(l, a, b):
    checkLab(l, a, b)
    return tuple(_lib.lchFromLabInt(_toIntTriplet(l, a, b)).data)

def labFromLchInt(l, c, h):
    checkLch(l, c, h)
    return tuple(_lib.labFromLchInt(_toIntTriplet(l, c, h)).data)

#
# convenience functions to maintain interim calculation accuracy in floating point
#

for fn in _lib.labLchFromRgbInt, _lib.rgbLchFromLabInt, _lib.rgbLabFromLchInt:
    fn.argtypes = [IntTriplet, IntTripletPtr, IntTripletPtr]

def labLchFromRgbInt(r, g, b):
    checkRgb256(r, g, b)
    lab = IntTriplet(); lch = IntTriplet()
    _lib.labLchFromRgbInt(_toIntTriplet(r, g, b), byref(lab), byref(lch))
    return tuple(lab.data) + tuple(lch.data)

def rgbLchFromLabInt(l, a, b):
    checkLab(l, a, b)
    rgb = IntTriplet(); lch = IntTriplet()
    _lib.rgbLchFromLabInt(_toIntTriplet(l, a, b), byref(rgb), byref(lch))
    return tuple(rgb.data) + tuple(lch.data)

def rgbLabFromLchInt(l, c, h):
    checkLch(l, c, h)
    rgb = IntTriplet(); lab = IntTriplet()
    _lib.rgbLabFromLchInt(_toIntTriplet(l, c, h), byref(rgb), byref(lab))
    return tuple(rgb.data) + tuple(lab.data)

#
# fillTable functions
#

# NOTE: Order of multiplying type by dimensions below is opposite to declaring array in C

TinyRgb_257_257 = TinyRgb * 257 * 257
_lib.fillTableL_ab.argtypes = [TinyRgb_257_257, c_int]
def makeTableL_ab(l):
    arr = TinyRgb_257_257()
    _lib.fillTableL_ab(arr, l)
    return arr

TinyRgb_101_257 = TinyRgb * 257 * 101
_lib.fillTableA.argtypes = [TinyRgb_101_257, c_int]
def makeTableA(a):
    arr = TinyRgb_101_257()
    _lib.fillTableA(arr, a)
    return arr

TinyRgb_101_257 = TinyRgb * 257 * 101
_lib.fillTableB.argtypes = [TinyRgb_101_257, c_int]
def makeTableB(b):
    arr = TinyRgb_101_257()
    _lib.fillTableB(arr, b)
    return arr

TinyRgb_181_360 = TinyRgb * 360 * 181
_lib.fillTableL_ch.argtypes = [TinyRgb_181_360, c_int]
def makeTableL_ch(l):
    arr = TinyRgb_181_360()
    _lib.fillTableL_ch(arr, l)
    return arr

TinyRgb_101_360 = TinyRgb * 360 * 101
_lib.fillTableC.argtypes = [TinyRgb_101_360, c_int]
def makeTableC(c):
    arr = TinyRgb_101_360()
    _lib.fillTableC(arr, c)
    return arr

TinyRgb_101_181 = TinyRgb * 181 * 101
_lib.fillTableH.argtypes = [TinyRgb_101_181, c_int]
def makeTableH(h):
    arr = TinyRgb_101_181()
    _lib.fillTableH(arr, h)
    return arr

if __name__ == "__main__":
    L, A, B, l, c, h = labLchFromRgbInt(99, 129, 39)
    assert (L, A, B) == (50, -25, 43)
    assert (l, c, h) == (50, 50, 120)
