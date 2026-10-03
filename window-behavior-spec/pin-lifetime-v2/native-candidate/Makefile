# Else exist specifically for clang
ifeq ($(CXX),g++)
    EXTRA_FLAGS = --no-gnu-unique
else
    EXTRA_FLAGS =
endif

CXXFLAGS ?= -O2
CXXFLAGS += -shared -fPIC -std=c++2b -Wno-c++11-narrowing
INCLUDES = `pkg-config --cflags pixman-1 libdrm hyprland libinput libudev wayland-server xkbcommon libeis-1.0`
LIBS = `pkg-config --libs cairo json-c`

SRC = main.cpp barDeco.cpp BarPassElement.cpp dragBridge.cpp familyBridge.cpp ancestorHit.cpp snapshotBridge.cpp atlasRenderer.cpp atlasAdapter.cpp pinBridge.cpp
TARGET = hyprbars-v24-pin-lifetime-candidate.so

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(EXTRA_FLAGS) $(INCLUDES) $^ $> -o $@ $(LIBS)

clean:
	rm ./$(TARGET)

meson-build:
	mkdir -p build
	cd build && meson .. && ninja

.PHONY: all meson-build clean
