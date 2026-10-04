
#define _POSIX_C_SOURCE 200809L
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <wayland-client.h>
#include "xdg-shell-client.h"
struct buffer;struct barrier;
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

static uint32_t ack;
static unsigned commits, refused_count, bindings, bound_version;
static void refuse(struct client *client,const char *reason){(void)reason;++refused_count;client->failed=true;client->quit=true;}
static void test_ack(struct xdg_surface *surface,uint32_t serial){(void)surface;ack=serial;}
#define xdg_surface_ack_configure test_ack
static bool commit_buffer(struct client *client){if(client->acked!=ack)return false;++commits;event(client,"buffercommit",NULL);return true;}
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
        
    }
}

static const struct xdg_wm_base_listener wm_listener={0};
static void *test_bind(struct wl_registry *registry,uint32_t name,const struct wl_interface *interface,uint32_t version){(void)registry;(void)name;(void)interface;++bindings;bound_version=version;return (void *)(uintptr_t)1;}
#define wl_registry_bind test_bind
static int test_listener(struct xdg_wm_base *wm,const struct xdg_wm_base_listener *listener,void *data){(void)wm;(void)listener;(void)data;return 0;}
#define xdg_wm_base_add_listener test_listener
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

static unsigned checks;
static bool check(bool value,const char *name){++checks;if(!value)fprintf(stderr,"FAIL %s\n",name);return value;}
#define CHECK(v,n) if(!check((v),(n)))return 1
int main(void){
 struct client c={.width=320,.height=180,.ordinary_width=320,.ordinary_height=180};
 for(uint32_t version=1;version<6;++version){registry_global(&c,NULL,4,"xdg_wm_base",version);CHECK(!c.wm&&!bindings,"pre-v6 cannot qualify suspend readiness");}
 registry_global(&c,NULL,4,"xdg_wm_base",6);CHECK(c.wm&&bindings==1&&bound_version==6,"actual v6 bound exactly");
 registry_global(&c,NULL,4,"xdg_wm_base",7);CHECK(bindings==1,"duplicate registry announcement cannot replace bound role");
 struct client newer={0};registry_global(&newer,NULL,4,"xdg_wm_base",9);CHECK(newer.wm&&bound_version==6,"newer role bounded to supported v6");
 uint32_t max_suspended[]={XDG_TOPLEVEL_STATE_MAXIMIZED,XDG_TOPLEVEL_STATE_SUSPENDED};
 struct wl_array states={.size=sizeof max_suspended,.alloc=sizeof max_suspended,.data=max_suspended};
 toplevel_configure(&c,NULL,798,598,&states);
 CHECK(c.pending_maximized&&!c.pending_fullscreen&&c.pending_suspended&&!c.maximized&&!c.suspended&&c.width==320,"staged flags cannot alter current before surface ACK");
 surface_configure(&c,NULL,41);
 CHECK(c.maximized&&!c.fullscreen&&c.suspended&&c.serial==41&&c.acked==41&&ack==41&&commits==1,"MAX plus SUSPENDED promotes only with ACK");
 uint32_t full_suspended[]={XDG_TOPLEVEL_STATE_FULLSCREEN,XDG_TOPLEVEL_STATE_SUSPENDED};states.data=full_suspended;states.size=sizeof full_suspended;
 toplevel_configure(&c,NULL,800,600,&states);CHECK(c.maximized&&c.suspended&&c.pending_fullscreen&&!c.pending_maximized,"next stage retains prior committed snapshot");
 surface_configure(&c,NULL,42);CHECK(!c.maximized&&c.fullscreen&&c.suspended&&commits==2,"FULLSCREEN and SUSPENDED independently promoted");
 uint32_t max_only[]={XDG_TOPLEVEL_STATE_MAXIMIZED};states.data=max_only;states.size=sizeof max_only;
 toplevel_configure(&c,NULL,798,598,&states);surface_configure(&c,NULL,43);
 CHECK(c.maximized&&!c.fullscreen&&!c.suspended&&!c.pending_suspended&&commits==3,"restore-minimized MAX clears suspended at fresh ACK");
 states.data=NULL;states.size=0;toplevel_configure(&c,NULL,320,180,&states);surface_configure(&c,NULL,44);
 CHECK(!c.maximized&&!c.fullscreen&&!c.suspended&&c.width==320&&c.height==180&&commits==4,"ordinary geometry clears all flags");
 states.size=1;toplevel_configure(&c,NULL,320,180,&states);CHECK(c.failed&&refused_count==1,"malformed state array refused");
 surface_configure(&c,NULL,45);CHECK(commits==4,"refused lifecycle cannot create new queued buffer");
 fprintf(stderr,"checks %u\n",checks);return 0;
}
