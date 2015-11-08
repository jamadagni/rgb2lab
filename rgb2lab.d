/**
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

private
{

// Convert RGB values of a color in the sRGB color space to CIE XYZ values
// Nominal range of the components for both input and output values is [0, 1]
real [3] xyzFromRgb(real [3] rgb)
{
    foreach (ref v; rgb) v = (v > 0.04045) ? (((v + 0.055) / 1.055) ^^ 2.4) : (v / 12.92);
    real r = rgb[0], g = rgb[1], b = rgb[2];
    return [
        r * 0.4124564 + g * 0.3575761 + b * 0.1804375,
        r * 0.2126729 + g * 0.7151522 + b * 0.0721750,
        r * 0.0193339 + g * 0.1191920 + b * 0.9503041
        ];
        // NOTE: coefficients above only appropriate for D65 illuminant and sRGB color space
}

// Convert CIE XYZ values of a color to RGB values in the sRGB color space
// Nominal range of the components for both input and output values is [0, 1]
real [3] rgbFromXyz(real [3] xyz)
{
    real x = xyz[0], y = xyz[1], z = xyz[2];
    real [3] rgb = [
        x *  3.2404542 + y * -1.5371385 + z * -0.4985314,
        x * -0.9692660 + y *  1.8760108 + z *  0.0415560,
        x *  0.0556434 + y * -0.2040259 + z *  1.0572252
        ];
        // NOTE: coefficients above only appropriate for D65 illuminant and sRGB color space
    foreach (ref v; rgb) v = (v > 0.0031308) ? (1.055 * v ^^ (1 / 2.4) - 0.055) : (v * 12.92);
    return rgb;
}

enum eps = (6 / 29.0) ^^ 3, kap = (29 / 3.0) ^^ 3;

// NOTE: only appropriate for D65 illuminant and 2° observer
real [3] xyzReferenceValues = [0.95047, 1.0, 1.08883];

// Convert CIE XYZ values of a color to CIE Lab values assuming D65 illuminant and 2° observer
// The nominal ranges are as follows:
//     1) Input: [0, 1] for each component
//     2) Output: 0 to 100 for $(I L); ±128 for $(I a) and $(I b)
real [3] labFromXyz(real [3] xyz)
{
    xyz [] /= xyzReferenceValues [];
    foreach (ref v; xyz) v = (v > eps) ? (v ^^ (1 / 3.0)) : ((kap * v + 16) / 116.0);
    real x = xyz[0], y = xyz[1], z = xyz[2];
    return [(116 * y) - 16, 500 * (x - y), 200 * (y - z)];
}

// Convert CIE Lab values of a color to CIE XYZ values assuming D65 illuminant and 2° observer
// The nominal ranges are as follows:
//     1) Input: 0 to 100 for $(I L); ±128 for $(I a) and $(I b)
//     2) Output: [0, 1] for each component
real [3] xyzFromLab(real [3] lab)
{
    real l = lab[0], a = lab[1], b = lab[2],
         y = (l + 16) / 116.0,
         x = a / 500.0 + y,
         z = y - b / 200.0;
    real [3] xyz = [x, y, z];
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
real [3] labFromRgb(real [3] rgb) { return labFromXyz(xyzFromRgb(rgb)); }

/**
Convert CIE Lab values of a color to RGB values in the sRGB gamut
assuming D65 illuminant and 2° observer

The nominal ranges are as follows:
    1) Input: 0 to 100 for $(I L); ±128 for $(I a) and $(I b)
    2) Output: [0, 1] for each component
*/
real [3] rgbFromLab(real [3] lab) { return rgbFromXyz(xyzFromLab(lab)); }

/**
Convert CIE Lab values of a color to CIE LCH(ab) values

The nominal ranges are as follows:
    1) Input: 0 to 100 for $(I L); ±128 for $(I a) and $(I b)
    2) Output: 0 to 100 for $(I L); 0 to 128√2 for $(I C) and 0 to 360° for $(I h)
$(B Note): $(I L) is unchanged
*/
real [3] lchFromLab(real [3] lab)
{
    import std.math: hypot, atan2, PI;
    real l = lab[0], a = lab[1], b = lab[2];
    if (a == 0 && b == 0) return [l, 0, -1];
    real h = atan2(b, a) * 180 / PI;
    if (h < 0) h += 360; // +360 needed since atan2 outputs in ±π
    return [l, hypot(a, b), h];
}

/**
Convert CIE LCH(ab) values of a color to CIE Lab values

The nominal ranges are as follows:
    1) Input: 0 to 100 for $(I L); 0 to 128√2 for $(I C) and 0 to 360° for $(I h)
    2) Output: 0 to 100 for $(I L); ±128 for $(I a) and $(I b)
$(B Note): $(I L) is unchanged
*/
real [3] labFromLch(real [3] lch)
{
    import std.math: cos, sin, PI;
    real l = lch[0], c = lch[1], h = lch[2];
    if (h == -1)
    {
        if (c != 0) return new real[3]; // all NaNs
        return [l, 0, 0]; // if c == 0
    }
    h *= PI / 180;
    return [l, c * cos(h), c * sin(h)];
}

/// Convenience function; see lchFromLab and labFromRgb
real [3] lchFromRgb(real [3] rgb) { return lchFromLab(labFromRgb(rgb)); }

/// Convenience function; see rgbFromLab and labFromLch
real [3] rgbFromLch(real [3] lch) { return rgbFromLab(labFromLch(lch)); }
