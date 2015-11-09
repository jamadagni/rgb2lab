// librgb2lab
// ==========
// Convert color values from RGB to/from CIE LAB/LCH
// for sRGB gamut, D65 illuminant, 2° observer
//
// Copyright (C) 2015, Shriramana Sharma
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
