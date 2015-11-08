// Conversions of color values from RGB to LAB/LCH and back

typedef union {
    double data[3];
    struct { double r, g, b; };
    struct { double L, A, B; };
    struct { double l, c, h; };
} DoubleTriplet;

DoubleTriplet rgbFromLab(DoubleTriplet lab);
DoubleTriplet labFromRgb(DoubleTriplet rgb);
DoubleTriplet lchFromLab(DoubleTriplet lab);
DoubleTriplet labFromLch(DoubleTriplet lch);
DoubleTriplet lchFromRgb(DoubleTriplet rgb);
DoubleTriplet rgbFromLch(DoubleTriplet lch);
