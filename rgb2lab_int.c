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
    *rgb = _roundAndFixRgb(rgbFromLch(_double(lab)));
    *lch = _fixLch(_round(lchFromLab(_double(lab))));
}

void rgbLabFromLchInt(IntTriplet lch, IntTriplet * rgb, IntTriplet * lab)
{
    DoubleTriplet lab_ = labFromLch(_double(lch));
    *rgb = _roundAndFixRgb(rgbFromLab(lab_));
    *lab = _round(lab_);
}
