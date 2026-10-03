#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"
g++ -std=c++23 -O2 -fPIC -shared -Wall -Wextra -Werror -MD -MF plugin-production.d plugin-production.cpp -o libomarchy-a11y-prod-v2.so $(pkg-config --cflags --libs hyprland dbus-1 xkbcommon atspi-2 lua wayland-server)
g++ -std=c++23 -O2 -Wall -Wextra -Werror test_lua.cpp -o test_lua $(pkg-config --cflags --libs lua)
./test_lua
