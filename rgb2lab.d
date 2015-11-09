// librgb2lab (D version)
// ======================
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
//
// Credit:
// These functions are based on formulae and coefficients provided at
// Bruce Justin Lindbloom's website http://www.brucelindbloom.com/

union RealTriplet
{
    real [3] data;
    struct { real r, g, b; }
    struct { real L, A, B; }
    struct { real l, c, h; }
    struct { real x, y, z; }
    this(real i, real j, real k) { data = [i, j, k]; }
    alias data this; // for foreach, [] operations etc
}

private
{

// Convert RGB values of a color in the sRGB color space to CIE XYZ values
// Nominal range of the components for both input and output values is [0, 1]
RealTriplet xyzFromRgb(RealTriplet rgb)
{
    foreach (ref v; rgb) v = (v > 0.04045) ? (((v + 0.055) / 1.055) ^^ 2.4) : (v / 12.92);
    return RealTriplet(
        rgb.r * 0.4124564 + rgb.g * 0.3575761 + rgb.b * 0.1804375,
        rgb.r * 0.2126729 + rgb.g * 0.7151522 + rgb.b * 0.0721750,
        rgb.r * 0.0193339 + rgb.g * 0.1191920 + rgb.b * 0.9503041
        );
        // NOTE: coefficients above only appropriate for D65 illuminant and sRGB color space
}

// Convert CIE XYZ values of a color to RGB values in the sRGB color space
// Nominal range of the components for both input and output values is [0, 1]
RealTriplet rgbFromXyz(RealTriplet xyz)
{
    RealTriplet rgb = RealTriplet(
        xyz.x *  3.2404542 + xyz.y * -1.5371385 + xyz.z * -0.4985314,
        xyz.x * -0.9692660 + xyz.y *  1.8760108 + xyz.z *  0.0415560,
        xyz.x *  0.0556434 + xyz.y * -0.2040259 + xyz.z *  1.0572252
        );
        // NOTE: coefficients above only appropriate for D65 illuminant and sRGB color space
    foreach (ref v; rgb) v = (v > 0.0031308) ? (1.055 * v ^^ (1 / 2.4) - 0.055) : (v * 12.92);
    return rgb;
}

enum real eps = (6 / 29.0) ^^ 3, kap = (29 / 3.0) ^^ 3;

// NOTE: only appropriate for D65 illuminant and 2° observer
enum RealTriplet xyzReferenceValues = RealTriplet(0.95047, 1.0, 1.08883);

// Convert CIE XYZ values of a color to CIE Lab values assuming D65 illuminant and 2° observer
// The nominal ranges are as follows:
//     1) Input: [0, 1] for each component
//     2) Output: 0 to 100 for $(I L); ±128 for $(I a) and $(I b)
RealTriplet labFromXyz(RealTriplet xyz)
{
    xyz [] /= xyzReferenceValues [];
    foreach (ref v; xyz) v = (v > eps) ? (v ^^ (1 / 3.0)) : ((kap * v + 16) / 116.0);
    return RealTriplet((116 * xyz.y) - 16, 500 * (xyz.x - xyz.y), 200 * (xyz.y - xyz.z));
}

// Convert CIE Lab values of a color to CIE XYZ values assuming D65 illuminant and 2° observer
// The nominal ranges are as follows:
//     1) Input: 0 to 100 for $(I L); ±128 for $(I a) and $(I b)
//     2) Output: [0, 1] for each component
RealTriplet xyzFromLab(RealTriplet lab)
{
    RealTriplet xyz;
    xyz.y = (lab.L + 16) / 116.0,
    xyz.x = lab.A / 500.0 + xyz.y,
    xyz.z = xyz.y - lab.B / 200.0;
    foreach (ref v; xyz)
    {
        real v3 = v ^^ 3;
        v = (v3 > eps) ? v3 : ((116 * v - 16) / kap);
    }
    xyz [] *= xyzReferenceValues [];
    return xyz;
}

} // private

/**
Convert RGB values of a color in the sRGB gamut to CIE Lab values
assuming D65 illuminant and 2° observer

The nominal ranges are as follows:
    1) Input: [0, 1] for each component
    2) Output: 0 to 100 for $(I L); ±128 for $(I a) and $(I b)
*/
RealTriplet labFromRgb(RealTriplet rgb) { return labFromXyz(xyzFromRgb(rgb)); }

/**
Convert CIE Lab values of a color to RGB values in the sRGB gamut
assuming D65 illuminant and 2° observer

The nominal ranges are as follows:
    1) Input: 0 to 100 for $(I L); ±128 for $(I a) and $(I b)
    2) Output: [0, 1] for each component
*/
RealTriplet rgbFromLab(RealTriplet lab) { return rgbFromXyz(xyzFromLab(lab)); }

/**
Convert CIE Lab values of a color to CIE LCH(ab) values

The nominal ranges are as follows:
    1) Input: 0 to 100 for $(I L); ±128 for $(I a) and $(I b)
    2) Output: 0 to 100 for $(I L); 0 to 128√2 for $(I C) and 0 to 360° for $(I h)
$(B Note): $(I L) is unchanged
*/
RealTriplet lchFromLab(RealTriplet lab)
{
    if (lab.A == 0 && lab.B == 0) return RealTriplet(lab.L, 0, -1);
    import std.math: hypot, atan2, PI;
    real h = atan2(lab.B, lab.A) * 180 / PI;
    if (lab.h < 0) lab.h += 360; // +360 needed since atan2 outputs in ±π
    return RealTriplet(lab.L, hypot(lab.A, lab.B), lab.h);
}

/**
Convert CIE LCH(ab) values of a color to CIE Lab values

The nominal ranges are as follows:
    1) Input: 0 to 100 for $(I L); 0 to 128√2 for $(I C) and 0 to 360° for $(I h)
    2) Output: 0 to 100 for $(I L); ±128 for $(I a) and $(I b)
$(B Note): $(I L) is unchanged
*/
RealTriplet labFromLch(RealTriplet lch)
{
    if (lch.h == -1)
    {
        if (lch.c != 0) return RealTriplet(); // all NaNs
        return RealTriplet(lch.l, 0, 0); // if c == 0
    }
    import std.math: cos, sin, PI;
    lch.h *= PI / 180;
    return RealTriplet(lch.l, lch.c * cos(lch.h), lch.c * sin(lch.h));
}

/// Convenience function; see lchFromLab and labFromRgb
RealTriplet lchFromRgb(RealTriplet rgb) { return lchFromLab(labFromRgb(rgb)); }

/// Convenience function; see rgbFromLab and labFromLch
RealTriplet rgbFromLch(RealTriplet lch) { return rgbFromLab(labFromLch(lch)); }
