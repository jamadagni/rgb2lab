PREFIX = /usr/local

CFLAGS = -g3 -Wall -Wextra

C_LIB_SOURCES = rgb2lab.c rgb2lab_int.c
C_TARGETS = librgb2lab.so rgb2lab_test

D_TARGETS = extrema
ALL_TARGETS = $(C_TARGETS) $(D_TARGETS)

PY_LIB_SOURCES = labDisplay.py rgb2lab_common.py rgb2lab.py rgb2lab_int.py
PY_LIB_DIR = $(shell python3 -m site | grep "$(PREFIX).*packages'" | cut -d "'" -f2)

lib: librgb2lab.so

install: librgb2lab.so
	install librgb2lab.so $(PREFIX)/lib/
	ldconfig
	install -m 644 $(PY_LIB_SOURCES) $(PY_LIB_DIR)/
	install rgb2lab-gui.py $(PREFIX)/bin/rgb2lab

uninstall:
	rm -f $(PREFIX)/lib/librgb2lab.so
	ldconfig
	rm $(addprefix $(PY_LIB_DIR)/,$(PY_LIB_SOURCES))
	rm $(PREFIX)/bin/rgb2lab

$(C_TARGETS): $(C_LIB_SOURCES) $(C_LIB_SOURCES:.c=.h)

all: $(ALL_TARGETS)

librgb2lab.so:
	$(CC) $(CFLAGS) -fPIC -shared $(C_LIB_SOURCES) -lm -o $@

rgb2lab_test: rgb2lab_test.c
	$(CC) $(CFLAGS) rgb2lab_test.c $(C_LIB_SOURCES) -lm -o $@

extrema: extrema.d rgb2lab.d
	dmd -ofextrema extrema.d rgb2lab.d && rm extrema.o rgb2lab.o

clean:
	rm -f $(ALL_TARGETS)
