// librgb2lab
// ==========
//
// Convert color values from RGB to/from CIE LAB/LCH
// for sRGB gamut, D65 illuminant, 2° observer
//
// Copyright (C) 2015, Shriramana Sharma, samjnaa-at-gmail-dot-com
//
// Use, modification and distribution are permitted subject to the
// "BSD-2-Clause"-type license stated in the accompanying file LICENSE.txt

typedef union
{
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

int fillTableL_AB(TinyRgb table[257][257], int l);
int fillTableA_BL(TinyRgb table[257][101], int a);
int fillTableB_AL(TinyRgb table[257][101], int b);
int fillTableL_HC(TinyRgb table[360][181], int l);
int fillTableC_HL(TinyRgb table[360][101], int c);
int fillTableH_CL(TinyRgb table[181][101], int h);
