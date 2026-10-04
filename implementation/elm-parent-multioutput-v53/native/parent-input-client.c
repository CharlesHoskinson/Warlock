#define _POSIX_C_SOURCE 200809L
#include "parent-input-client.h"
#include <wayland-client.h>
#include <stdbool.h>
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

struct client { struct wl_display *display; struct elm_parent_input_v1 *probe; uint32_t global, sequence, waiting; bool received, accepted; };
static void done(void *data, struct elm_parent_input_v1 *probe, uint32_t sequence, uint32_t accepted) {
    (void)probe;
    struct client *client = data;
    if (sequence != client->waiting || accepted > 1) return;
    client->received = true; client->accepted = accepted;
    printf("{\"sequence\":%u,\"accepted\":%s,\"scope\":\"parent-notify-only\"}\n", sequence, accepted ? "true" : "false");
    fflush(stdout);
}
static const struct elm_parent_input_v1_listener listener = {done};
static void global(void *data, struct wl_registry *registry, uint32_t name, const char *interface, uint32_t version) {
    struct client *client = data;
    if (!strcmp(interface, "elm_parent_input_v1") && version >= 2 && !client->probe) {
        client->global = name;
        client->probe = wl_registry_bind(registry, name, &elm_parent_input_v1_interface, 2);
        elm_parent_input_v1_add_listener(client->probe, &listener, client);
    }
}
static void removed(void *data, struct wl_registry *registry, uint32_t name) {
    (void)registry;
    struct client *client = data;
    if (name == client->global && client->probe) {
        elm_parent_input_v1_destroy(client->probe); client->probe = NULL;
    }
}
static const struct wl_registry_listener registry_listener = {global, removed};
static bool private_socket(void) {
    const char *gate = getenv("ELM_PARENT_INPUT_QA"), *socket = getenv("WAYLAND_DISPLAY"), *runtime = getenv("XDG_RUNTIME_DIR");
    if (!gate || strcmp(gate, "1") || !socket || !*socket) return false;
    char path[4096];
    int count = socket[0] == '/' ? snprintf(path, sizeof path, "%s", socket) :
        runtime ? snprintf(path, sizeof path, "%s/%s", runtime, socket) : -1;
    if (count < 0 || (size_t)count >= sizeof path) return false;
    struct stat info;
    return lstat(path, &info) == 0 && S_ISSOCK(info.st_mode) && info.st_uid == geteuid();
}
static bool send_request(struct client *client, bool motion, int32_t x, int32_t y, uint32_t button, uint32_t state) {
    if (!client->probe || client->sequence == UINT32_MAX) return false;
    client->waiting = ++client->sequence; client->received = false;
    if (motion) elm_parent_input_v1_motion(client->probe, client->waiting, x, y);
    else elm_parent_input_v1_button(client->probe, client->waiting, button, state);
    while (!client->received) if (wl_display_dispatch(client->display) < 0) return false;
    return client->accepted;
}
static bool send_capability(struct client *client, uint32_t enabled) {
    if (!client->probe || client->sequence == UINT32_MAX) return false;
    client->waiting = ++client->sequence; client->received = false;
    elm_parent_input_v1_pointer_capability(client->probe, client->waiting, enabled);
    while (!client->received) if (wl_display_dispatch(client->display) < 0) return false;
    return client->accepted;
}
static bool number(const char *text, int64_t minimum, int64_t maximum, int64_t *value) {
    if (!text || !*text) return false;
    errno = 0; char *end = NULL;
    intmax_t parsed = strtoimax(text, &end, 10);
    if (errno || !end || *end || parsed < minimum || parsed > maximum) return false;
    *value = parsed; return true;
}
int main(void) {
    if (!private_socket()) { fputs("private owned QA socket required\n", stderr); return 2; }
    struct client client = {0};
    client.display = wl_display_connect(NULL);
    if (!client.display) return 3;
    struct wl_registry *registry = wl_display_get_registry(client.display);
    wl_registry_add_listener(registry, &registry_listener, &client);
    if (wl_display_roundtrip(client.display) < 0 || !client.probe) { wl_display_disconnect(client.display); return 4; }
    puts("{\"ready\":true,\"scope\":\"parent-notify-only\"}"); fflush(stdout);
    char line[256];
    int result = 0;
    while (fgets(line, sizeof line, stdin)) {
        bool accepted = false;
        if (!strchr(line, '\n') && !feof(stdin)) { result = 5; break; }
        char *save = NULL;
        char *command = strtok_r(line, " \t\r\n", &save);
        char *one = strtok_r(NULL, " \t\r\n", &save);
        char *two = strtok_r(NULL, " \t\r\n", &save);
        char *extra = strtok_r(NULL, " \t\r\n", &save);
        int64_t first, second;
        if (command && !strcmp(command, "quit") && !one) break;
        if (command && !strcmp(command, "motion") && one && two && !extra &&
            number(one, INT32_MIN, INT32_MAX, &first) && number(two, INT32_MIN, INT32_MAX, &second))
            accepted = send_request(&client, true, (int32_t)first, (int32_t)second, 0, 0);
        else if (command && (!strcmp(command, "press") || !strcmp(command, "release")) && one && !two &&
            number(one, 0, UINT32_MAX, &first))
            accepted = send_request(&client, false, 0, 0, (uint32_t)first, !strcmp(command, "press"));
        else if (command && !strcmp(command, "pointer-capability") && one && !two && number(one, 0, 1, &first))
            accepted = send_capability(&client, (uint32_t)first);
        else { fputs("commands: motion X Y; press BUTTON; release BUTTON; pointer-capability 0|1; quit\n", stderr); result = 5; break; }
        if (!accepted) { result = 6; break; }
    }
    if (client.probe) { elm_parent_input_v1_destroy(client.probe); if (wl_display_roundtrip(client.display) < 0 && !result) result = 7; }
    wl_registry_destroy(registry);
    wl_display_disconnect(client.display);
    return result;
}
