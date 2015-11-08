#include "rgb2lab_int.h"
#include <stdio.h>

int main()
{
    IntTriplet t = {{99, 129, 39}};
    IntTriplet tt = labFromRgbInt(t);
    printf("(%d, %d, %d)\n", tt.L, tt.A, tt.B);

    TinyRgb table[257][257];
    int validRGBs = fillTableL_AB(table, 70);
    printf("At L = 70, we have %d valid RGB values out of %d possible.\n", validRGBs, 257 * 257);
}
