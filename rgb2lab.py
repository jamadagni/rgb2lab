# Conversions of color values from RGB to LAB/LCH and back

from rgb2lab_check import *
from ctypes import *

def _makeFields(s):
    return tuple([(c, c_double) for c in s])

class _RGB(Structure): _fields_ = _makeFields("rgb")
class _LAB(Structure): _fields_ = _makeFields("LAB")
class _LCH(Structure): _fields_ = _makeFields("lch")

Double3Array = c_double * 3
class DoubleTriplet(Union):
    _anonymous_ = ["rgb", "LAB", "lch"]
    _fields_ = [("data", Double3Array),
                ("rgb", _RGB),
                ("LAB", _LAB),
                ("lch", _LCH)]
DoubleTripletPtr = POINTER(DoubleTriplet)

def _toDoubleTriplet(a, b, c):
    return DoubleTriplet(Double3Array(a, b, c))

_lib = CDLL("librgb2lab.so")

def _setSig(fn, restype, argtypes):
    if restype is not None: fn.restype = restype
    fn.argtypes = argtypes

for fn in _lib.labFromRgb, _lib.rgbFromLab, _lib.lchFromRgb, _lib.rgbFromLch, _lib.lchFromLab, _lib.labFromLch:
    _setSig(fn, DoubleTriplet, [DoubleTriplet])

def labFromRgb(r, g, b):
    checkRgb01(r, g, b)
    return tuple(_lib.labFromRgb(_toDoubleTriplet(r, g, b)).data)

def rgbFromLab(l, a, b):
    checkLab(l, a, b)
    return tuple(_lib.rgbFromLab(_toDoubleTriplet(l, a, b)).data)

def lchFromRgb(r, g, b):
    checkRgb01(r, g, b)
    return tuple(_lib.lchFromRgb(_toDoubleTriplet(r, g, b)).data)

def rgbFromLch(l, c, h):
    checkLch(l, c, h)
    return tuple(_lib.rgbFromLch(_toDoubleTriplet(l, c, h)).data)

def lchFromLab(l, a, b):
    checkLab(l, a, b)
    return tuple(_lib.lchFromLab(_toDoubleTriplet(l, a, b)).data)

def labFromLch(l, c, h):
    checkLch(l, c, h)
    return tuple(_lib.labFromLch(_toDoubleTriplet(l, c, h)).data)
