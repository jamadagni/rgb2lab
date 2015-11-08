from ctypes import *

class Rgb2LabError(RuntimeError): pass # separate class for identification

def checkRgb01(r, g, b):
    for v in r, g, b:
        if not (0 <= v <= 1):
            raise Rgb2LabError("RGB values should be in the range [0, 1].")

def checkRgb256(r, g, b):
    for v in r, g, b:
        if not (0 <= v <= 255):
            raise Rgb2LabError("RGB values should be in the range [0, 255].")

def checkLab(l, a, b):
    if not (0 <= l <= 100 and -128 <= a <= 128 and -128 <= b <= 128):
        raise Rgb2LabError("L, A and B values should be in the ranges [0, 100], [-128, +128] and [-128, +128] respectively.")

def checkLch(l, c, h):
    if not (0 <= l <= 100 and ((0 <= c <= 180 and 0 <= h < 360) or (c == 0 and h == -1))):
        raise Rgb2LabError("L, C and H values should be in the ranges [0, 100], [0, 180] and [0, 360) respectively. H may be -1 only if C is 0.")

def _makeConversionFns(T):

    '''
    Given `T` a CTypes numeric type, creates:
    1. a function factory for a function taking one Union as input and returning one
    2. a function factory for a function taking one Union as input and returning two via pointers
    '''

    def makeFields(fields): return tuple([(f, T) for f in fields])

    class RGB(Structure): _fields_ = makeFields("rgb")
    class LAB(Structure): _fields_ = makeFields("LAB")
    class LCH(Structure): _fields_ = makeFields("lch")

    Array3 = T * 3
    class Triplet(Union):
        _anonymous_ = ["rgb", "LAB", "lch"]
        _fields_ = [("data", Array3),
                    ("rgb", RGB),
                    ("LAB", LAB),
                    ("lch", LCH)]
    TripletPtr = POINTER(Triplet)

    def toTriplet(i, j, k): return Triplet(Array3(i, j, k))

    def makeRetOneFn(checkFn, libFn):
        libFn.argtypes = [Triplet]
        libFn.restype = Triplet
        def fn(i, j, k):
            checkFn(i, j, k)
            return tuple(libFn(toTriplet(i, j, k)).data)
        return fn

    def makeRetTwoFn(checkFn, libFn):
        libFn.argtypes = [Triplet, TripletPtr, TripletPtr]
        def fn(i, j, k):
            checkFn(i, j, k)
            t1 = Triplet(); t2 = Triplet()
            libFn(toTriplet(i, j, k), byref(t1), byref(t2))
            return tuple(t1.data) + tuple(t2.data)
        return fn

    return makeRetOneFn, makeRetTwoFn
