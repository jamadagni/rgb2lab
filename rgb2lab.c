/*
Conversions of color values from RGB to LAB/LCH and back

These functions are based on:
    http://www.brucelindbloom.com/Math.html
and the pages linked to therefrom, especially:
    http://www.brucelindbloom.com/Eqn_RGB_XYZ_Matrix.html
    http://www.brucelindbloom.com/Eqn_XYZ_to_RGB.html
    http://www.brucelindbloom.com/Eqn_RGB_to_XYZ.html
    http://www.brucelindbloom.com/Eqn_XYZ_to_Lab.html
    http://www.brucelindbloom.com/Eqn_Lab_to_XYZ.html
    http://www.brucelindbloom.com/Eqn_Lab_to_LCH.html
    http://www.brucelindbloom.com/Eqn_LCH_to_Lab.html
Note that:
    R, G and B are linear w.r.t. device output
    X, Y and Z are linear w.r.t. energy
    L, a and b are linear w.r.t. perception
*/

#include "rgb2lab.h"
#include <math.h>

// NOTE: some curious problem with Python CTypes prevents more than 3 anonymous
// structs so can't include members x, y, z as part of DoubleTriplet union
#define X(xyz) xyz.data[0]
#define Y(xyz) xyz.data[1]
#define Z(xyz) xyz.data[2]

static const double PI = 3.14159265358979323846; // acos(-1)

// Convert RGB values of a color in the sRGB color space to CIE XYZ values
// Nominal range of the components for both input and output values is [0, 1]
static DoubleTriplet xyzFromRgb(DoubleTriplet rgb)
{
    for (int i = 0; i < 3; ++i)
    {
        double v = rgb.data[i];
        rgb.data[i] = (v > 0.04045) ? pow(((v + 0.055) / 1.055), 2.4) : (v / 12.92);
    }
    DoubleTriplet temp = {{
        rgb.r * 0.4124564 + rgb.g * 0.3575761 + rgb.b * 0.1804375,
        rgb.r * 0.2126729 + rgb.g * 0.7151522 + rgb.b * 0.0721750,
        rgb.r * 0.0193339 + rgb.g * 0.1191920 + rgb.b * 0.9503041
        }};
        // NOTE: coefficients above only appropriate for D65 illuminant and sRGB color space
    return temp;
}

// Convert CIE XYZ values of a color to RGB values in the sRGB color space
// Nominal range of the components for both input and output values is [0, 1]
static DoubleTriplet rgbFromXyz(DoubleTriplet xyz)
{
    DoubleTriplet rgb = {{
        X(xyz) *  3.2404542 + Y(xyz) * -1.5371385 + Z(xyz) * -0.4985314,
        X(xyz) * -0.9692660 + Y(xyz) *  1.8760108 + Z(xyz) *  0.0415560,
        X(xyz) *  0.0556434 + Y(xyz) * -0.2040259 + Z(xyz) *  1.0572252
        }};
        // NOTE: coefficients above only appropriate for D65 illuminant and sRGB color space
    for (int i = 0; i < 3; ++i)
    {
        double v = rgb.data[i];
        rgb.data[i] = (v > 0.0031308) ? (1.055 * pow(v, (1 / 2.4)) - 0.055) : (v * 12.92);
    }
    return rgb;
}

static const double eps = (6 * 6 * 6) / (29.0 * 29.0 * 29.0), kap = (29 * 29 * 29) / (3.0 * 3.0 * 3.0);

// NOTE: only appropriate for D65 illuminant and 2° observer
static const DoubleTriplet xyzReferenceValues = {{0.95047, 1.0, 1.08883}};

// Convert CIE XYZ values of a color to CIE Lab values assuming D65 illuminant and 2° observer
// The nominal ranges are as follows:
//     1) Input: [0, 1] for each component
//     2) Output: 0 to 100 for `L`; ±128 for `a` and `b`
static DoubleTriplet labFromXyz(DoubleTriplet xyz)
{
    for (int i = 0; i < 3; ++i)
    {
        xyz.data[i] /= xyzReferenceValues.data[i];
        double v = xyz.data[i];
        xyz.data[i] = (v > eps) ? pow(v, (1 / 3.0)) : ((kap * v + 16) / 116.0);
    }
    DoubleTriplet temp = {{(116 * Y(xyz)) - 16, 500 * (X(xyz) - Y(xyz)), 200 * (Y(xyz) - Z(xyz))}};
    return temp;
}

// Convert CIE Lab values of a color to CIE XYZ values assuming D65 illuminant and 2° observer
// The nominal ranges are as follows:
//     1) Input: 0 to 100 for `L`; ±128 for `a` and `b`
//     2) Output: [0, 1] for each component
static DoubleTriplet xyzFromLab(DoubleTriplet lab)
{
    double y = (lab.l + 16) / 116.0,
           x = lab.a / 500.0 + y,
           z = y - lab.b / 200.0;
    DoubleTriplet xyz = {{x, y, z}};
    for (int i = 0; i < 3; ++i)
    {
        double v = xyz.data[i], v3 = pow(v, 3);
        xyz.data[i] = ((v3 > eps) ? v3 : ((116 * v - 16) / kap)) * xyzReferenceValues.data[i];
    }
    return xyz;
}

/**
Convert RGB values of a color in the sRGB gamut to CIE Lab values
assuming D65 illuminant and 2° observer

The nominal ranges are as follows:
    1) Input: [0, 1] for each component
    2) Output: 0 to 100 for `L`; ±128 for `a` and `b`
*/
DoubleTriplet labFromRgb(DoubleTriplet rgb) { return labFromXyz(xyzFromRgb(rgb)); }

/**
Convert CIE Lab values of a color to RGB values in the sRGB gamut
assuming D65 illuminant and 2° observer

The nominal ranges are as follows:
    1) Input: 0 to 100 for `L`; ±128 for `a` and `b`
    2) Output: [0, 1] for each component
*/
DoubleTriplet rgbFromLab(DoubleTriplet lab) { return rgbFromXyz(xyzFromLab(lab)); }

/**
Convert CIE Lab values of a color to CIE LCH(ab) values

The nominal ranges are as follows:
    1) Input: 0 to 100 for `L`; ±128 for `a` and `b`
    2) Output: 0 to 100 for `L`; 0 to 128√2 for `C` and 0 to 360° for `h`
Note: `L` is unchanged
*/
DoubleTriplet lchFromLab(DoubleTriplet lab)
{
    DoubleTriplet temp = {{lab.l, 0, -1}};
    if (lab.a != 0 || lab.b != 0)
    {
        temp.c = hypot(lab.a, lab.b);
        temp.h = atan2(lab.b, lab.a) * 180 / PI;
        if (temp.h < 0) temp.h += 360; // +360 needed since atan2 outputs in ±π
    }
    return temp;
}

/**
Convert CIE LCH(ab) values of a color to CIE Lab values

The nominal ranges are as follows:
    1) Input: 0 to 100 for `L`; 0 to 128√2 for `C` and 0 to 360° for `h`
    2) Output: 0 to 100 for `L`; ±128 for `a` and `b`
Note: `L` is unchanged
*/
DoubleTriplet labFromLch(DoubleTriplet lch)
{
    if (lch.h == -1) lch.h = 0;
    else lch.h *= PI / 180;
    DoubleTriplet temp = {{lch.l, lch.c * cos(lch.h), lch.c * sin(lch.h)}};
    return temp;
}

/// Convenience function; see lchFromLab and labFromRgb
DoubleTriplet lchFromRgb(DoubleTriplet rgb) { return lchFromLab(labFromRgb(rgb)); }

/// Convenience function; see rgbFromLab and labFromLch
DoubleTriplet rgbFromLch(DoubleTriplet lch) { return rgbFromLab(labFromLch(lch)); }