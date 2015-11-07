// Conversions of color values from RGB to LAB/LCH and back

#include "rgb2lab_int.h"
#include "rgb2lab.h"
#include <math.h>
#include <stdlib.h>
#include <stdint.h>

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

static void fillTableWorker(int fixedPos, int fixed, int var1Min, int var1Max, int var2Min, int var2Max, IntTriplet (*fn)(IntTriplet), TinyRgb table[var1Max - var1Min + 1][var2Max - var2Min + 1])
{
    ++var1Max; ++var2Max; // to stop at max value plus one
    for (int var1 = var1Min; var1 != var1Max; ++var1)
        for (int var2 = var2Min; var2 != var2Max; ++var2)
        {
            IntTriplet input;
#define WRITEIN(TGT, F1, F2, F3) { TGT.data[0] = F1; TGT.data[1] = F2, TGT.data[2] = F3; }
            if      (fixedPos == 0) WRITEIN(input, fixed, var1, var2)
            else if (fixedPos == 1) WRITEIN(input, var1, fixed, var2)
            else                    WRITEIN(input, var1, var2, fixed)
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
            }
        }
}

int fillTableL_ab(TinyRgb table[257][257], int l)
{
    if (l < 0 || l > 100) return 1;
    fillTableWorker(0, l, /* a min max */ -128, +128, /* b min max */ -128, +128, &rgbFromLabInt, table);
    return 0;
}

int fillTableA(TinyRgb table[101][257], int a)
{
    if (a < -128 || a > +128) return 1;
    fillTableWorker(1, a, /* l min max */ 0, 100, /* a min max */ -128, +128, &rgbFromLabInt, table);
    return 0;
}

int fillTableB(TinyRgb table[101][257], int b)
{
    if (b < -128 || b > +128) return 1;
    fillTableWorker(2, b, /* l min max */ 0, 100, /* b min max */ -128, +128, &rgbFromLabInt, table);
    return 0;
}

int fillTableL_ch(TinyRgb table[181][360], int l)
{
    if (l < 0 || l > 100) return 1;
    fillTableWorker(0, l, /* c min max */ 0, 180, /* h min max */ 0, 359, &rgbFromLchInt, table);
    return 0;
}

int fillTableC(TinyRgb table[101][360], int c)
{
    if (c < 0 || c > 180) return 1;
    fillTableWorker(1, c, /* l min max */ 0, 100, /* h min max */ 0, 359, &rgbFromLchInt, table);
    return 0;
}

int fillTableH(TinyRgb table[101][181], int h)
{
    if (h < 0 || h > 359) return 1;
    fillTableWorker(2, h, /* l min max */ 0, 100, /* c min max */ 0, 180, &rgbFromLchInt, table);
    return 0;
}
