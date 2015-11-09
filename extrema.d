import rgb2lab;
import core.time: MonoTime;
import std.stdio, std.format, std.range, std.conv, std.array, std.parallelism;
version(writebin)
{
    import std.file;
    import msgpack;
}

float [3] toFloat(real [3] r, uint scale = 1) { return [(r[0] * scale).to!float, (r[1] * scale).to!float, (r[2] * scale).to!float]; }

void mywrite(string firstLabel, float firstValue, string otherLabels, float [] otherValues)
{
    writef("%s = %10.4f at ", firstLabel, firstValue);
    static string [] otherFormats = ["%10.4f, ", "%10.4f; ", "% 4g, ", "% 4g, ", "% 4g\n"];
    foreach (l, f, v; zip(otherLabels, otherFormats, otherValues)) write(l, " = ", f.format(v));
}

void main()
{
    MonoTime startTime, endTime;

{
    auto labFromRgbMap = uninitializedArray!(float [3][][][])(256, 256, 256);
    real [3] RGB;
    startTime = MonoTime.currTime;
    foreach (r; parallel(iota(0, 256)))
        foreach (g; 0 .. 256)
            foreach (b; 0 .. 256)
                labFromRgbMap[r][g][b] = labFromRgb(RealTriplet(r / 255.0, g / 255.0, b / 255.0)).toFloat();
    endTime = MonoTime.currTime;
    writefln("Completed %s calls to labFromRgb in %.3f seconds", 256 ^^ 3, (endTime - startTime).total!"msecs" / 1000.0);
    version(writebin) std.file.write("labFromRgb.bin", pack(labFromRgbMap));

    float [5] abRgbForMaxL, abRgbForMinL, lbRgbForMaxA, lbRgbForMinA, laRgbForMaxB, laRgbForMinB;
    float [3] LAB;
    float L, A, B;
    float maxL, maxA, maxB;
    float minL, minA, minB;
    maxL = maxA = maxB = -float.infinity; // all values will be above this
    minL = minA = minB = +float.infinity; // all values will be below this
    startTime = MonoTime.currTime;
    foreach (r; 0 .. 256)
        foreach (g; 0 .. 256)
            foreach (b; 0 .. 256)
            {
                LAB = labFromRgbMap[r][g][b];
                L = LAB[0]; A = LAB[1]; B = LAB[2];
                if (L > maxL) { maxL = L; abRgbForMaxL = [A, B, r, g, b]; }
                if (L < minL) { minL = L; abRgbForMinL = [A, B, r, g, b]; }
                if (A > maxA) { maxA = A; lbRgbForMaxA = [L, B, r, g, b]; }
                if (A < minA) { minA = A; lbRgbForMinA = [L, B, r, g, b]; }
                if (B > maxB) { maxB = B; laRgbForMaxB = [L, A, r, g, b]; }
                if (B < minB) { minB = B; laRgbForMinB = [L, A, r, g, b]; }
            }
    endTime = MonoTime.currTime;
    writefln("Completed %s loops searching for Lab extrema in %.3f seconds", 256 ^^ 3, (endTime - startTime).total!"msecs" / 1000.0);

    mywrite("maxL", maxL, "ABrgb", abRgbForMaxL);
    mywrite("minL", minL, "ABrgb", abRgbForMinL);
    mywrite("maxA", maxA, "LBrgb", lbRgbForMaxA);
    mywrite("minA", minA, "LBrgb", lbRgbForMinA);
    mywrite("maxB", maxB, "LArgb", laRgbForMaxB);
    mywrite("minB", minB, "LArgb", laRgbForMinB);
}

{
    auto rgbFromLabMap = uninitializedArray!(float [3][][][])(101, 257, 257);
    startTime = MonoTime.currTime;
    foreach (l; parallel(iota(0, 101)))
        foreach (a; -128 .. 129)
            foreach (b; -128 .. 129)
                rgbFromLabMap[l][a + 128][b + 128] = rgbFromLab(RealTriplet(l, a, b)).toFloat(255); // 255 is scale factor
    endTime = MonoTime.currTime;
    writefln("Completed %s calls to rgbFromLab in %.3f seconds", 101 * 257 * 257, (endTime - startTime).total!"msecs" / 1000.0);
    version(writebin) std.file.write("rgbFromLab.bin", pack(rgbFromLabMap));

    float [5] gbLabForMaxR, gbLabForMinR, rbLabForMaxG, rbLabForMinG, rgLabForMaxB, rgLabForMinB;
    float [3] RGB;
    float R, G, B;
    float maxR, maxG, maxB;
    float minR, minG, minB;
    maxR = maxG = maxB = -float.infinity; // all values will be above this
    minR = minG = minB = +float.infinity; // all values will be below this
    startTime = MonoTime.currTime;
    foreach (l; 0 .. 101)
        foreach (a; -128 .. 129)
            foreach (b; -128 .. 129)
            {
                RGB = rgbFromLabMap[l][a + 128][b + 128];
                R = RGB[0]; G = RGB[1]; B = RGB[2];
                if (R > maxR) { maxR = R; gbLabForMaxR = [G, B, l, a, b]; }
                if (R < minR) { minR = R; gbLabForMinR = [G, B, l, a, b]; }
                if (G > maxG) { maxG = G; rbLabForMaxG = [R, B, l, a, b]; }
                if (G < minG) { minG = G; rbLabForMinG = [R, B, l, a, b]; }
                if (B > maxB) { maxB = B; rgLabForMaxB = [R, G, l, a, b]; }
                if (B < minB) { minB = B; rgLabForMinB = [R, G, l, a, b]; }
            }
    endTime = MonoTime.currTime;
    writefln("Completed %s loops searching for RGB extrema in %.3f seconds", 101 * 257 * 257, (endTime - startTime).total!"msecs" / 1000.0);

    mywrite("maxR", maxR, "GBlab", gbLabForMaxR);
    mywrite("minR", minR, "GBlab", gbLabForMinR);
    mywrite("maxG", maxG, "RBlab", rbLabForMaxG);
    mywrite("minG", minG, "RBlab", rbLabForMinG);
    mywrite("maxB", maxB, "RGlab", rgLabForMaxB);
    mywrite("minB", minB, "RGlab", rgLabForMinB);
}

}
