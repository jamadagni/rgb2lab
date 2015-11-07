// Conversions of color values from RGB to LAB/LCH and back

typedef union {
    int data[3];
    struct { int r, g, b; };
    struct { int L, A, B; };
    struct { int l, c, h; };
} IntTriplet;

IntTriplet labFromRgbInt(IntTriplet rgb);
IntTriplet rgbFromLabInt(IntTriplet lab);
IntTriplet lchFromRgbInt(IntTriplet rgb);
IntTriplet rgbFromLchInt(IntTriplet lch);
IntTriplet lchFromLabInt(IntTriplet lab);
IntTriplet labFromLchInt(IntTriplet lch);
void labLchFromRgbInt(IntTriplet rgb, IntTriplet * lab, IntTriplet * lch);
void rgbLchFromLabInt(IntTriplet lab, IntTriplet * rgb, IntTriplet * lch);
void rgbLabFromLchInt(IntTriplet lch, IntTriplet * rgb, IntTriplet * lab);
