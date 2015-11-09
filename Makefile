CC = clang
CFLAGS = -g3 -Wall -Wextra

LIB_SOURCES = rgb2lab.c rgb2lab_int.c
ALL_TARGETS = librgb2lab.so rgb2lab_test extrema_d

all: $(ALL_TARGETS)
$(ALL_TARGETS): $(LIB_SOURCES) $(LIB_SOURCES:.c=.h)

librgb2lab.so:
	$(CC) $(CFLAGS) -fPIC -shared $(LIB_SOURCES) -lm -o $@

rgb2lab_test: rgb2lab_test.c
	$(CC) $(CFLAGS) rgb2lab_test.c $(LIB_SOURCES) -lm -o $@

extrema_d: extrema.d rgb2lab.d
	dcc -o extrema_d extrema.d rgb2lab.d

clean:
	rm -f $(ALL_TARGETS)
