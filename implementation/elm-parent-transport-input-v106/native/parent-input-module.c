#define _POSIX_C_SOURCE 200809L
#include <libweston/libweston.h>
#include "libweston/backend.h"
#include "libweston/libweston-internal.h"
#include "parent-input-server.h"
#include <linux/input-event-codes.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

struct probe {
    struct weston_compositor *compositor;
    struct weston_seat *seat;
    struct wl_global *global;
    struct wl_resource *controller;
    struct wl_listener destroy, seat_destroy;
    bool held[3];
};
static const uint32_t buttons[3] = {BTN_LEFT, BTN_RIGHT, BTN_MIDDLE};
static bool clock_now(struct timespec *time) { return clock_gettime(CLOCK_MONOTONIC, time) == 0; }
static pid_t focused_pid(struct weston_pointer *pointer) {
    if (!pointer || !pointer->focus || !pointer->focus->surface ||
        !pointer->focus->surface->resource) return -1;
    pid_t pid = -1; uid_t uid; gid_t gid;
    wl_client_get_credentials(wl_resource_get_client(pointer->focus->surface->resource),
                              &pid, &uid, &gid);
    return pid;
}
static void release_all(struct probe *probe) {
    struct timespec time;
    if (!probe->seat || !weston_seat_get_pointer(probe->seat) || !clock_now(&time)) return;
    for (size_t i = 0; i < 3; ++i) if (probe->held[i]) {
        notify_button(probe->seat, &time, buttons[i], WL_POINTER_BUTTON_STATE_RELEASED);
        probe->held[i] = false;
    }
    notify_pointer_frame(probe->seat);
}
static void resource_destroyed(struct wl_resource *resource) {
    struct probe *probe = wl_resource_get_user_data(resource);
    if (probe->controller != resource) return;
    release_all(probe);
    probe->controller = NULL;
}
static void destroy_request(struct wl_client *client, struct wl_resource *resource) {
    (void)client; wl_resource_destroy(resource);
}
static bool valid_point(struct probe *probe, int32_t x, int32_t y) {
    struct weston_output *output;
    unsigned count = 0;
    bool contains = false;
    if (x < 0 || y < 0 || x > 4095 || y > 4095) return false;
    wl_list_for_each(output, &probe->compositor->output_list, link) {
        if (!output->enabled) continue;
        ++count;
        contains = x >= output->pos.c.x && y >= output->pos.c.y &&
            (int64_t)x < (int64_t)output->pos.c.x + output->width &&
            (int64_t)y < (int64_t)output->pos.c.y + output->height;
    }
    return count == 1 && contains;
}
static void motion_request(struct wl_client *client, struct wl_resource *resource, uint32_t sequence, int32_t x, int32_t y) {
    (void)client;
    struct probe *probe = wl_resource_get_user_data(resource);
    struct timespec time;
    bool accepted = probe->seat && weston_seat_get_pointer(probe->seat) && sequence && valid_point(probe, x, y) && clock_now(&time);
    if (accepted) {
        struct weston_coord_global position = {.c = weston_coord(x, y)};
        notify_motion_absolute(probe->seat, &time, position);
        notify_pointer_frame(probe->seat);
        struct weston_pointer *pointer = weston_seat_get_pointer(probe->seat);
        weston_log("elm-parent-input motion %d,%d actual %.2f,%.2f focus=%p pid=%ld\n",
                   x, y, pointer->pos.c.x, pointer->pos.c.y, (void *)pointer->focus,
                   (long)focused_pid(pointer));
    }
    elm_parent_input_v1_send_done(resource, sequence, accepted);
}
static void button_request(struct wl_client *client, struct wl_resource *resource, uint32_t sequence, uint32_t button, uint32_t state) {
    (void)client;
    struct probe *probe = wl_resource_get_user_data(resource);
    struct timespec time;
    bool accepted = false;
    if (!probe->seat || !weston_seat_get_pointer(probe->seat)) { elm_parent_input_v1_send_done(resource, sequence, false); return; }
    for (size_t i = 0; i < 3; ++i) {
        if (!sequence || button != buttons[i] || state > 1 || probe->held[i] == (state == 1) || !clock_now(&time)) continue;
        notify_button(probe->seat, &time, button, state);
        probe->held[i] = state == 1;
        notify_pointer_frame(probe->seat);
        struct weston_pointer *pointer = weston_seat_get_pointer(probe->seat);
        weston_log("elm-parent-input button %u state=%u focus=%p pid=%ld\n",
                   button, state, (void *)pointer->focus, (long)focused_pid(pointer));
        accepted = true; break;
    }
    elm_parent_input_v1_send_done(resource, sequence, accepted);
}
static void pointer_capability_request(struct wl_client *client, struct wl_resource *resource, uint32_t sequence, uint32_t enabled) {
    (void)client;
    struct probe *probe = wl_resource_get_user_data(resource);
    bool accepted = false;
    if (sequence && enabled <= 1 && probe->seat) {
        if (enabled && probe->seat->pointer_device_count == 0) {
            accepted = weston_seat_init_pointer(probe->seat) == 0;
        } else if (!enabled && probe->seat->pointer_device_count == 1) {
            release_all(probe);
            weston_seat_release_pointer(probe->seat);
            accepted = probe->seat->pointer_device_count == 0;
        }
        weston_log("elm-parent-input capability requested=%u actual=%d accepted=%d\n", enabled, probe->seat->pointer_device_count, accepted);
    }
    elm_parent_input_v1_send_done(resource, sequence, accepted);
}
// One server request queues all capability changes before returning to the
// Wayland event loop. Uses the exact owning seat APIs and balanced release path.
static void pointer_burst_request(struct wl_client *client, struct wl_resource *resource, uint32_t sequence, uint32_t cycles, uint32_t enabled) {
    (void)client;
    struct probe *probe = wl_resource_get_user_data(resource);
    bool accepted = sequence && cycles >= 1 && cycles <= 16 && enabled <= 1 && probe->seat && probe->seat->pointer_device_count == 1;
    if (accepted) {
        for (uint32_t i = 0; i < cycles; ++i) {
            release_all(probe);
            weston_seat_release_pointer(probe->seat);
            if (probe->seat->pointer_device_count != 0 || weston_seat_init_pointer(probe->seat) != 0) { accepted = false; break; }
        }
        if (accepted && !enabled) { release_all(probe); weston_seat_release_pointer(probe->seat); }
        accepted = accepted && probe->seat->pointer_device_count == (int)enabled;
        weston_log("elm-parent-input burst cycles=%u final=%u actual=%d accepted=%d\n", cycles, enabled, probe->seat->pointer_device_count, accepted);
    }
    elm_parent_input_v1_send_done(resource, sequence, accepted);
}
static const struct elm_parent_input_v1_interface implementation = {destroy_request, motion_request, button_request, pointer_capability_request, pointer_burst_request};
static void bind_probe(struct wl_client *client, void *data, uint32_t version, uint32_t id) {
    struct probe *probe = data;
    pid_t pid; uid_t uid; gid_t gid;
    wl_client_get_credentials(client, &pid, &uid, &gid);
    struct wl_resource *resource = wl_resource_create(client, &elm_parent_input_v1_interface, version < 3 ? version : 3, id);
    if (!resource) { wl_client_post_no_memory(client); return; }
    if (uid != geteuid() || probe->controller) {
        wl_resource_post_error(resource, 0, "private probe requires same UID and exclusive controller");
        return;
    }
    probe->controller = resource;
    wl_resource_set_implementation(resource, &implementation, probe, resource_destroyed);
}
static void seat_destroyed(struct wl_listener *listener, void *data) {
    (void)data;
    struct probe *probe = wl_container_of(listener, probe, seat_destroy);
    // Weston destroys pointer_state before emitting seat.destroy_signal.
    // No pointer notification is valid at this retirement boundary.
    probe->seat = NULL;
    memset(probe->held, 0, sizeof probe->held);
    wl_list_remove(&probe->seat_destroy.link);
    wl_list_init(&probe->seat_destroy.link);
}
static void compositor_destroyed(struct wl_listener *listener, void *data) {
    (void)data;
    struct probe *probe = wl_container_of(listener, probe, destroy);
    if (probe->controller) wl_resource_destroy(probe->controller);
    wl_global_destroy(probe->global);
    wl_list_remove(&probe->destroy.link);
    wl_list_remove(&probe->seat_destroy.link);
    free(probe);
}
WL_EXPORT int wet_module_init(struct weston_compositor *compositor, int *argc, char *argv[]) {
    (void)argc; (void)argv;
    const char *gate = getenv("ELM_PARENT_INPUT_QA");
    if (!gate || strcmp(gate, "1")) return -1;
    struct weston_seat *seat, *selected = NULL;
    unsigned count = 0;
    wl_list_for_each(seat, &compositor->seat_list, link) {
        ++count;
        if (seat->seat_name && !strcmp(seat->seat_name, "default") && weston_seat_get_pointer(seat)) selected = seat;
    }
    if (count != 1 || !selected || selected->pointer_device_count != 1) return -1;
    struct probe *probe = calloc(1, sizeof *probe);
    if (!probe) return -1;
    probe->compositor = compositor; probe->seat = selected;
    probe->global = wl_global_create(compositor->wl_display, &elm_parent_input_v1_interface, 3, probe, bind_probe);
    if (!probe->global) { free(probe); return -1; }
    probe->seat_destroy.notify = seat_destroyed;
    wl_signal_add(&selected->destroy_signal, &probe->seat_destroy);
    probe->destroy.notify = compositor_destroyed;
    wl_signal_add(&compositor->destroy_signal, &probe->destroy);
    return 0;
}
