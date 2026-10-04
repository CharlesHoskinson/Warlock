/* Private read-only Weston observer, compiled with the actual owning headers. */
#include <errno.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <limits.h>
static bool process_started(pid_t pid, char result[21]) {
    if (pid < 2) return false;
    char path[64], data[4096];
    int n = snprintf(path, sizeof path, "/proc/%d/stat", pid);
    if (n <= 0 || (size_t)n >= sizeof path) return false;
    FILE *file = fopen(path, "r"); if (!file) return false;
    size_t size = fread(data, 1, sizeof data - 1, file); bool error = ferror(file); fclose(file);
    if (error || !size || size == sizeof data - 1) return false;
    data[size] = 0; char *cursor = strrchr(data, ')'); if (!cursor) return false;
    cursor++; char *save = NULL; char *token = strtok_r(cursor, " \t\n", &save);
    for (unsigned field = 3; field < 22 && token; field++) token = strtok_r(NULL, " \t\n", &save);
    if (!token || !*token || strlen(token) > 20) return false;
    for (const char *p = token; *p; p++) if (*p < '0' || *p > '9') return false;
    errno = 0; char *end; uintmax_t value = strtoumax(token, &end, 10);
    if (errno || *end || !value || value > UINT64_MAX) return false;
    snprintf(result, 21, "%" PRIuMAX, value); return true;
}
static bool safe_name(const char *text) {
    if (!text || !*text || strlen(text) > 128) return false;
    for (const char *p = text; *p; p++) if (!((*p >= 'a' && *p <= 'z') || (*p >= 'A' && *p <= 'Z') || (*p >= '0' && *p <= '9') || strchr("-_.", *p))) return false;
    return true;
}
static pid_t surface_pid(struct weston_surface *surface, uid_t *uid) {
    pid_t pid = -1; gid_t gid;
    if (surface && surface->resource) wl_client_get_credentials(wl_resource_get_client(surface->resource), &pid, uid, &gid);
    return pid;
}
static void observed_view_destroyed(struct wl_listener *listener, void *data) {
    (void)data; struct probe *probe = wl_container_of(listener, probe, observed_destroy);
    probe->observed_view = NULL;
    wl_list_remove(&probe->observed_destroy.link); wl_list_init(&probe->observed_destroy.link);
}
static bool select_identity(struct probe *probe, struct weston_view *view) {
    if (probe->observed_view == view) return true;
    if (probe->view_identity == UINT32_MAX) return false;
    wl_list_remove(&probe->observed_destroy.link); wl_list_init(&probe->observed_destroy.link);
    probe->observed_view = view; probe->view_identity++;
    wl_signal_add(&view->destroy_signal, &probe->observed_destroy); return true;
}
static bool observation_packet(struct probe *probe, struct wl_client *client, uint32_t sequence, int32_t wanted, const char *started, char packet[4096]) {
    if (!sequence || probe->observation_revision == UINT32_MAX || wanted < 2 || wanted == getpid() || !started ||
        !probe->controller || wl_resource_get_client(probe->controller) != client || !probe->seat) return false;
    char target_start[21], parent_start[21], controller_start[21];
    if (!process_started(wanted, target_start) || strcmp(started, target_start) || !process_started(getpid(), parent_start)) return false;
    pid_t controller_pid; uid_t controller_uid; gid_t controller_gid;
    wl_client_get_credentials(client, &controller_pid, &controller_uid, &controller_gid);
    if (controller_uid != geteuid() || controller_pid == wanted || !process_started(controller_pid, controller_start)) return false;
    struct weston_view *view, *selected = NULL; unsigned count = 0;
    wl_list_for_each(view, &probe->compositor->view_list, link) {
        uid_t uid = (uid_t)-1;
        if (!weston_view_is_mapped(view) || !view->surface || surface_pid(view->surface, &uid) != wanted) continue;
        const char *role = weston_surface_get_role(view->surface);
        if (!role || strcmp(role, "xdg_toplevel") || view->parent_view) continue;
        if (uid != geteuid()) return false;
        selected = view; count++;
    }
    if (count != 1 || !selected) return false;
    if (selected->transform.dirty) return false; /* Owning conversion asserts clean transform; never mutate on query. */
    struct weston_surface *surface = selected->surface;
    if (surface->width < 1 || surface->width > 4096 || surface->height < 1 || surface->height > 4096) return false;
    struct weston_output *output, *chosen = NULL; count = 0;
    wl_list_for_each(output, &probe->compositor->output_list, link) if (output->enabled) { chosen = output; count++; }
    if (count != 1 || !chosen || chosen->width < 1 || chosen->height < 1 || chosen->width > 4096 || chosen->height > 4096 ||
        !chosen->current_mode || chosen->current_mode->width < 1 || chosen->current_mode->height < 1 ||
        chosen->current_mode->width > 8192 || chosen->current_mode->height > 8192 || chosen->current_scale < 1 || chosen->current_scale > 2 || !safe_name(chosen->name)) return false;
    struct weston_coord_global corners[4];
    const double coordinates[4][2] = {{0,0},{surface->width,0},{0,surface->height},{surface->width,surface->height}};
    for (unsigned i = 0; i < 4; i++) {
        corners[i] = weston_coord_surface_to_global(selected, weston_coord_surface(coordinates[i][0], coordinates[i][1], surface));
        if (!isfinite(corners[i].c.x) || !isfinite(corners[i].c.y) || fabs(corners[i].c.x) > INT32_MAX || fabs(corners[i].c.y) > INT32_MAX) return false;
    }
    struct weston_pointer *pointer = weston_seat_get_pointer(probe->seat);
    if (!pointer || !isfinite(pointer->pos.c.x) || !isfinite(pointer->pos.c.y)) return false;
    uid_t focus_uid = (uid_t)-1; pid_t focus_pid = pointer->focus ? surface_pid(pointer->focus->surface, &focus_uid) : -1;
    char focus_start[21] = "0";
    if (focus_pid > 1 && !process_started(focus_pid, focus_start)) return false;
    if (!select_identity(probe, selected)) return false;
    uint32_t revision = probe->observation_revision + 1;
    int size = snprintf(packet, 4096,
        "{\"schema\":1,\"sequence\":%u,\"revision\":%u,\"parent\":{\"pid\":%d,\"started\":\"%s\",\"uid\":%u},"
        "\"controller\":{\"pid\":%d,\"started\":\"%s\"},\"target\":{\"pid\":%d,\"started\":\"%s\"},"
        "\"viewId\":%u,\"surfaceId\":%u,\"surfaceExtent\":[%d,%d],\"corners\":[[%.17g,%.17g],[%.17g,%.17g],[%.17g,%.17g],[%.17g,%.17g]],"
        "\"viewportDestination\":[%d,%d],\"output\":{\"id\":%u,\"name\":\"%s\",\"origin\":[%.17g,%.17g],\"logicalExtent\":[%d,%d],\"modeExtent\":[%d,%d],\"scale\":%d},"
        "\"pointer\":{\"global\":[%.17g,%.17g],\"focusedPid\":%d,\"focusedStarted\":\"%s\",\"focusedViewId\":%u,\"focusedSurfaceId\":%u}}",
        sequence, revision, getpid(), parent_start, (unsigned)geteuid(), controller_pid, controller_start, wanted, target_start,
        probe->view_identity, wl_resource_get_id(surface->resource), surface->width, surface->height,
        corners[0].c.x,corners[0].c.y,corners[1].c.x,corners[1].c.y,corners[2].c.x,corners[2].c.y,corners[3].c.x,corners[3].c.y,
        surface->buffer_viewport.surface.width,surface->buffer_viewport.surface.height,
        chosen->id,chosen->name,chosen->pos.c.x,chosen->pos.c.y,chosen->width,chosen->height,chosen->current_mode->width,chosen->current_mode->height,chosen->current_scale,
        pointer->pos.c.x,pointer->pos.c.y,focus_pid,focus_start,pointer->focus==selected ? probe->view_identity : 0,
        pointer->focus && pointer->focus->surface->resource ? wl_resource_get_id(pointer->focus->surface->resource) : 0);
    if (size < 1 || size >= 4096) return false;
    probe->observation_revision = revision; return true;
}
static void observe_request(struct wl_client *client, struct wl_resource *resource, uint32_t sequence, int32_t pid, const char *started) {
    struct probe *probe = wl_resource_get_user_data(resource); char packet[4096] = "{}";
    bool accepted = observation_packet(probe, client, sequence, pid, started, packet);
    elm_parent_surface_observer_v1_send_observation(resource, sequence, accepted, accepted ? packet : "{}");
}
static void observer_destroyed(struct wl_resource *resource) {
    struct probe *probe = wl_resource_get_user_data(resource); if (probe->observer == resource) probe->observer = NULL;
}
static void observer_destroy_request(struct wl_client *client, struct wl_resource *resource) {(void)client;wl_resource_destroy(resource);}
static const struct elm_parent_surface_observer_v1_interface observer_implementation = {observer_destroy_request,observe_request};
static void bind_observer(struct wl_client *client, void *data, uint32_t version, uint32_t id) {
    (void)version;struct probe *probe=data;pid_t pid;uid_t uid;gid_t gid;
    wl_client_get_credentials(client,&pid,&uid,&gid);
    struct wl_resource *resource=wl_resource_create(client,&elm_parent_surface_observer_v1_interface,1,id);
    if (!resource) {wl_client_post_no_memory(client);return;}
    if (uid!=geteuid() || probe->observer) {wl_resource_post_error(resource,0,"same UID exclusive observer required");return;}
    probe->observer=resource;wl_resource_set_implementation(resource,&observer_implementation,probe,observer_destroyed);
}
