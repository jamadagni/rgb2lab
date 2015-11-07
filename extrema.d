import rgb2lab;
import core.time: MonoTime;
import std.stdio, std.format, std.range, std.conv;
version(writebin)
{
    import std.file;
    import msgpack;
}

float[3] toFloat(real[3] r) { return [to!float(r[0]), to!float(r[1]), to!float(r[2])]; }

void main()
{
    MonoTime startTime, endTime;
    float [3][] row;
    auto rowSink = appender(row);
    float [3][][] plane;
    auto planeSink = appender(plane);
    rowSink.reserve(256);
    planeSink.reserve(256);

    float [3][][][] labFromRgbMap;
    labFromRgbMap.reserve(256);
    startTime = MonoTime.currTime;
    foreach (r; 0 .. 256)
    {
        planeSink.clear();
        foreach (g; 0 .. 256)
        {
            rowSink.clear();
            foreach (b; 0 .. 256)
                rowSink ~= labFromRgb([r / 255.0, g / 255.0, b / 255.0]).toFloat();
            planeSink ~= rowSink.data.dup;
        }
        labFromRgbMap ~= planeSink.data.dup;
    }
    endTime = MonoTime.currTime;
    writefln("Completed %s calls to labFromRgb in %.3f seconds", 256 ^^ 3, (endTime - startTime).total!"msecs" / 1000.0);
    version(writebin) std.file.write("labFromRgb.bin", pack(labFromRgbMap));

    float [5] abRgbForMaxL, abRgbForMinL, lbRgbForMaxA, lbRgbForMinA, laRgbForMaxB, laRgbForMinB;
    float [3] LAB;
    float L, A, B;
    float maxL, maxA, maxB;
    float minL, minA, minB;
    maxL = maxA = maxB = -200; // all values will be above this
    minL = minA = minB = +200; // all values will be below this
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

    void mywrite(string firstLabel, float firstValue, string otherLabels, float [] otherValues)
    {
        writef("%s = %9.4f at ", firstLabel, firstValue);
        static string [] otherFormats = ["%9.4f, ", "%9.4f; ", "%3g, ", "%3g, ", "%3g\n"];
        foreach (l, f, v; zip(otherLabels, otherFormats, otherValues)) write(l, " = ", f.format(v));
    }
    mywrite("maxL", maxL, "ABrgb", abRgbForMaxL);
    mywrite("minL", minL, "ABrgb", abRgbForMinL);
    mywrite("maxA", maxA, "LBrgb", lbRgbForMaxA);
    mywrite("minA", minA, "LBrgb", lbRgbForMinA);
    mywrite("maxB", maxB, "LArgb", laRgbForMaxB);
    mywrite("minB", minB, "LArgb", laRgbForMinB);

    float [3][][][] rgbFromLabMap;
    rgbFromLabMap.reserve(256);
    startTime = MonoTime.currTime;
    foreach (l; 0 .. 101)
    {
        planeSink.clear();
        foreach (a; -128 .. 128)
        {
            rowSink.clear();
            foreach (b; -128 .. 128)
                rowSink ~= rgbFromLab([l, a, b]).toFloat();
            planeSink ~= rowSink.data;
        }
        rgbFromLabMap ~= planeSink.data;
    }
    endTime = MonoTime.currTime;
    writefln("Completed %s calls to rgbFromLab in %.3f seconds", 101 * 256 * 256, (endTime - startTime).total!"msecs" / 1000.0);
    version(writebin) std.file.write("rgbFromLab.bin", pack(rgbFromLabMap));
}
