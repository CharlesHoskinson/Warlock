#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <time.h>
#include <wayland-client.h>
#include <xkbcommon/xkbcommon.h>
#include "virtual-keyboard-client.h"

static struct zwp_virtual_keyboard_manager_v1 *manager;
static struct wl_seat *seat;
static void global(void *data, struct wl_registry *r, uint32_t name, const char *iface, uint32_t version) {
    (void)data; (void)version;
    if (!strcmp(iface, "zwp_virtual_keyboard_manager_v1"))
        manager=wl_registry_bind(r,name,&zwp_virtual_keyboard_manager_v1_interface,1);
    if (!strcmp(iface,"wl_seat") && !seat)
        seat=wl_registry_bind(r,name,&wl_seat_interface,1);
}
static void removed(void *data,struct wl_registry *r,uint32_t name) {(void)data;(void)r;(void)name;}
static const struct wl_registry_listener listener={global,removed};
static uint32_t millis(void) {struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1000+t.tv_nsec/1000000;}
static void key(struct wl_display *d,struct zwp_virtual_keyboard_v1 *k,struct xkb_state *state,unsigned code,unsigned pressed) {
    zwp_virtual_keyboard_v1_key(k,millis(),code,pressed);
    xkb_state_update_key(state,code+8,pressed?XKB_KEY_DOWN:XKB_KEY_UP);
    zwp_virtual_keyboard_v1_modifiers(k,xkb_state_serialize_mods(state,XKB_STATE_MODS_DEPRESSED),
        xkb_state_serialize_mods(state,XKB_STATE_MODS_LATCHED),xkb_state_serialize_mods(state,XKB_STATE_MODS_LOCKED),
        xkb_state_serialize_layout(state,XKB_STATE_LAYOUT_EFFECTIVE));
    wl_display_flush(d);
}
int main(void) {
    struct wl_display *d=wl_display_connect(NULL);if(!d)return 2;
    struct wl_registry *r=wl_display_get_registry(d);wl_registry_add_listener(r,&listener,NULL);wl_display_roundtrip(d);
    if(!manager||!seat){fprintf(stderr,"No virtual keyboard protocol/seat\n");return 3;}
    struct xkb_context *ctx=xkb_context_new(XKB_CONTEXT_NO_FLAGS);
    const struct xkb_rule_names names={.rules="evdev",.model="pc105",.layout="us"};
    struct xkb_keymap *map=xkb_keymap_new_from_names(ctx,&names,XKB_KEYMAP_COMPILE_NO_FLAGS);
    if(!map)return 4;
    struct xkb_state *state=xkb_state_new(map);char *text=xkb_keymap_get_as_string(map,XKB_KEYMAP_FORMAT_TEXT_V1);
    size_t length=strlen(text)+1;int fd=memfd_create("orca-qa-evdev-map",MFD_CLOEXEC);
    if(fd<0||write(fd,text,length)!=(ssize_t)length)return 5;
    struct zwp_virtual_keyboard_v1 *k=zwp_virtual_keyboard_manager_v1_create_virtual_keyboard(manager,seat);
    zwp_virtual_keyboard_v1_keymap(k,WL_KEYBOARD_KEYMAP_FORMAT_XKB_V1,fd,length);wl_display_roundtrip(d);close(fd);free(text);
    char line[100];unsigned code,value;unsigned char held[256]={0};
    while(fgets(line,sizeof(line),stdin)) {
        if(sscanf(line,"key %u %u",&code,&value)==2) {
            if(code>=sizeof(held)||value>1)return 6;
            key(d,k,state,code,value);held[code]=value;
        } else if(sscanf(line,"sleep %u",&value)==1)usleep(value*1000);
        else if(!strncmp(line,"sync",4)) {wl_display_roundtrip(d);puts("ready");fflush(stdout);}
        else return 7;
    }
    for(code=0;code<sizeof(held);code++)if(held[code])key(d,k,state,code,0);
    zwp_virtual_keyboard_v1_destroy(k);wl_display_roundtrip(d);
    xkb_state_unref(state);xkb_keymap_unref(map);xkb_context_unref(ctx);
    wl_registry_destroy(r);wl_display_disconnect(d);return 0;
}
