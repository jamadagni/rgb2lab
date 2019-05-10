// librgb2lab
// ==========
// Convert color values from RGB to/from CIE LAB/LCH
// for sRGB gamut, D65 illuminant, 2° observer
//
// Copyright (C) 2015, Shriramana Sharma, samjnaa-at-gmail-dot-com
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
//
// Credit:
// These functions are based on formulae and coefficients provided at
// Bruce Justin Lindbloom's website http://www.brucelindbloom.com/

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
    double y = (lab.L + 16) / 116.0,
           x = lab.A / 500.0 + y,
           z = y - lab.B / 200.0;
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
    DoubleTriplet temp = {{lab.L, 0, -1}};
    if (lab.A != 0 || lab.B != 0)
    {
        temp.c = hypot(lab.A, lab.B);
        temp.h = atan2(lab.B, lab.A) * 180 / PI;
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
    DoubleTriplet temp = {{lch.l, 0, 0}};
    if (lch.h == -1)
    {
        if (lch.c != 0) temp.l = nan(""); // illegal input; give illegal output to signal it
        return temp; // if lch.c == 0, then {l, 0, 0} will be returned which is correct
    }
    lch.h *= PI / 180;
    temp.A = lch.c * cos(lch.h);
    temp.B = lch.c * sin(lch.h);
    return temp;
}

/// Convenience function; see lchFromLab and labFromRgb
DoubleTriplet lchFromRgb(DoubleTriplet rgb) { return lchFromLab(labFromRgb(rgb)); }

/// Convenience function; see rgbFromLab and labFromLch
DoubleTriplet rgbFromLch(DoubleTriplet lch) { return rgbFromLab(labFromLch(lch)); }
