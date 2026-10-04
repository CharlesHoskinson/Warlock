
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
struct wl_display; struct xdg_toplevel;
struct wl_callback;
struct wl_callback_listener { void (*done)(void*, struct wl_callback*, uint32_t); };
struct wl_callback { const struct wl_callback_listener *listener; void *data; bool destroyed; };
static struct wl_callback callbacks[64];
static unsigned creates, destroys, mutations, doubles;
struct wl_callback *wl_display_sync(struct wl_display *display);
void wl_callback_destroy(struct wl_callback *callback);
int wl_callback_add_listener(struct wl_callback *callback, const struct wl_callback_listener *listener, void *data);
void xdg_toplevel_set_maximized(struct xdg_toplevel *toplevel);
void xdg_toplevel_unset_maximized(struct xdg_toplevel *toplevel);
struct client;
struct barrier {
    struct client *client;
    struct wl_callback *callback;
    uint64_t request_sequence;
    uint32_t request_serial;
    const char *command;
    struct barrier *next;
};
struct buffer {
    struct client *client;
    struct wl_buffer *resource;
    void *data;
    size_t bytes;
    int width, height;
    uint32_t serial;
    struct buffer *next;
};
struct client {
    struct wl_display *display;
    struct wl_registry *registry;
    struct wl_compositor *compositor;
    struct wl_shm *shm;
    struct xdg_wm_base *wm;
    struct wl_surface *surface;
    struct xdg_surface *xdg;
    struct xdg_toplevel *toplevel;
    struct buffer *buffers;
    struct barrier *barriers;
    unsigned inflight, outstanding_barriers;
    uint64_t sequence;
    uint32_t serial, acked;
    int width, height, ordinary_width, ordinary_height, staged_width, staged_height, submitted_width, submitted_height;
    bool maximized, fullscreen, pending_maximized, pending_fullscreen, ready, quit, failed;
    char commands[256];
    size_t command_size;
};
static uint64_t stamp(void) {
    struct timespec time;
    if (clock_gettime(CLOCK_MONOTONIC, &time) != 0) return 0;
    return (uint64_t)time.tv_sec * UINT64_C(1000000000) + (uint64_t)time.tv_nsec;
}
static void event(struct client *client, const char *kind, const char *extra) {
    if (client->sequence == UINT64_MAX) { client->failed = true; client->quit = true; return; }
    printf("{\"event\":\"%s\",\"sequence\":%" PRIu64 ",\"monotonicNs\":%" PRIu64
           ",\"serial\":%u,\"ackedSerial\":%u,\"width\":%d,\"height\":%d,\"maximized\":%s,\"fullscreen\":%s%s}\n",
           kind, ++client->sequence, stamp(), client->serial, client->acked, client->width, client->height,
           client->maximized ? "true" : "false", client->fullscreen ? "true" : "false", extra ? extra : "");
    fflush(stdout);
}
static void refuse(struct client *client, const char *reason) {
    char extra[160];
    snprintf(extra, sizeof extra, ",\"reason\":\"%s\"", reason);
    event(client, "refused", extra);
    client->failed = true; client->quit = true;
}

struct wl_callback *wl_display_sync(struct wl_display *display) {
    (void)display;
    if (creates >= 64) return NULL;
    return &callbacks[creates++];
}
void wl_callback_destroy(struct wl_callback *callback) {
    if (callback->destroyed) { ++doubles; return; }
    callback->destroyed = true; ++destroys;
}
int wl_callback_add_listener(struct wl_callback *callback, const struct wl_callback_listener *listener, void *data) {
    callback->listener = listener; callback->data = data; return 0;
}
void xdg_toplevel_set_maximized(struct xdg_toplevel *toplevel) { (void)toplevel; ++mutations; }
void xdg_toplevel_unset_maximized(struct xdg_toplevel *toplevel) { (void)toplevel; ++mutations; }
static void begin(const char *name) {
    memset(callbacks, 0, sizeof callbacks); creates = destroys = mutations = doubles = 0;
    printf("{\"case\":\"%s\"}\n", name);
}
static void summary(struct client *client, const char *phase) {
    unsigned linked = 0; for (struct barrier *entry = client->barriers; entry; entry = entry->next) ++linked;
    printf("{\"summary\":\"%s\",\"creates\":%u,\"destroys\":%u,\"mutations\":%u,\"doubles\":%u,\"outstanding\":%u,\"linked\":%u,\"quit\":%s,\"failed\":%s}\n",
           phase, creates, destroys, mutations, doubles, client->outstanding_barriers, linked,
           client->quit ? "true" : "false", client->failed ? "true" : "false");
}
static void complete(unsigned index) {
    struct wl_callback *callback = &callbacks[index];
    if (callback->destroyed || !callback->listener) { ++doubles; return; }
    callback->listener->done(callback->data, callback, 1000 + index);
}
static void remove_barrier(struct barrier *barrier) {
    struct client *client = barrier->client;
    struct barrier **entry = &client->barriers;
    while (*entry && *entry != barrier) entry = &(*entry)->next;
    if (*entry) { *entry = barrier->next; --client->outstanding_barriers; }
    (void)barrier->callback;
    free(barrier);
}
static void barrier_done(void *data, struct wl_callback *callback, uint32_t callback_data) {
    (void)callback;
    struct barrier *barrier = data;
    char extra[220];
    snprintf(extra, sizeof extra, ",\"requestSequence\":%" PRIu64 ",\"requestSerial\":%u,\"command\":\"%s\",\"callbackData\":%u",
             barrier->request_sequence, barrier->request_serial, barrier->command, callback_data);
    event(barrier->client, "server-barrier", extra); // Server processing, never configure/pixel completion.
    remove_barrier(barrier);
}
static const struct wl_callback_listener barrier_listener = {barrier_done};
static bool queue_barrier(struct client *client, const char *command) {
    if (client->outstanding_barriers >= 8) { refuse(client, "eight-outstanding-barrier-limit"); return false; }
    struct barrier *barrier = calloc(1, sizeof *barrier);
    if (!barrier) { refuse(client, "barrier-record"); return false; }
    barrier->callback = wl_display_sync(client->display);
    if (!barrier->callback) { free(barrier); refuse(client, "barrier-callback"); return false; }
    barrier->client = client; barrier->request_sequence = client->sequence;
    barrier->request_serial = client->serial; barrier->command = command;
    barrier->next = client->barriers; client->barriers = barrier; ++client->outstanding_barriers;
    wl_callback_add_listener(barrier->callback, &barrier_listener, barrier);
    return true;
}
static void execute(struct client *client, char *command) {
    if (!strcmp(command, "quit")) { event(client, "request", ",\"command\":\"quit\""); client->quit = true; return; }
    if (!strcmp(command, "inspect")) {
        char extra[120]; snprintf(extra, sizeof extra, ",\"bufferWidth\":%d,\"bufferHeight\":%d,\"inflight\":%u", client->submitted_width, client->submitted_height, client->inflight);
        event(client, "inspect", extra); return;
    }
    if (!client->ready) { refuse(client, "command-before-ready"); return; }
    const char *known = NULL;
    if (!strcmp(command, "maximize")) known = "maximize";
    else if (!strcmp(command, "unmaximize")) known = "unmaximize";
    else if (!strcmp(command, "sync")) known = "sync";
    else { refuse(client, "unknown-command"); return; }
    if (client->outstanding_barriers >= 8) { refuse(client, "eight-outstanding-barrier-limit"); return; }
    if (!strcmp(known, "maximize")) xdg_toplevel_set_maximized(client->toplevel);
    else if (!strcmp(known, "unmaximize")) xdg_toplevel_unset_maximized(client->toplevel);
    const char *extra = !strcmp(known, "maximize") ? ",\"command\":\"maximize\"" :
        !strcmp(known, "unmaximize") ? ",\"command\":\"unmaximize\"" : ",\"command\":\"sync\"";
    event(client, "request", extra);
    if (!client->failed) queue_barrier(client, known);

}

static void cleanup(struct client *client) { while (client->barriers) remove_barrier(client->barriers); }
int main(void) {
    begin("multiple-out-of-order");
    struct client first = {.ready=true,.serial=101,.acked=101,.width=320,.height=180};
    execute(&first, "maximize");
    first.serial = 202; execute(&first, "unmaximize");
    first.serial = 303; execute(&first, "sync");
    summary(&first, "before-completion");
    first.serial = 999;
    complete(2); complete(0); complete(1);
    summary(&first, "after-completion");
    cleanup(&first); summary(&first, "after-cleanup");

    begin("limit-before-ninth-mutation");
    struct client full = {.ready=true,.serial=88,.acked=88,.width=320,.height=180};
    for (unsigned index = 0; index < 8; ++index) execute(&full, "maximize");
    summary(&full, "at-eight");
    execute(&full, "unmaximize"); summary(&full, "after-ninth");
    cleanup(&full); summary(&full, "after-cleanup");

    begin("quit-teardown-once");
    struct client quit = {.ready=true,.serial=77,.acked=77,.width=320,.height=180};
    execute(&quit, "maximize"); execute(&quit, "unmaximize"); execute(&quit, "quit");
    cleanup(&quit); summary(&quit, "after-cleanup");
    cleanup(&quit); summary(&quit, "second-cleanup");

    begin("inspect-local-only");
    struct client local = {.ready=true,.serial=55,.acked=55,.width=320,.height=180};
    execute(&local, "inspect"); summary(&local, "after-inspect");
    cleanup(&local);
    return 0;
}
