// Conversions of color values from RGB to LAB/LCH and back

typedef union {
    double data[3];
    struct { double r, g, b; };
    struct { double l, a, B; }; // cap B to silence error
    struct { double L, c, h; }; // cap L to silence error
} DoubleTriplet;

DoubleTriplet rgbFromLab(DoubleTriplet lab);
DoubleTriplet labFromRgb(DoubleTriplet rgb);
DoubleTriplet lchFromLab(DoubleTriplet lab);
DoubleTriplet labFromLch(DoubleTriplet lch);
DoubleTriplet lchFromRgb(DoubleTriplet rgb);
DoubleTriplet rgbFromLch(DoubleTriplet lch);
