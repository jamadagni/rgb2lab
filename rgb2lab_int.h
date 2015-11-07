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

typedef struct { unsigned char valid, r, g, b; } TinyRgb;

int fillTableL_ab(TinyRgb table[257][257], int l); // 257 A, 257 B
int fillTableA   (TinyRgb table[101][257], int a); // 101 L, 257 B
int fillTableB   (TinyRgb table[101][257], int b); // 101 L, 257 A
int fillTableL_ch(TinyRgb table[181][360], int l); // 181 c, 360 h
int fillTableC   (TinyRgb table[101][360], int c); // 101 l, 360 h
int fillTableH   (TinyRgb table[101][181], int h); // 101 l, 181 c
