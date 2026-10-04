#define _GNU_SOURCE
#include <wayland-client.h>
#include "xdg-shell-client.h"
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <poll.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

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
    bool maximized, fullscreen, suspended, pending_maximized, pending_fullscreen, pending_suspended, ready, quit, failed;
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
           ",\"serial\":%u,\"ackedSerial\":%u,\"width\":%d,\"height\":%d,\"maximized\":%s,\"fullscreen\":%s,\"suspended\":%s%s}\n",
           kind, ++client->sequence, stamp(), client->serial, client->acked, client->width, client->height,
           client->maximized ? "true" : "false", client->fullscreen ? "true" : "false", client->suspended ? "true" : "false", extra ? extra : "");
    fflush(stdout);
}
static void refuse(struct client *client, const char *reason) {
    char extra[160];
    snprintf(extra, sizeof extra, ",\"reason\":\"%s\"", reason);
    event(client, "refused", extra);
    client->failed = true; client->quit = true;
}
static void remove_buffer(struct buffer *buffer) {
    struct client *client = buffer->client;
    struct buffer **entry = &client->buffers;
    while (*entry && *entry != buffer) entry = &(*entry)->next;
    if (*entry) { *entry = buffer->next; --client->inflight; }
    wl_buffer_destroy(buffer->resource);
    munmap(buffer->data, buffer->bytes);
    free(buffer);
}
static void released(void *data, struct wl_buffer *resource) {
    (void)resource;
    struct buffer *buffer = data;
    char extra[160];
    snprintf(extra, sizeof extra, ",\"bufferSerial\":%u,\"bufferWidth\":%d,\"bufferHeight\":%d", buffer->serial, buffer->width, buffer->height);
    event(buffer->client, "buffer-release", extra);
    remove_buffer(buffer);
}
static const struct wl_buffer_listener buffer_listener = {released};
static bool commit_buffer(struct client *client) {
    if (client->inflight >= 8) { refuse(client, "eight-inflight-buffer-limit"); return false; }
    int stride = client->width * 4;
    size_t bytes = (size_t)stride * (size_t)client->height;
    int fd = memfd_create("elm-maximize-probe", MFD_CLOEXEC);
    if (fd < 0 || ftruncate(fd, (off_t)bytes) != 0) { if (fd >= 0) close(fd); refuse(client, "memfd-allocation"); return false; }
    void *pixels = mmap(NULL, bytes, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (pixels == MAP_FAILED) { close(fd); refuse(client, "shm-mapping"); return false; }
    // Injective color for the serial low 18 bits; the native runner selects
    // unique serial colors and verifies pixels separately from queued commits.
    uint32_t red = UINT32_C(0x28) ^ (client->acked & UINT32_C(63));
    uint32_t green = UINT32_C(0x71) ^ ((client->acked >> 6) & UINT32_C(63));
    uint32_t blue = UINT32_C(0xc8) ^ ((client->acked >> 12) & UINT32_C(63));
    uint32_t argb = UINT32_C(0xff000000) | (red << 16) | (green << 8) | blue;
    for (size_t i = 0; i < bytes / sizeof(uint32_t); ++i) ((uint32_t *)pixels)[i] = argb;
    struct wl_shm_pool *pool = wl_shm_create_pool(client->shm, fd, (int)bytes);
    struct wl_buffer *resource = pool ? wl_shm_pool_create_buffer(pool, 0, client->width, client->height, stride, WL_SHM_FORMAT_ARGB8888) : NULL;
    if (pool) wl_shm_pool_destroy(pool);
    close(fd);
    if (!resource) { munmap(pixels, bytes); refuse(client, "shm-buffer"); return false; }
    struct buffer *buffer = calloc(1, sizeof *buffer);
    if (!buffer) { wl_buffer_destroy(resource); munmap(pixels, bytes); refuse(client, "buffer-record"); return false; }
    *buffer = (struct buffer){.client=client,.resource=resource,.data=pixels,.bytes=bytes,.width=client->width,.height=client->height,.serial=client->acked,.next=client->buffers};
    client->buffers = buffer; ++client->inflight;
    wl_buffer_add_listener(resource, &buffer_listener, buffer);
    xdg_surface_set_window_geometry(client->xdg, 0, 0, client->width, client->height);
    wl_surface_attach(client->surface, resource, 0, 0);
    wl_surface_damage(client->surface, 0, 0, client->width, client->height);
    wl_surface_commit(client->surface);
    if (wl_display_flush(client->display) < 0 && errno != EAGAIN) { refuse(client, "commit-transport"); return false; }
    client->submitted_width = client->width; client->submitted_height = client->height;
    char extra[160];
    snprintf(extra, sizeof extra, ",\"bufferWidth\":%d,\"bufferHeight\":%d,\"inflight\":%u,\"argb\":\"%08" PRIx32 "\"", client->width, client->height, client->inflight, argb);
    event(client, "buffercommit", extra); // Queued commit, never a pixel/presentation receipt.
    return true;
}
static void surface_configure(void *data, struct xdg_surface *surface, uint32_t serial) {
    struct client *client = data;
    if (client->quit) return;
    if (client->staged_width < 0 || client->staged_height < 0 || client->staged_width > 4096 || client->staged_height > 4096) {
        refuse(client, "invalid-configure-dimensions"); return;
    }
    client->serial = serial;
    client->maximized = client->pending_maximized; client->fullscreen = client->pending_fullscreen; client->suspended = client->pending_suspended;
    client->width = client->staged_width ? client->staged_width : (client->maximized || client->fullscreen ? client->width : client->ordinary_width);
    client->height = client->staged_height ? client->staged_height : (client->maximized || client->fullscreen ? client->height : client->ordinary_height);
    if (!client->maximized && !client->fullscreen) { client->ordinary_width = client->width; client->ordinary_height = client->height; }
    xdg_surface_ack_configure(surface, serial);
    client->acked = serial;
    char extra[120];
    snprintf(extra, sizeof extra, ",\"configuredWidth\":%d,\"configuredHeight\":%d", client->staged_width, client->staged_height);
    event(client, "configure", extra);
    if (!commit_buffer(client)) return;
    if (!client->ready) { client->ready = true; event(client, "ready", ",\"title\":\"ELM-MAXIMIZE-PROBE\",\"appId\":\"elm-maximize-probe\""); }
}
static const struct xdg_surface_listener surface_listener = {surface_configure};
static void toplevel_configure(void *data, struct xdg_toplevel *toplevel, int32_t width, int32_t height, struct wl_array *states) {
    (void)toplevel;
    struct client *client = data;
    if (width < 0 || height < 0 || width > 4096 || height > 4096 || states->size % sizeof(uint32_t)) { refuse(client, "invalid-toplevel-configure"); return; }
    client->staged_width = width; client->staged_height = height;
    client->pending_maximized = false; client->pending_fullscreen = false; client->pending_suspended = false;
    for (size_t offset = 0; offset < states->size; offset += sizeof(uint32_t)) {
        uint32_t value; memcpy(&value, (char *)states->data + offset, sizeof value);
        client->pending_maximized |= value == XDG_TOPLEVEL_STATE_MAXIMIZED;
        client->pending_fullscreen |= value == XDG_TOPLEVEL_STATE_FULLSCREEN;
        client->pending_suspended |= value == XDG_TOPLEVEL_STATE_SUSPENDED;
    }
}
static void close_toplevel(void *data, struct xdg_toplevel *toplevel) {
    (void)toplevel; struct client *client = data; event(client, "server-close", NULL); client->quit = true;
}
static void configure_bounds(void *data, struct xdg_toplevel *toplevel, int32_t width, int32_t height) {
    (void)toplevel;
    if (width < 0 || height < 0 || width > 4096 || height > 4096) refuse(data, "invalid-configure-bounds");
}
static void wm_capabilities(void *data, struct xdg_toplevel *toplevel, struct wl_array *caps) { (void)data; (void)toplevel; (void)caps; }
static const struct xdg_toplevel_listener toplevel_listener = {toplevel_configure, close_toplevel, configure_bounds, wm_capabilities};
static void ping(void *data, struct xdg_wm_base *wm, uint32_t serial) { (void)data; xdg_wm_base_pong(wm, serial); }
static const struct xdg_wm_base_listener wm_listener = {ping};
static void registry_global(void *data, struct wl_registry *registry, uint32_t name, const char *interface, uint32_t version) {
    struct client *client = data;
    if (!strcmp(interface, "wl_compositor") && !client->compositor && version >= 1)
        client->compositor = wl_registry_bind(registry, name, &wl_compositor_interface, version < 4 ? version : 4);
    else if (!strcmp(interface, "wl_shm") && !client->shm)
        client->shm = wl_registry_bind(registry, name, &wl_shm_interface, 1);
    else if (!strcmp(interface, "xdg_wm_base") && !client->wm && version >= 6) {
        client->wm = wl_registry_bind(registry, name, &xdg_wm_base_interface, 6);
        xdg_wm_base_add_listener(client->wm, &wm_listener, client);
    }
}
static void global_removed(void *data, struct wl_registry *registry, uint32_t name) { (void)data; (void)registry; (void)name; }
static const struct wl_registry_listener registry_listener = {registry_global, global_removed};
static void remove_barrier(struct barrier *barrier) {
    struct client *client = barrier->client;
    struct barrier **entry = &client->barriers;
    while (*entry && *entry != barrier) entry = &(*entry)->next;
    if (*entry) { *entry = barrier->next; --client->outstanding_barriers; }
    wl_callback_destroy(barrier->callback);
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
static void stdin_ready(struct client *client) {
    char bytes[256];
    ssize_t count = read(STDIN_FILENO, bytes, sizeof bytes);
    if (count < 0) { if (errno != EAGAIN && errno != EINTR) refuse(client, "stdin-read"); return; }
    if (!count) { if (client->command_size) refuse(client, "partial-command-at-eof"); else client->quit = true; return; }
    for (ssize_t i = 0; i < count && !client->quit; ++i) {
        if (bytes[i] == '\n') { client->commands[client->command_size] = 0; execute(client, client->commands); client->command_size = 0; }
        else if (bytes[i] == '\0' || client->command_size >= sizeof client->commands - 1) { refuse(client, "command-bound"); return; }
        else client->commands[client->command_size++] = bytes[i];
    }
}
int main(void) {
    struct client client = {.width=320,.height=180,.ordinary_width=320,.ordinary_height=180};
    client.display = wl_display_connect(NULL);
    if (!client.display) return 2;
    client.registry = wl_display_get_registry(client.display);
    wl_registry_add_listener(client.registry, &registry_listener, &client);
    if (wl_display_roundtrip(client.display) < 0 || !client.compositor || !client.shm || !client.wm) { wl_display_disconnect(client.display); return 3; }
    client.surface = wl_compositor_create_surface(client.compositor);
    client.xdg = xdg_wm_base_get_xdg_surface(client.wm, client.surface);
    xdg_surface_add_listener(client.xdg, &surface_listener, &client);
    client.toplevel = xdg_surface_get_toplevel(client.xdg);
    xdg_toplevel_add_listener(client.toplevel, &toplevel_listener, &client);
    xdg_toplevel_set_title(client.toplevel, "ELM-MAXIMIZE-PROBE");
    xdg_toplevel_set_app_id(client.toplevel, "elm-maximize-probe");
    wl_surface_commit(client.surface); // Initial role-only commit must precede configure.
    int flags = fcntl(STDIN_FILENO, F_GETFL);
    if (flags < 0 || fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK) < 0) refuse(&client, "stdin-nonblocking");
    while (!client.quit) {
        bool prepared = false;
        while (!client.quit) {
            if (wl_display_prepare_read(client.display) == 0) { prepared = true; break; }
            if (wl_display_dispatch_pending(client.display) < 0) { refuse(&client, "dispatch-pending"); break; }
        }
        if (!prepared) break;
        int flushed = wl_display_flush(client.display);
        if (flushed < 0 && errno != EAGAIN) { wl_display_cancel_read(client.display); refuse(&client, "flush-transport"); break; }
        struct pollfd pollfds[2] = {{.fd=wl_display_get_fd(client.display),.events=POLLIN | (flushed < 0 ? POLLOUT : 0)}, {.fd=STDIN_FILENO,.events=POLLIN}};
        int result = poll(pollfds, 2, -1);
        if (result < 0) { wl_display_cancel_read(client.display); if (errno == EINTR) continue; refuse(&client, "poll"); break; }
        if (pollfds[0].revents & POLLIN) {
            if (wl_display_read_events(client.display) < 0 || wl_display_dispatch_pending(client.display) < 0) { refuse(&client, "read-transport"); break; }
        } else wl_display_cancel_read(client.display);
        if (pollfds[0].revents & (POLLERR | POLLHUP | POLLNVAL)) { refuse(&client, "display-disconnected"); break; }
        if (!client.quit && pollfds[1].revents & (POLLIN | POLLHUP)) stdin_ready(&client);
        if (pollfds[1].revents & (POLLERR | POLLNVAL)) { refuse(&client, "stdin-disconnected"); break; }
    }
    if (flags >= 0) fcntl(STDIN_FILENO, F_SETFL, flags);
    while (client.barriers) remove_barrier(client.barriers);
    xdg_toplevel_destroy(client.toplevel); xdg_surface_destroy(client.xdg); wl_surface_destroy(client.surface);
    while (client.buffers) remove_buffer(client.buffers); // Teardown only; no reuse/eviction of inflight pixels.
    xdg_wm_base_destroy(client.wm); wl_shm_destroy(client.shm); wl_compositor_destroy(client.compositor); wl_registry_destroy(client.registry);
    if (!client.failed && wl_display_flush(client.display) < 0 && errno != EAGAIN) client.failed = true;
    wl_display_disconnect(client.display);
    if (!client.failed) event(&client, "normalexit", NULL);
    return client.failed ? 1 : 0;
}
