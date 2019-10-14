// librgb2lab
// ==========
//
// Convert color values from RGB to/from CIE LAB/LCH
// for sRGB gamut, D65 illuminant, 2° observer
//
// Copyright (C) 2019, Shriramana Sharma, samjnaa-at-gmail-dot-com
//
// Use, modification and distribution are permitted subject to the
// "BSD-2-Clause"-type license stated in the accompanying file LICENSE.txt

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
    if (lch.h == 360) lch.h = 0; // again can happen by rounding
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

typedef enum { LforAB, AforBL, BforAL, LforHC, CforHL, HforCL } TableType1D;

static int fillTableWorker_fix2_var1(TableType1D tt, int fixed1, int fixed2,
                                     int varMin, int varMax,
                                     IntTriplet (*fn)(IntTriplet),
                                     TinyRgb table[varMax - varMin + 1])
{
    int validRGBs = 0;
    ++varMax; // to stop at max value plus one
    for (int var = varMin; var != varMax; ++var)
    {
        IntTriplet input;
#define WRITEINPUT(F1, F2, F3) input.data[0] = F1; input.data[1] = F2, input.data[2] = F3
        switch (tt)
        {
            case LforAB: WRITEINPUT(var, fixed1, fixed2); break;
            case LforHC: WRITEINPUT(var, fixed2, fixed1); break;
            case AforBL: // same as next case
            case CforHL: WRITEINPUT(fixed2, var, fixed1); break;
            case BforAL: // same as next case
            case HforCL: WRITEINPUT(fixed2, fixed1, var); break;
        }
        IntTriplet rgb = fn(input);
        TinyRgb * t = &table[var - varMin];
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

typedef enum { ABforL, BLforA, ALforB, HCforL, HLforC, CLforH } TableType2D;

static int fillTableWorker_fix1_var2(TableType2D tt, int fixed,
                                     int var1Min, int var1Max,
                                     int var2Min, int var2Max,
                                     IntTriplet (*fn)(IntTriplet),
                                     TinyRgb table[var1Max - var1Min + 1][var2Max - var2Min + 1])
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
                case ABforL: WRITEINPUT(fixed, var1, var2); break;
                case HCforL: WRITEINPUT(fixed, var2, var1); break;
                case BLforA: // same as next case
                case HLforC: WRITEINPUT(var2, fixed, var1); break;
                case ALforB: // same as next case
                case CLforH: WRITEINPUT(var2, var1, fixed); break;
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

int fillTable_LforAB(TinyRgb table[101], int a, int b)
{
    if (_invalidAB(a) || _invalidAB(b)) return -1;
    return fillTableWorker_fix2_var1(LforAB, a, b, /* l min max */ 0, 100, &rgbFromLabInt, table);
}

int fillTable_AforBL(TinyRgb table[257], int b, int l)
{
    if (_invalidAB(b) || _invalidL(l)) return -1;
    return fillTableWorker_fix2_var1(AforBL, b, l, /* a min max */ -128, +128, &rgbFromLabInt, table);
}

int fillTable_BforAL(TinyRgb table[257], int a, int l)
{
    if (_invalidAB(a) || _invalidL(l)) return -1;
    return fillTableWorker_fix2_var1(BforAL, a, l, /* b min max */ -128, +128, &rgbFromLabInt, table);
}

int fillTable_LforHC(TinyRgb table[101], int h, int c)
{
    if (_invalidH(h) || _invalidC(c)) return -1;
    return fillTableWorker_fix2_var1(LforHC, h, c, /* l min max */ 0, 100, &rgbFromLchInt, table);
}

int fillTable_CforHL(TinyRgb table[181], int h, int l)
{
    if (_invalidH(h) || _invalidL(l)) return -1;
    return fillTableWorker_fix2_var1(CforHL, h, l, /* c min max */ 0, 180, &rgbFromLchInt, table);
}

int fillTable_HforCL(TinyRgb table[360], int c, int l)
{
    if (_invalidC(c) || _invalidL(l)) return -1;
    return fillTableWorker_fix2_var1(HforCL, c, l, /* h min max */ 0, 359, &rgbFromLchInt, table);
}

int fillTable_ABforL(TinyRgb table[257][257], int l)
{
    if (_invalidL(l)) return -1;
    return fillTableWorker_fix1_var2(ABforL, l, /* a min max */ -128, +128, /* b min max */ -128, +128, &rgbFromLabInt, table);
}

int fillTable_BLforA(TinyRgb table[257][101], int a)
{
    if (_invalidAB(a)) return -1;
    return fillTableWorker_fix1_var2(BLforA, a, /* b min max */ -128, +128, /* l min max */ 0, 100, &rgbFromLabInt, table);
}

int fillTable_ALforB(TinyRgb table[257][101], int b)
{
    if (_invalidAB(b)) return -1;
    return fillTableWorker_fix1_var2(ALforB, b, /* a min max */ -128, +128, /* l min max */ 0, 100, &rgbFromLabInt, table);
}

int fillTable_HCforL(TinyRgb table[360][181], int l)
{
    if (_invalidL(l)) return -1;
    return fillTableWorker_fix1_var2(HCforL, l, /* h min max */ 0, 359, /* c min max */ 0, 180, &rgbFromLchInt, table);
}

int fillTable_HLforC(TinyRgb table[360][101], int c)
{
    if (_invalidC(c)) return -1;
    return fillTableWorker_fix1_var2(HLforC, c, /* h min max */ 0, 359, /* l min max */ 0, 100, &rgbFromLchInt, table);
}

int fillTable_CLforH(TinyRgb table[181][101], int h)
{
    if (_invalidH(h)) return -1;
    return fillTableWorker_fix1_var2(CLforH, h, /* c min max */ 0, 180, /* l min max */ 0, 100, &rgbFromLchInt, table);
}
