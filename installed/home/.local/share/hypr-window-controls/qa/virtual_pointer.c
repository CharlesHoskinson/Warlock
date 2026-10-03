#define _POSIX_C_SOURCE 200809L
#include <wayland-client.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "virtual-pointer-client.h"

static struct zwlr_virtual_pointer_manager_v1 *manager;
static void global(void *data, struct wl_registry *registry, uint32_t name, const char *interface, uint32_t version) {
    if (!strcmp(interface, "zwlr_virtual_pointer_manager_v1"))
        manager = wl_registry_bind(registry, name, &zwlr_virtual_pointer_manager_v1_interface, version > 2 ? 2 : version);
}
static void removed(void *data, struct wl_registry *registry, uint32_t name) {}
static const struct wl_registry_listener listener = {global, removed};
static uint32_t milliseconds(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}
int main(int argc, char **argv) {
    if (argc != 3) return 2;
    uint32_t width = atoi(argv[1]), height = atoi(argv[2]);
    if (!width || !height) return 2;
    struct wl_display *display = wl_display_connect(NULL);
    if (!display) return 3;
    struct wl_registry *registry = wl_display_get_registry(display);
    wl_registry_add_listener(registry, &listener, NULL);
    wl_display_roundtrip(display);
    if (!manager) { fprintf(stderr, "Virtual pointer protocol is unavailable\n"); return 4; }
    struct zwlr_virtual_pointer_v1 *pointer = zwlr_virtual_pointer_manager_v1_create_virtual_pointer(manager, NULL);
    wl_display_roundtrip(display);
    char line[200], command[32]; int first, second;
    while (fgets(line, sizeof(line), stdin)) {
        if (sscanf(line, "%31s %d %d", command, &first, &second) < 2) continue;
        if (!strcmp(command, "move"))
            zwlr_virtual_pointer_v1_motion_absolute(pointer, milliseconds(), first, second, width, height);
        else if (!strcmp(command, "button"))
            zwlr_virtual_pointer_v1_button(pointer, milliseconds(), first, second);
        else if (!strcmp(command, "wheel")) {
            zwlr_virtual_pointer_v1_axis_source(pointer, WL_POINTER_AXIS_SOURCE_WHEEL);
            zwlr_virtual_pointer_v1_axis_discrete(pointer, milliseconds(), WL_POINTER_AXIS_VERTICAL_SCROLL,
                wl_fixed_from_int(first), first > 0 ? 1 : -1);
        }
        else if (!strcmp(command, "sleep")) {
            struct timespec ts = {.tv_sec = first / 1000, .tv_nsec = (first % 1000) * 1000000L};
            nanosleep(&ts, NULL);
        }
        zwlr_virtual_pointer_v1_frame(pointer);
        if (wl_display_roundtrip(display) < 0) break;
    }
    // Always release both primary buttons before removing the QA device.
    zwlr_virtual_pointer_v1_button(pointer, milliseconds(), 272, 0);
    zwlr_virtual_pointer_v1_button(pointer, milliseconds(), 273, 0);
    zwlr_virtual_pointer_v1_frame(pointer);
    wl_display_roundtrip(display);
    zwlr_virtual_pointer_v1_destroy(pointer);
    zwlr_virtual_pointer_manager_v1_destroy(manager);
    wl_registry_destroy(registry);
    wl_display_disconnect(display);
    return 0;
}
