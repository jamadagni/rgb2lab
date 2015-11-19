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

#include "rgb2lab_int.h"
#include "rgb2lab.h"
#include <math.h>
#include <stdbool.h>

static DoubleTriplet _double(IntTriplet seq)
{
    DoubleTriplet temp = {{seq.data[0], seq.data[1], seq.data[2]}};
    return temp;
}

static IntTriplet _round(DoubleTriplet seq)
{
    IntTriplet temp;
    for (int i = 0; i < 3; ++i) temp.data[i] = round(seq.data[i]);
    return temp;
}

static IntTriplet _roundAndFixRgb(DoubleTriplet rgb)
{
    IntTriplet temp;
    for (int i = 0; i < 3; ++i)
    {
        int v = round(rgb.data[i] * 255);
        temp.data[i] = (v < 0 || v > 255) ? -1 : v;
    }
    return temp;
}

static IntTriplet _fixLch(IntTriplet lch)
{
    if (lch.c == 0) lch.h = -1; // sometimes c may become 0 by rounding, so need to do this again here
    return lch;
}

static DoubleTriplet _scaleRgb(IntTriplet rgb)
{
    DoubleTriplet temp;
    for (int i = 0; i < 3; ++i) temp.data[i] = rgb.data[i] / 255.0;
    return temp;
}

IntTriplet labFromRgbInt(IntTriplet rgb)
{
    return _round(labFromRgb(_scaleRgb(rgb)));
}

IntTriplet rgbFromLabInt(IntTriplet lab)
{
    return _roundAndFixRgb(rgbFromLab(_double(lab)));
}

IntTriplet lchFromRgbInt(IntTriplet rgb)
{
    return _fixLch(_round(lchFromRgb(_scaleRgb(rgb))));
}

IntTriplet rgbFromLchInt(IntTriplet lch)
{
    return _roundAndFixRgb(rgbFromLch(_double(lch)));
}

IntTriplet lchFromLabInt(IntTriplet lab)
{
    return _fixLch(_round(lchFromLab(_double(lab))));
}

IntTriplet labFromLchInt(IntTriplet lch)
{
    return _round(labFromLch(_double(lch)));
}

void labLchFromRgbInt(IntTriplet rgb, IntTriplet * lab, IntTriplet * lch)
{
    DoubleTriplet lab_ = labFromRgb(_scaleRgb(rgb));
    *lab = _round(lab_);
    *lch = _fixLch(_round(lchFromLab(lab_)));
}

void rgbLchFromLabInt(IntTriplet lab, IntTriplet * rgb, IntTriplet * lch)
{
    *rgb = _roundAndFixRgb(rgbFromLab(_double(lab)));
    *lch = _fixLch(_round(lchFromLab(_double(lab))));
}

void rgbLabFromLchInt(IntTriplet lch, IntTriplet * rgb, IntTriplet * lab)
{
    DoubleTriplet lab_ = labFromLch(_double(lch));
    *rgb = _roundAndFixRgb(rgbFromLab(lab_));
    *lab = _round(lab_);
}

typedef enum { L_AB, A_BL, B_AL, L_HC, C_HL, H_CL } TableType; // format: fixed_var1var2

static int fillTableWorker(TableType tt, int fixed, int var1Min, int var1Max, int var2Min, int var2Max, IntTriplet (*fn)(IntTriplet), TinyRgb table[var1Max - var1Min + 1][var2Max - var2Min + 1])
{
    int validRGBs = 0;
    ++var1Max; ++var2Max; // to stop at max value plus one
    for (int var1 = var1Min; var1 != var1Max; ++var1)
        for (int var2 = var2Min; var2 != var2Max; ++var2)
        {
            IntTriplet input;
#define WRITEINPUT(F1, F2, F3) input.data[0] = F1; input.data[1] = F2, input.data[2] = F3
            switch (tt)
            {
                case L_AB: WRITEINPUT(fixed, var1, var2); break;
                case L_HC: WRITEINPUT(fixed, var2, var1); break;
                case A_BL: // same as next case
                case C_HL: WRITEINPUT(var2, fixed, var1); break;
                case B_AL: // same as next case
                case H_CL: WRITEINPUT(var2, var1, fixed); break;
            }
            IntTriplet rgb = fn(input);
            TinyRgb * t = &table[var1 - var1Min][var2 - var2Min];
            if (rgb.r == -1 || rgb.g == -1 || rgb.b == -1)
                t->valid = 0;
            else
            {
                t->valid = 1;
                t->r = rgb.r;
                t->g = rgb.g;
                t->b = rgb.b;
                ++validRGBs;
            }
        }
    return validRGBs;
}

// strictly speaking there are no limits to the LAB/LCH values but this is for GUI
static bool _invalidL (int l) { return l <    0 || l > 100; }
static bool _invalidAB(int a) { return a < -128 || a > 128; }
static bool _invalidC (int c) { return c <    0 || c > 180; }
static bool _invalidH (int h) { return h <   -1 || h > 359; }

int fillTableL_AB(TinyRgb table[257][257], int l)
{
    if (_invalidL(l)) return -1;
    return fillTableWorker(L_AB, l, /* a min max */ -128, +128, /* b min max */ -128, +128, &rgbFromLabInt, table);
}

int fillTableA_BL(TinyRgb table[257][101], int a)
{
    if (_invalidAB(a)) return -1;
    return fillTableWorker(A_BL, a, /* b min max */ -128, +128, /* l min max */ 0, 100, &rgbFromLabInt, table);
}

int fillTableB_AL(TinyRgb table[257][101], int b)
{
    if (_invalidAB(b)) return -1;
    return fillTableWorker(B_AL, b, /* a min max */ -128, +128, /* l min max */ 0, 100, &rgbFromLabInt, table);
}

int fillTableL_HC(TinyRgb table[360][181], int l)
{
    if (_invalidL(l)) return -1;
    return fillTableWorker(L_HC, l, /* h min max */ 0, 359, /* c min max */ 0, 180, &rgbFromLchInt, table);
}

int fillTableC_HL(TinyRgb table[360][101], int c)
{
    if (_invalidC(c)) return -1;
    return fillTableWorker(C_HL, c, /* h min max */ 0, 359, /* l min max */ 0, 100, &rgbFromLchInt, table);
}

int fillTableH_CL(TinyRgb table[181][101], int h)
{
    if (_invalidH(h)) return -1;
    return fillTableWorker(H_CL, h, /* c min max */ 0, 180, /* l min max */ 0, 100, &rgbFromLchInt, table);
}
