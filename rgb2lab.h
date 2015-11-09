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
    double data[3];
    struct { double r, g, b; };
    struct { double L, A, B; };
    struct { double l, c, h; };
} DoubleTriplet;

DoubleTriplet rgbFromLab(DoubleTriplet lab);
DoubleTriplet labFromRgb(DoubleTriplet rgb);
DoubleTriplet lchFromLab(DoubleTriplet lab);
DoubleTriplet labFromLch(DoubleTriplet lch);
DoubleTriplet lchFromRgb(DoubleTriplet rgb);
DoubleTriplet rgbFromLch(DoubleTriplet lch);
