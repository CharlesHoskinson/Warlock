#define _GNU_SOURCE
#include <wayland-client.h>
#include "xdg-shell-client.h"
#include "xdg-dialog-client.h"
#include "background-effect-client.h"
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
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

struct client;
struct buffer {struct client *client;struct wl_buffer *resource;void *data;size_t bytes;struct buffer *next;};
struct barrier {struct client *client;struct wl_callback *callback;uint64_t control;const char *command;struct barrier *next;};
struct client {
    struct wl_display *display;struct wl_registry *registry;
    struct wl_compositor *compositor;struct wl_subcompositor *subcompositor;struct wl_shm *shm;struct xdg_wm_base *wm;
    struct xdg_wm_dialog_v1 *dialog_manager;
    struct ext_background_effect_manager_v1 *background_manager;struct ext_background_effect_surface_v1 *background_effect;uint32_t background_capabilities;
    struct wl_surface *modal_surface;struct xdg_surface *modal_xdg;struct xdg_toplevel *modal_top;struct xdg_dialog_v1 *modal_dialog;
    uint64_t modal_commits;uint32_t modal_serial,modal_color,modal_painted_color;bool modal_configured,modal_painted;
    struct wl_surface *root,*child,*grandchild;struct wl_subsurface *child_role,*grandchild_role;
    struct xdg_surface *xdg;struct xdg_toplevel *toplevel;
    struct wl_surface *popup_surface;struct xdg_surface *popup_xdg;struct xdg_popup *popup;
    uint64_t popup_commits;uint32_t popup_serial,popup_color,reposition_token;int popup_x,popup_y,popup_width,popup_height;bool popup_configured;
    struct buffer *buffers;struct barrier *barriers;unsigned inflight,outstanding;size_t allocated;
    uint64_t sequence,control,root_commits,child_commits;uint32_t child_color,serial;int width,height,painted_width,painted_height;
    const char *control_path;bool ready,quit,failed;
};
static uint64_t stamp(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return 0;return (uint64_t)t.tv_sec*UINT64_C(1000000000)+(uint64_t)t.tv_nsec;}
static void event(struct client *c,const char *kind,const char *extra){
    if(c->sequence==UINT64_MAX){c->failed=true;c->quit=true;return;}
    printf("{\"event\":\"%s\",\"sequence\":%" PRIu64 ",\"controlSequence\":%" PRIu64 ",\"rootCommits\":%" PRIu64 ",\"childCommits\":%" PRIu64 ",\"serial\":%u,\"width\":%d,\"height\":%d,\"monotonicNs\":%" PRIu64 "%s}\n",kind,++c->sequence,c->control,c->root_commits,c->child_commits,c->serial,c->width,c->height,stamp(),extra?extra:"");fflush(stdout);
}
static void refuse(struct client *c,const char *reason){char extra[160];snprintf(extra,sizeof extra,",\"reason\":\"%s\"",reason);event(c,"refused",extra);c->failed=true;c->quit=true;}
// Ownership and release ordering derived from reviewed xdg-origin-fixture-v184.
static void remove_buffer(struct buffer *b){struct client *c=b->client;struct buffer **p=&c->buffers;while(*p && *p!=b)p=&(*p)->next;if(*p){*p=b->next;--c->inflight;c->allocated-=b->bytes;}wl_buffer_destroy(b->resource);munmap(b->data,b->bytes);free(b);}
static void released(void *data,struct wl_buffer *resource){(void)resource;struct buffer *b=data;event(b->client,"buffer-release",NULL);remove_buffer(b);}
static const struct wl_buffer_listener buffer_listener={released};
static bool commit_buffer(struct client *c,struct wl_surface *surface,int width,int height,uint32_t argb){
    if(!surface || width<1 || height<1 || width>4096 || height>4096){refuse(c,"buffer-dimensions");return false;}
    size_t bytes=(size_t)width*(size_t)height*4;
    if(c->inflight>=8 || bytes>UINT64_C(64)*1024*1024 || bytes>UINT64_C(128)*1024*1024-c->allocated){refuse(c,"buffer-bound");return false;}
    int fd=memfd_create("warlock-child-probe",MFD_CLOEXEC);
    if(fd<0 || ftruncate(fd,(off_t)bytes)){if(fd>=0)close(fd);refuse(c,"memfd-allocation");return false;}
    void *pixels=mmap(NULL,bytes,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
    if(pixels==MAP_FAILED){close(fd);refuse(c,"shm-mapping");return false;}
    for(int y=0;y<height;++y)for(int x=0;x<width;++x)((uint32_t*)pixels)[(size_t)y*width+x]=argb;
    struct wl_shm_pool *pool=wl_shm_create_pool(c->shm,fd,(int)bytes);
    struct wl_buffer *resource=pool?wl_shm_pool_create_buffer(pool,0,width,height,width*4,WL_SHM_FORMAT_ARGB8888):NULL;
    if(pool)wl_shm_pool_destroy(pool);
    close(fd);
    if(!resource){munmap(pixels,bytes);refuse(c,"shm-buffer");return false;}
    struct buffer *b=calloc(1,sizeof *b);
    if(!b){wl_buffer_destroy(resource);munmap(pixels,bytes);refuse(c,"buffer-record");return false;}
    *b=(struct buffer){.client=c,.resource=resource,.data=pixels,.bytes=bytes,.next=c->buffers};c->buffers=b;++c->inflight;c->allocated+=bytes;
    wl_buffer_add_listener(resource,&buffer_listener,b);
    if(surface==c->root)xdg_surface_set_window_geometry(c->xdg,0,0,width,height);
    if(surface==c->modal_surface)xdg_surface_set_window_geometry(c->modal_xdg,0,0,width,height);
    wl_surface_attach(surface,resource,0,0);wl_surface_damage(surface,0,0,width,height);wl_surface_commit(surface);
    if(surface==c->root)++c->root_commits;else if(surface==c->popup_surface)++c->popup_commits;else if(surface==c->modal_surface)++c->modal_commits;else ++c->child_commits;
    if(surface==c->root){c->painted_width=width;c->painted_height=height;}
    if(surface==c->modal_surface){c->modal_painted=true;c->modal_painted_color=argb;}
    event(c,"buffercommit",NULL);
    if(surface==c->popup_surface){char extra[160];snprintf(extra,sizeof extra,",\"popupCommits\":%" PRIu64 ",\"popupSerial\":%u,\"popupColor\":%u",c->popup_commits,c->popup_serial,argb);event(c,"popup-buffercommit",extra);}
    if(surface==c->modal_surface){char extra[192];snprintf(extra,sizeof extra,",\"modalCommits\":%" PRIu64 ",\"modalSerial\":%u,\"modalColor\":%u,\"modalSize\":[%d,%d]",c->modal_commits,c->modal_serial,argb,width,height);event(c,"modal-buffercommit",extra);}
    return true;
}
static void configure(void *data,struct xdg_surface *surface,uint32_t serial){struct client *c=data;if(c->quit)return;c->serial=serial;xdg_surface_ack_configure(surface,serial);event(c,"ack-configure",NULL);if((!c->ready || c->painted_width!=c->width || c->painted_height!=c->height) && !commit_buffer(c,c->root,c->width,c->height,UINT32_C(0xffff0000)))return;if(!c->ready){c->ready=true;event(c,"ready",NULL);}}
static const struct xdg_surface_listener surface_listener={configure};
static void top_configure(void *data,struct xdg_toplevel *top,int32_t width,int32_t height,struct wl_array *states){(void)top;(void)states;struct client *c=data;if(width<0 || height<0 || width>4096 || height>4096){refuse(c,"configure-dimensions");return;}if(width)c->width=width;if(height)c->height=height;}
static void top_close(void *data,struct xdg_toplevel *top){(void)top;struct client *c=data;c->quit=true;event(c,"server-close",NULL);}
static void top_bounds(void *data,struct xdg_toplevel *top,int32_t width,int32_t height){(void)top;if(width<0 || height<0 || width>4096 || height>4096)refuse(data,"configure-bounds");}
static void top_caps(void *data,struct xdg_toplevel *top,struct wl_array *caps){(void)data;(void)top;(void)caps;}
static const struct xdg_toplevel_listener top_listener={top_configure,top_close,top_bounds,top_caps};
static void ping(void *data,struct xdg_wm_base *wm,uint32_t serial){(void)data;xdg_wm_base_pong(wm,serial);}
static const struct xdg_wm_base_listener wm_listener={ping};
static void background_capabilities(void *data,struct ext_background_effect_manager_v1 *manager,uint32_t flags){(void)manager;((struct client*)data)->background_capabilities=flags;}
static const struct ext_background_effect_manager_v1_listener background_listener={background_capabilities};
static void global(void *data,struct wl_registry *registry,uint32_t name,const char *interface,uint32_t version){
    struct client *c=data;
    if(!strcmp(interface,"wl_compositor"))c->compositor=wl_registry_bind(registry,name,&wl_compositor_interface,version<4?version:4);
    else if(!strcmp(interface,"wl_subcompositor"))c->subcompositor=wl_registry_bind(registry,name,&wl_subcompositor_interface,1);
    else if(!strcmp(interface,"wl_shm"))c->shm=wl_registry_bind(registry,name,&wl_shm_interface,1);
    else if(!strcmp(interface,"ext_background_effect_manager_v1")){c->background_manager=wl_registry_bind(registry,name,&ext_background_effect_manager_v1_interface,1);ext_background_effect_manager_v1_add_listener(c->background_manager,&background_listener,c);}
    else if(!strcmp(interface,"xdg_wm_dialog_v1"))c->dialog_manager=wl_registry_bind(registry,name,&xdg_wm_dialog_v1_interface,1);
    else if(!strcmp(interface,"xdg_wm_base")){c->wm=wl_registry_bind(registry,name,&xdg_wm_base_interface,version<6?version:6);xdg_wm_base_add_listener(c->wm,&wm_listener,c);}
}
static void removed(void *data,struct wl_registry *registry,uint32_t name){(void)data;(void)registry;(void)name;}
static const struct wl_registry_listener registry_listener={global,removed};
static void remove_barrier(struct barrier *b){struct client *c=b->client;struct barrier **p=&c->barriers;while(*p && *p!=b)p=&(*p)->next;if(*p){*p=b->next;--c->outstanding;}wl_callback_destroy(b->callback);free(b);}
static void barrier_done(void *data,struct wl_callback *callback,uint32_t value){(void)callback;(void)value;struct barrier *b=data;char extra[160];snprintf(extra,sizeof extra,",\"command\":\"%s\",\"barrierControl\":%" PRIu64,b->command,b->control);event(b->client,"server-barrier",extra);remove_barrier(b);}
static const struct wl_callback_listener barrier_listener={barrier_done};
static void queue_barrier(struct client *c,const char *command){if(c->outstanding>=8){refuse(c,"barrier-bound");return;}struct barrier *b=calloc(1,sizeof *b);if(!b){refuse(c,"barrier-record");return;}b->callback=wl_display_sync(c->display);if(!b->callback){free(b);refuse(c,"barrier-callback");return;}b->client=c;b->control=c->control;b->command=command;b->next=c->barriers;c->barriers=b;++c->outstanding;wl_callback_add_listener(b->callback,&barrier_listener,b);}
static void destroy_children(struct client *c){if(c->grandchild_role)wl_subsurface_destroy(c->grandchild_role);if(c->grandchild)wl_surface_destroy(c->grandchild);if(c->child_role)wl_subsurface_destroy(c->child_role);if(c->child)wl_surface_destroy(c->child);c->grandchild_role=NULL;c->grandchild=NULL;c->child_role=NULL;c->child=NULL;}
static void destroy_popup(struct client *c){
    if(c->popup)xdg_popup_destroy(c->popup);
    if(c->popup_xdg)xdg_surface_destroy(c->popup_xdg);
    if(c->popup_surface)wl_surface_destroy(c->popup_surface);
    c->popup=NULL;c->popup_xdg=NULL;c->popup_surface=NULL;c->popup_configured=false;
}
static void popup_surface_configure(void *data,struct xdg_surface *surface,uint32_t serial){
    struct client *c=data;if(c->quit || !c->popup || surface!=c->popup_xdg)return;
    c->popup_serial=serial;xdg_surface_ack_configure(surface,serial);
    if(c->popup_width!=64 || c->popup_height!=48){refuse(c,"popup-configure-size");return;}
    xdg_surface_set_window_geometry(surface,0,0,c->popup_width,c->popup_height);
    if(!commit_buffer(c,c->popup_surface,c->popup_width,c->popup_height,c->popup_color))return;
    c->popup_configured=true;
    char extra[256];snprintf(extra,sizeof extra,",\"popupSerial\":%u,\"popupCommits\":%" PRIu64 ",\"popupGeometry\":[%d,%d,%d,%d]",serial,c->popup_commits,c->popup_x,c->popup_y,c->popup_width,c->popup_height);event(c,"popup-configured",extra);
}
static const struct xdg_surface_listener popup_surface_listener={popup_surface_configure};
static void popup_geometry(void *data,struct xdg_popup *popup,int32_t x,int32_t y,int32_t width,int32_t height){
    struct client *c=data;if(popup!=c->popup || width!=64 || height!=48 || x < -4096 || x > 4096 || y < -4096 || y > 4096){refuse(c,"popup-geometry");return;}
    c->popup_x=x;c->popup_y=y;c->popup_width=width;c->popup_height=height;
}
static void popup_done(void *data,struct xdg_popup *popup){struct client *c=data;if(popup==c->popup){event(c,"popup-done",NULL);destroy_popup(c);}}
static void popup_repositioned(void *data,struct xdg_popup *popup,uint32_t token){struct client *c=data;if(popup!=c->popup || token!=c->reposition_token){refuse(c,"popup-reposition-token");return;}char extra[80];snprintf(extra,sizeof extra,",\"repositionToken\":%u",token);event(c,"popup-repositioned",extra);}
static const struct xdg_popup_listener popup_listener={popup_geometry,popup_done,popup_repositioned};
static struct xdg_positioner *popup_position(struct client *c,int x,int y){
    struct xdg_positioner *position=xdg_wm_base_create_positioner(c->wm);if(!position){refuse(c,"popup-positioner");return NULL;}
    xdg_positioner_set_size(position,64,48);xdg_positioner_set_anchor_rect(position,x,y,1,1);
    xdg_positioner_set_anchor(position,XDG_POSITIONER_ANCHOR_BOTTOM_RIGHT);xdg_positioner_set_gravity(position,XDG_POSITIONER_GRAVITY_BOTTOM_RIGHT);
    return position;
}
static bool popup_command(struct client *c,const char *command){
    const char *known=NULL;
    if(!strcmp(command,"popup-create")){
        known="popup-create";if(c->popup){refuse(c,"popup-already-exists");return true;}
        c->popup_surface=wl_compositor_create_surface(c->compositor);if(!c->popup_surface){refuse(c,"popup-surface-allocation");return true;}
        c->popup_xdg=xdg_wm_base_get_xdg_surface(c->wm,c->popup_surface);if(!c->popup_xdg){destroy_popup(c);refuse(c,"popup-xdg-allocation");return true;}
        xdg_surface_add_listener(c->popup_xdg,&popup_surface_listener,c);struct xdg_positioner *position=popup_position(c,290,210);if(!position)return true;
        c->popup=xdg_surface_get_popup(c->popup_xdg,c->xdg,position);xdg_positioner_destroy(position);if(!c->popup){destroy_popup(c);refuse(c,"popup-role-allocation");return true;}xdg_popup_add_listener(c->popup,&popup_listener,c);
        c->popup_color=UINT32_C(0xff00ffff);wl_surface_commit(c->popup_surface);++c->popup_commits;
    }else if(!strcmp(command,"popup-yellow")){
        known="popup-yellow";if(!c->popup || !c->popup_configured){refuse(c,"popup-not-configured");return true;}c->popup_color=UINT32_C(0xffffff00);
        if(!commit_buffer(c,c->popup_surface,64,48,c->popup_color))return true;
    }else if(!strcmp(command,"popup-reposition")){
        known="popup-reposition";if(!c->popup || !c->popup_configured || wl_proxy_get_version((struct wl_proxy*)c->popup)<3 || c->reposition_token==UINT32_MAX){refuse(c,"popup-reposition-unavailable");return true;}
        struct xdg_positioner *position=popup_position(c,100,80);if(!position)return true;
        xdg_popup_reposition(c->popup,position,++c->reposition_token);xdg_positioner_destroy(position);
    }else if(!strcmp(command,"popup-destroy")){
        known="popup-destroy";if(!c->popup){refuse(c,"missing-popup");return true;}destroy_popup(c);event(c,"popup-destroyed",NULL);
    }else return false;
    char extra[128];snprintf(extra,sizeof extra,",\"command\":\"%s\"",known);event(c,"request",extra);if(!c->failed)queue_barrier(c,known);return true;
}
static void destroy_modal(struct client *c){
    if(c->modal_dialog)xdg_dialog_v1_destroy(c->modal_dialog);
    if(c->modal_top)xdg_toplevel_destroy(c->modal_top);
    if(c->modal_xdg)xdg_surface_destroy(c->modal_xdg);
    if(c->modal_surface)wl_surface_destroy(c->modal_surface);
    c->modal_dialog=NULL;c->modal_top=NULL;c->modal_xdg=NULL;c->modal_surface=NULL;c->modal_configured=false;c->modal_painted=false;
}
static void modal_surface_configure(void *data,struct xdg_surface *surface,uint32_t serial){
    struct client *c=data;if(c->quit || !c->modal_top || surface!=c->modal_xdg)return;
    c->modal_serial=serial;xdg_surface_ack_configure(surface,serial);
    if((!c->modal_painted || c->modal_painted_color!=c->modal_color) && !commit_buffer(c,c->modal_surface,96,64,c->modal_color))return;
    c->modal_configured=true;char extra[128];snprintf(extra,sizeof extra,",\"modalSerial\":%u,\"modalCommits\":%" PRIu64,serial,c->modal_commits);event(c,"modal-configured",extra);
}
static const struct xdg_surface_listener modal_surface_listener={modal_surface_configure};
static void modal_top_configure(void *data,struct xdg_toplevel *top,int32_t width,int32_t height,struct wl_array *states){
    struct client *c=data;(void)states;if(top!=c->modal_top || (width && width!=96) || (height && height!=64))refuse(c,"modal-configure-size");
}
static void modal_top_close(void *data,struct xdg_toplevel *top){struct client *c=data;if(top==c->modal_top){destroy_modal(c);event(c,"modal-server-close",NULL);}}
static const struct xdg_toplevel_listener modal_top_listener={modal_top_configure,modal_top_close,top_bounds,top_caps};
static bool modal_command(struct client *c,const char *command){
    const char *known=NULL;
    if(!strcmp(command,"modal-create")){
        known="modal-create";if(!c->dialog_manager || c->modal_top){refuse(c,"modal-create-unavailable");return true;}
        c->modal_surface=wl_compositor_create_surface(c->compositor);if(!c->modal_surface){refuse(c,"modal-surface-allocation");return true;}
        c->modal_xdg=xdg_wm_base_get_xdg_surface(c->wm,c->modal_surface);if(!c->modal_xdg){destroy_modal(c);refuse(c,"modal-xdg-allocation");return true;}
        xdg_surface_add_listener(c->modal_xdg,&modal_surface_listener,c);c->modal_top=xdg_surface_get_toplevel(c->modal_xdg);
        if(!c->modal_top){destroy_modal(c);refuse(c,"modal-role-allocation");return true;}
        xdg_toplevel_add_listener(c->modal_top,&modal_top_listener,c);xdg_toplevel_set_title(c->modal_top,"WARLOCK-MODAL-PROBE");xdg_toplevel_set_app_id(c->modal_top,"warlock-modal-probe");
        xdg_toplevel_set_min_size(c->modal_top,96,64);xdg_toplevel_set_max_size(c->modal_top,96,64);xdg_toplevel_set_parent(c->modal_top,c->toplevel);
        c->modal_dialog=xdg_wm_dialog_v1_get_xdg_dialog(c->dialog_manager,c->modal_top);if(!c->modal_dialog){destroy_modal(c);refuse(c,"modal-dialog-allocation");return true;}
        xdg_dialog_v1_set_modal(c->modal_dialog);c->modal_color=UINT32_C(0xffff00ff);wl_surface_commit(c->modal_surface);++c->modal_commits;
    }else if(!strcmp(command,"modal-yellow")){
        known="modal-yellow";if(!c->modal_top || !c->modal_configured){refuse(c,"modal-not-configured");return true;}c->modal_color=UINT32_C(0xffffff00);if(!commit_buffer(c,c->modal_surface,96,64,c->modal_color))return true;
    }else if(!strcmp(command,"modal-set") || !strcmp(command,"modal-unset")){
        known=!strcmp(command,"modal-set")?"modal-set":"modal-unset";if(!c->modal_dialog){refuse(c,"missing-modal");return true;}
        if(!strcmp(command,"modal-set"))xdg_dialog_v1_set_modal(c->modal_dialog);else xdg_dialog_v1_unset_modal(c->modal_dialog);
    }else if(!strcmp(command,"modal-unparent") || !strcmp(command,"modal-reparent")){
        known=!strcmp(command,"modal-unparent")?"modal-unparent":"modal-reparent";if(!c->modal_top){refuse(c,"missing-modal");return true;}
        xdg_toplevel_set_parent(c->modal_top,!strcmp(command,"modal-unparent")?NULL:c->toplevel);
    }else if(!strcmp(command,"modal-destroy")){
        known="modal-destroy";if(!c->modal_top){refuse(c,"missing-modal");return true;}destroy_modal(c);event(c,"modal-destroyed",NULL);
    }else return false;
    char extra[128];snprintf(extra,sizeof extra,",\"command\":\"%s\"",known);event(c,"request",extra);if(!c->failed)queue_barrier(c,known);return true;
}
static bool background_command(struct client *c,const char *command){
    const char *known=NULL;
    if(!strcmp(command,"background-create")){
        known="background-create";if(!c->background_manager || !(c->background_capabilities&EXT_BACKGROUND_EFFECT_MANAGER_V1_CAPABILITY_BLUR) || c->background_effect){refuse(c,"background-create-unavailable");return true;}
        c->background_effect=ext_background_effect_manager_v1_get_background_effect(c->background_manager,c->root);
        if(!c->background_effect){refuse(c,"background-allocation");return true;}
    }else if(!strcmp(command,"background-region-pending") || !strcmp(command,"background-region-pending-two")){
        known=!strcmp(command,"background-region-pending")?"background-region-pending":"background-region-pending-two";
        if(!c->background_effect){refuse(c,"background-missing");return true;}
        struct wl_region *region=wl_compositor_create_region(c->compositor);if(!region){refuse(c,"background-region-allocation");return true;}
        wl_region_add(region,!strcmp(command,"background-region-pending")?0:10,20,100,200);
        ext_background_effect_surface_v1_set_blur_region(c->background_effect,region);wl_region_destroy(region);
    }else if(!strcmp(command,"background-clear-pending")){
        known="background-clear-pending";if(!c->background_effect){refuse(c,"background-missing");return true;}ext_background_effect_surface_v1_set_blur_region(c->background_effect,NULL);
    }else if(!strcmp(command,"background-destroy")){
        known="background-destroy";if(!c->background_effect){refuse(c,"background-missing");return true;}ext_background_effect_surface_v1_destroy(c->background_effect);c->background_effect=NULL;
    }else return false;
    char extra[128];snprintf(extra,sizeof extra,",\"command\":\"%s\"",known);event(c,"request",extra);if(!c->failed)queue_barrier(c,known);return true;
}
static void execute(struct client *c,const char *command){
    if(!strcmp(command,"quit")){c->quit=true;event(c,"request",",\"command\":\"quit\"");return;}
    if(!c->ready){refuse(c,"command-before-ready");return;}
    if(popup_command(c,command) || modal_command(c,command) || background_command(c,command))return;
    const char *known=NULL;
    if(!strcmp(command,"child-create") || !strcmp(command,"child-create-sync")){
        known=!strcmp(command,"child-create")?"child-create":"child-create-sync";if(c->child){refuse(c,"child-already-exists");return;}
        c->child=wl_compositor_create_surface(c->compositor);c->child_role=wl_subcompositor_get_subsurface(c->subcompositor,c->child,c->root);
        if(!strcmp(command,"child-create"))wl_subsurface_set_desync(c->child_role);
        wl_subsurface_set_position(c->child_role,20,30);c->child_color=UINT32_C(0xff0000ff);
        if(!commit_buffer(c,c->child,64,48,c->child_color))return;
        if(!strcmp(command,"child-create")){wl_surface_commit(c->root);++c->root_commits;}
    } else if(!strcmp(command,"root-commit")){known="root-commit";wl_surface_commit(c->root);++c->root_commits;}
    else if(!c->child){refuse(c,"missing-child");return;}
    else if(!strcmp(command,"child-blue")){known="child-blue";c->child_color=UINT32_C(0xff0000ff);if(!commit_buffer(c,c->child,64,48,c->child_color))return;}
    else if(!strcmp(command,"child-yellow")){known="child-yellow";c->child_color=UINT32_C(0xffffff00);if(!commit_buffer(c,c->child,64,48,c->child_color))return;}
    else if(!strcmp(command,"child-empty")){known="child-empty";wl_surface_commit(c->child);++c->child_commits;}
    else if(!strcmp(command,"grand-yellow")){known="grand-yellow";if(!c->grandchild){refuse(c,"missing-grandchild");return;}if(!commit_buffer(c,c->grandchild,16,12,UINT32_C(0xffffff00)))return;}
    else if(!strcmp(command,"grand-desync")){known="grand-desync";if(!c->grandchild_role){refuse(c,"missing-grandchild");return;}wl_subsurface_set_desync(c->grandchild_role);}
    else if(!strcmp(command,"child-sync")){known="child-sync";wl_subsurface_set_sync(c->child_role);}
    else if(!strcmp(command,"child-desync")){known="child-desync";wl_subsurface_set_desync(c->child_role);}
    else if(!strcmp(command,"child-move-pending")){known="child-move-pending";wl_subsurface_set_position(c->child_role,100,110);}
    else if(!strcmp(command,"child-below-pending")){known="child-below-pending";wl_subsurface_place_below(c->child_role,c->root);}
    else if(!strcmp(command,"child-above-pending")){known="child-above-pending";wl_subsurface_place_above(c->child_role,c->root);}
    else if(!strcmp(command,"child-move")){known="child-move";wl_subsurface_set_position(c->child_role,100,110);wl_surface_commit(c->root);++c->root_commits;}
    else if(!strcmp(command,"child-below")){known="child-below";wl_subsurface_place_below(c->child_role,c->root);wl_surface_commit(c->root);++c->root_commits;}
    else if(!strcmp(command,"child-above")){known="child-above";wl_subsurface_place_above(c->child_role,c->root);wl_surface_commit(c->root);++c->root_commits;}
    else if(!strcmp(command,"child-detach")){known="child-detach";wl_surface_attach(c->child,NULL,0,0);wl_surface_commit(c->child);++c->child_commits;}
    else if(!strcmp(command,"child-reattach")){known="child-reattach";if(!commit_buffer(c,c->child,64,48,c->child_color))return;}
    else if(!strcmp(command,"child-destroy")){known="child-destroy";destroy_children(c);}
    else if(!strcmp(command,"grand-create")){
        known="grand-create";if(c->grandchild){refuse(c,"grandchild-already-exists");return;}
        c->grandchild=wl_compositor_create_surface(c->compositor);c->grandchild_role=wl_subcompositor_get_subsurface(c->subcompositor,c->grandchild,c->child);
        wl_subsurface_set_desync(c->grandchild_role);wl_subsurface_set_position(c->grandchild_role,7,9);
        if(!commit_buffer(c,c->grandchild,16,12,UINT32_C(0xff00ffff)))return;
        wl_surface_commit(c->child);++c->child_commits;
    } else {refuse(c,"unknown-command");return;}
    char extra[128];snprintf(extra,sizeof extra,",\"command\":\"%s\"",known);event(c,"request",extra);if(!c->failed)queue_barrier(c,known);
}
static void control_ready(struct client *c){
    int fd=open(c->control_path,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);if(fd<0){if(errno!=ENOENT)refuse(c,"control-open");return;}
    struct stat st;if(fstat(fd,&st) || !S_ISREG(st.st_mode) || st.st_uid!=getuid() || (st.st_mode&077) || st.st_size<1 || st.st_size>=128){close(fd);refuse(c,"control-file-bound");return;}
    char bytes[128];ssize_t count=read(fd,bytes,sizeof bytes-1);close(fd);
    if(count!=st.st_size || memchr(bytes,0,(size_t)count)){refuse(c,"control-read");return;}bytes[count]=0;
    uint64_t sequence=0;char command[32],trailer;if(sscanf(bytes,"%" SCNu64 " %31s %c",&sequence,command,&trailer)!=2 || !sequence){refuse(c,"control-shape");return;}
    if(sequence==c->control)return;
    if(c->control==UINT64_MAX || sequence!=c->control+1){refuse(c,"control-sequence");return;}
    c->control=sequence;execute(c,command);
}
int main(int argc,char **argv){
    if(argc==2 && !strcmp(argv[1],"--validate")){puts("{\"valid\":true,\"width\":320,\"height\":240,\"inflightLimit\":8,\"barrierLimit\":8}");return 0;}
    if(argc!=1)return 64;
    struct client c={.width=320,.height=240,.control_path=getenv("WARLOCK_CHILD_CONTROL_PATH")};if(!c.control_path || c.control_path[0]!='/')return 64;
    c.display=wl_display_connect(NULL);if(!c.display)return 2;c.registry=wl_display_get_registry(c.display);wl_registry_add_listener(c.registry,&registry_listener,&c);
    if(wl_display_roundtrip(c.display)<0 || !c.compositor || !c.subcompositor || !c.shm || !c.wm){wl_display_disconnect(c.display);return 3;}
    c.root=wl_compositor_create_surface(c.compositor);c.xdg=xdg_wm_base_get_xdg_surface(c.wm,c.root);xdg_surface_add_listener(c.xdg,&surface_listener,&c);
    c.toplevel=xdg_surface_get_toplevel(c.xdg);xdg_toplevel_add_listener(c.toplevel,&top_listener,&c);xdg_toplevel_set_title(c.toplevel,"WARLOCK-CHILD-PROBE");xdg_toplevel_set_app_id(c.toplevel,"warlock-child-probe");xdg_toplevel_set_min_size(c.toplevel,320,240);xdg_toplevel_set_max_size(c.toplevel,320,240);
    wl_surface_commit(c.root);++c.root_commits;
    while(!c.quit){
        bool prepared=false;while(!c.quit){if(wl_display_prepare_read(c.display)==0){prepared=true;break;}if(wl_display_dispatch_pending(c.display)<0){refuse(&c,"dispatch-pending");break;}}
        if(!prepared)break;
        int flushed=wl_display_flush(c.display);if(flushed<0 && errno!=EAGAIN){wl_display_cancel_read(c.display);refuse(&c,"flush-transport");break;}
        struct pollfd p={.fd=wl_display_get_fd(c.display),.events=POLLIN|(flushed<0?POLLOUT:0)};int result=poll(&p,1,25);
        if(result<0){wl_display_cancel_read(c.display);if(errno==EINTR)continue;refuse(&c,"poll");break;}
        if(p.revents&POLLIN){if(wl_display_read_events(c.display)<0 || wl_display_dispatch_pending(c.display)<0){refuse(&c,"read-transport");break;}}else wl_display_cancel_read(c.display);
        if(p.revents&(POLLERR|POLLHUP|POLLNVAL)){refuse(&c,"display-disconnected");break;}
        if(!c.quit)control_ready(&c);
    }
    while(c.barriers)remove_barrier(c.barriers);
    if(c.background_effect)ext_background_effect_surface_v1_destroy(c.background_effect);
    destroy_modal(&c);destroy_popup(&c);destroy_children(&c);xdg_toplevel_destroy(c.toplevel);xdg_surface_destroy(c.xdg);wl_surface_destroy(c.root);
    while(c.buffers)remove_buffer(c.buffers);
    if(c.dialog_manager)xdg_wm_dialog_v1_destroy(c.dialog_manager);
    if(c.background_manager)ext_background_effect_manager_v1_destroy(c.background_manager);
    xdg_wm_base_destroy(c.wm);wl_shm_destroy(c.shm);wl_subcompositor_destroy(c.subcompositor);wl_compositor_destroy(c.compositor);wl_registry_destroy(c.registry);
    if(!c.failed && wl_display_flush(c.display)<0 && errno!=EAGAIN)c.failed=true;
    wl_display_disconnect(c.display);if(!c.failed)event(&c,"normalexit",NULL);return c.failed?1:0;
}
