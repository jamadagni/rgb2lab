"""
Conversions of color values from RGB to LAB/LCH and back

These functions are based on:
    http://www.brucelindbloom.com/Math.html
and the pages linked to therefrom, especially:
    http://www.brucelindbloom.com/Eqn_RGB_XYZ_Matrix.html
    http://www.brucelindbloom.com/Eqn_XYZ_to_RGB.html
    http://www.brucelindbloom.com/Eqn_RGB_to_XYZ.html
    http://www.brucelindbloom.com/Eqn_XYZ_to_Lab.html
    http://www.brucelindbloom.com/Eqn_Lab_to_XYZ.html
    http://www.brucelindbloom.com/Eqn_Lab_to_LCH.html
    http://www.brucelindbloom.com/Eqn_LCH_to_Lab.html
"""

# Note that:
#     R, G and B are linear w.r.t. device output
#     X, Y and Z are linear w.r.t. energy
#     L, a and b are linear w.r.t. perception

class Rgb2LabError(RuntimeError): pass # separate class for identification

def _checkRgb(r, g, b):
    for v in r, g, b:
        if not (0 <= v <= 1):
            raise Rgb2LabError("RGB values should be in the range [0, 1].")

def _checkLab(l, a, b):
    if not (0 <= l <= 100 and -128 <= a <= 128 and -128 <= b <= 128):
        raise Rgb2LabError("L, A and B values should be in the ranges [0, 100], [-128, +128] and [-128, +128] respectively.")

def _checkLch(l, c, h):
    if not (0 <= l <= 100 and ((0 <= c <= 180 and 0 <= h < 360) or (c == 0 and h == -1))):
        raise Rgb2LabError("L, C and H values should be in the ranges [0, 100], [0, 180] and [0, 360) respectively. H may be -1 only if C is 0.")

def _xyzFromRgb(r, g, b):
    # Convert RGB values of a color in the sRGB color space to CIE XYZ values
    # Nominal range of the components for both input and output values is [0, 1]
    r, g, b = (((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in (r, g, b))
    return [
        r * 0.4124564 + g * 0.3575761 + b * 0.1804375,
        r * 0.2126729 + g * 0.7151522 + b * 0.0721750,
        r * 0.0193339 + g * 0.1191920 + b * 0.9503041
        ]
        # NOTE: coefficients above only appropriate for D65 illuminant and sRGB color space

def _rgbFromXyz(x, y, z):
    # Convert CIE XYZ values of a color to RGB values in the sRGB color space
    # Nominal range of the components for both input and output values is [0, 1]
    r = x *  3.2404542 + y * -1.5371385 + z * -0.4985314
    g = x * -0.9692660 + y *  1.8760108 + z *  0.0415560
    b = x *  0.0556434 + y * -0.2040259 + z *  1.0572252
    # NOTE: coefficients above only appropriate for D65 illuminant and sRGB color space
    return list(1.055 * v ** (1 / 2.4) - 0.055 if v > 0.0031308 else v * 12.92 for v in (r, g, b))

_eps = (6 / 29.0) ** 3; _kap = (29 / 3.0) ** 3

# NOTE: only appropriate for D65 illuminant and 2° observer
_xRef = 0.95047 ; _yRef = 1.0 ; _zRef = 1.08883

def _labFromXyz(x, y, z):
    # Convert CIE XYZ values of a color to CIE Lab values assuming D65 illuminant and 2° observer
    # The nominal ranges are as follows:
    #     1) Input: [0, 1] for each component
    #     2) Output: 0 to 100 for `L`; ±128 for `a` and `b`
    x /= _xRef ; y /= _yRef ; z /= _zRef
    x, y, z = (v ** (1 / 3.0) if v > _eps else (_kap * v + 16) / 116.0 for v in (x, y, z))
    return [(116 * y) - 16, 500 * (x - y), 200 * (y - z)]

def _xyzFromLab(l, a, b):
    # Convert CIE Lab values of a color to CIE XYZ values assuming D65 illuminant and 2° observer
    # The nominal ranges are as follows:
    #     1) Input: 0 to 100 for `L`; ±128 for `a` and `b`
    #     2) Output: [0, 1] for each component
    y = (l + 16) / 116.0 ; x = a / 500 + y ; z = y - b / 200
    x, y, z = (v ** 3 if v ** 3 > _eps else ((116 * v - 16) / _kap) for v in (x, y, z))
    return x * _xRef, y * _yRef, z * _zRef

def labFromRgb(r, g, b):
    """
    Convert RGB values of a color in the sRGB gamut to CIE Lab values
    assuming D65 illuminant and 2° observer

    The nominal ranges are as follows:
        1) Input: [0, 1] for each component
        2) Output: 0 to 100 for `L`; ±128 for `a` and `b`
    """
    _checkRgb(r, g, b)
    return _labFromXyz(*_xyzFromRgb(r, g, b))

def rgbFromLab(l, a, b):
    """
    Convert CIE Lab values of a color to RGB values in the sRGB gamut
    assuming D65 illuminant and 2° observer

    The nominal ranges are as follows:
        1) Input: 0 to 100 for `L`; ±128 for `a` and `b`
        2) Output: [0, 1] for each component
    """
    _checkLab(l, a, b)
    return _rgbFromXyz(*_xyzFromLab(l, a, b))

from math import hypot, degrees, atan2
def lchFromLab(l, a, b):
    """
    Convert CIE Lab values of a color to CIE LCH(ab) values

    The nominal ranges are as follows:
        1) Input: 0 to 100 for `L`; ±128 for `a` and `b`
        2) Output: 0 to 100 for `L`; 0 to 128√2 for `C` and 0 to 360° for `h`
    Note: `L` is unchanged
    """
    _checkLab(l, a, b)
    if a == 0 and b == 0: return l, 0, -1
    else: return l, hypot(a, b), (degrees(atan2(b, a)) % 360) # %360 needed since atan2 outputs in ±π

from math import radians, sin, cos
def labFromLch(l, c, h):
    """
    Convert CIE LCH(ab) values of a color to CIE Lab values

    The nominal ranges are as follows:
        1) Input: 0 to 100 for `L`; 0 to 128√2 for `C` and 0 to 360° for `h`
        2) Output: 0 to 100 for `L`; ±128 for `a` and `b`
    Note: `L` is unchanged
    """
    _checkLch(l, c, h)
    if h == -1: h = 0
    else: h = radians(h)
    return l, c * cos(h), c * sin(h)

def lchFromRgb(r, g, b):
    """Convenience function; see lchFromLab and labFromRgb"""
    _checkRgb(r, g, b)
    return lchFromLab(*labFromRgb(r, g, b))

def rgbFromLch(l, c, h):
    """Convenience function; see rgbFromLab and labFromLch"""
    _checkLch(l, c, h)
    return rgbFromLab(*labFromLch(l, c, h))
