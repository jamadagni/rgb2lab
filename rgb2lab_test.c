#include "rgb2lab_int.h"
#include <stdio.h>

int main()
{
    IntTriplet t = {{99, 129, 39}};
    IntTriplet tt = labFromRgbInt(t);
    printf("(%d, %d, %d)\n", tt.L, tt.A, tt.B);

    TinyRgb table[257][257];
    fillTableL_AB(table, 70);
}
