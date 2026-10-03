CXX ?= c++
CPPFLAGS += $(shell pkg-config --cflags pixman-1 libdrm hyprland libinput libudev wayland-server xkbcommon libeis-1.0)
CXXFLAGS += -O2 -shared -fPIC -fno-gnu-unique -std=c++2b -Wall -Wextra -Wno-unused-parameter
# Always build a fresh filename: a loaded shared library must never be rewritten.
TARGET ?= content-probe-v1.so
$(TARGET): probe.cpp
	@test ! -e $@ || { echo 'Choose a fresh TARGET before rebuilding'; exit 1; }
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $< -o $@
