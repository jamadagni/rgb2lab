# Valid values are integers in [0, 255] for r, g, b and l; [0, 360) for h; [0, 180] for s

import rgb2lab
from rgb2lab import *

def _checkAndScaleRgb(r, g, b):
    for v in r, g, b:
        if not (0 <= v <= 255):
            raise Rgb2LabError("RGB values should be in the range [0, 255].")
    return tuple(v / 255 for v in (r, g, b))

# if below forwards don't exist, then items starting with _ are
# not accessed from other module since they are considered private
_checkLab = rgb2lab._checkLab
_checkLch = rgb2lab._checkLch

def _round(seq):
    return tuple(round(v) for v in seq)

def _roundAndFixRgb(rgb):
    return tuple((-1 if (v < 0 or v > 255) else v) for v in (round(v * 255) for v in rgb))

def _fixLch(lch):
    l, c, h = lch # can't assign to a tuple; will make a new one
    if c == 0: h = -1 # sometimes c may become 0 by rounding, so need to do this again here
    return l, c, h

def labFromRgbInt(r, g, b):
    r, g, b = _checkAndScaleRgb(r, g, b)
    return _round(labFromRgb(r, g, b))

def rgbFromLabInt(l, a, b):
    _checkLab(l, a, b)
    return _roundAndFixRgb(rgbFromLab(l, a, b))

def lchFromRgbInt(r, g, b):
    r, g, b = _checkAndScaleRgb(r, g, b)
    return _fixLch(_round(lchFromRgb(r, g, b)))

def rgbFromLchInt(l, c, h):
    _checkLch(l, c, h)
    return _roundAndFixRgb(rgbFromLch(l, c, h))

def lchFromLabInt(l, a, b):
    _checkLab(l, a, b)
    return _fixLch(_round(lchFromLab(l, a, b)))

def labFromLchInt(l, c, h):
    _checkLch(l, c, h)
    return _round(labFromLch(l, c, h))

def labLchFromRgbInt(r, g, b):
    r, g, b = _checkAndScaleRgb(r, g, b)
    l, a, b = labFromRgb(r, g, b)
    return _round((l, a, b)) + _fixLch(_round(lchFromLab(l, a, b)))

def rgbLchFromLabInt(l, a, b):
    _checkLab(l, a, b)
    return _roundAndFixRgb(rgbFromLch(l, a, b)) + _fixLch(_round(lchFromLab(l, a, b)))

def rgbLabFromLchInt(l, c, h):
    _checkLch(l, c, h)
    l, a, b = labFromLch(l, c, h)
    return _roundAndFixRgb(rgbFromLab(l, a, b)) + _round((l, a, b))
