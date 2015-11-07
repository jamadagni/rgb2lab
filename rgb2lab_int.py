# Conversions of color values from RGB to LAB/LCH and back

from rgb2lab_check import *
from ctypes import *

def _makeFields(s):
    return tuple([(c, c_int) for c in s])

class _RGB(Structure): _fields_ = _makeFields("rgb")
class _LAB(Structure): _fields_ = _makeFields("LAB")
class _LCH(Structure): _fields_ = _makeFields("lch")

Int3Array = c_int * 3
class IntTriplet(Union):
    _anonymous_ = ["rgb", "LAB", "lch"]
    _fields_ = [("data", Int3Array),
                ("rgb", _RGB),
                ("LAB", _LAB),
                ("lch", _LCH)]
IntTripletPtr = POINTER(IntTriplet)

def _toIntTriplet(a, b, c):
    return IntTriplet(Int3Array(a, b, c))

_lib = CDLL("librgb2lab.so")

def _setSig(fn, restype, argtypes):
    if restype is not None: fn.restype = restype
    fn.argtypes = argtypes

for fn in _lib.labFromRgbInt, _lib.rgbFromLabInt, _lib.lchFromRgbInt, _lib.rgbFromLchInt, _lib.lchFromLabInt, _lib.labFromLchInt:
    _setSig(fn, IntTriplet, [IntTriplet])
for fn in _lib.labLchFromRgbInt, _lib.rgbLchFromLabInt, _lib.rgbLabFromLchInt:
    _setSig(fn, None, [IntTriplet, IntTripletPtr, IntTripletPtr])

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

if __name__ == "__main__":
    L, A, B, l, c, h = labLchFromRgbInt(99, 129, 39)
    assert (L, A, B) == (50, -25, 43)
    assert (l, c, h) == (50, 50, 120)
