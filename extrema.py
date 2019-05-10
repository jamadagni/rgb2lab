#! /usr/bin/env python3

# Copyright (C) 2015, Shriramana Sharma, samjnaa-at-gmail-dot-com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from rgb2lab import *
from time import process_time

otherFormats = ["{:10.4f}, ", "{:10.4f}; ", "{: 4d}, ", "{: 4d}, ", "{: 4d}\n"];
def mywrite(firstLabel, firstValue, otherLabels, otherValues):
    print("{} = {:10.4f} at ".format(firstLabel, firstValue), end = "")
    for l, f, v in zip(otherLabels, otherFormats, otherValues):
        print(l, " = ", f.format(v), sep = "", end = "")

labFromRgbMap = []
startTime = process_time()
for r in range(256):
    plane = []
    for g in range(256):
        row = []
        for b in range(256):
            row.append(labFromRgb(*(v / 255.0 for v in (r, g, b))))
        plane.append(row)
    labFromRgbMap.append(plane)
endTime = process_time()
print("Completed {} calls to labFromRgb in {:.3f} seconds".format(256 ** 3, endTime - startTime))

maxL = maxA = maxB = float("-inf") # all values will be above this
minL = minA = minB = float("+inf") # all values will be below this
startTime = process_time()
for r in range(256):
    for g in range(256):
        for b in range(256):
            LAB = labFromRgbMap[r][g][b]
            L = LAB[0] ; A = LAB[1] ; B = LAB[2]
            if L > maxL: maxL = L ; abRgbForMaxL = [A, B, r, g, b]
            if L < minL: minL = L ; abRgbForMinL = [A, B, r, g, b]
            if A > maxA: maxA = A ; lbRgbForMaxA = [L, B, r, g, b]
            if A < minA: minA = A ; lbRgbForMinA = [L, B, r, g, b]
            if B > maxB: maxB = B ; laRgbForMaxB = [L, A, r, g, b]
            if B < minB: minB = B ; laRgbForMinB = [L, A, r, g, b]
endTime = process_time()
print("Completed {} loops searching for Lab extrema in {:.3f} seconds".format(256 ** 3, endTime - startTime))

mywrite("maxL", maxL, "ABrgb", abRgbForMaxL)
mywrite("minL", minL, "ABrgb", abRgbForMinL)
mywrite("maxA", maxA, "LBrgb", lbRgbForMaxA)
mywrite("minA", minA, "LBrgb", lbRgbForMinA)
mywrite("maxB", maxB, "LArgb", laRgbForMaxB)
mywrite("minB", minB, "LArgb", laRgbForMinB)

rgbFromLabMap = []
startTime = process_time()
for l in range(101):
    plane = []
    for a in range(-128, 129):
        row = []
        for b in range(-128, 129):
            row.append(tuple(v * 255 for v in rgbFromLab(l, a, b)))
        plane.append(row)
    rgbFromLabMap.append(plane)
endTime = process_time()
print("Completed {} calls to rgbFromLab in {:.3f} seconds".format(101 * 257 * 257, endTime - startTime))

maxR = maxG = maxB = float("-inf") # all values will be above this
minR = minG = minB = float("+inf") # all values will be below this
startTime = process_time()
for l in range(101):
    for a in range(-128, 129):
        for b in range(-128, 129):
            RGB = rgbFromLabMap[l][a + 128][b + 128]
            R = RGB[0] ; G = RGB[1] ; B = RGB[2]
            if R > maxR: maxR = R ; gbLabForMaxR = [G, B, l, a, b]
            if R < minR: minR = R ; gbLabForMinR = [G, B, l, a, b]
            if G > maxG: maxG = G ; rbLabForMaxG = [R, B, l, a, b]
            if G < minG: minG = G ; rbLabForMinG = [R, B, l, a, b]
            if B > maxB: maxB = B ; rgLabForMaxB = [R, G, l, a, b]
            if B < minB: minB = B ; rgLabForMinB = [R, G, l, a, b]
endTime = process_time()
print("Completed {} loops searching for RGB extrema in {:.3f} seconds".format(101 * 257 * 257, endTime - startTime))

mywrite("maxR", maxR, "GBlab", gbLabForMaxR)
mywrite("minR", minR, "GBlab", gbLabForMinR)
mywrite("maxG", maxG, "RBlab", rbLabForMaxG)
mywrite("minG", minG, "RBlab", rbLabForMinG)
mywrite("maxB", maxB, "RGlab", rgLabForMaxB)
mywrite("minB", minB, "RGlab", rgLabForMinB)
