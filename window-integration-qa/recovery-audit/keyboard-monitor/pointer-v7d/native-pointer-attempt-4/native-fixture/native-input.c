#define _GNU_SOURCE
/* Isolated real Wayland producer. Never runs against the main runtime. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <time.h>
#include <wayland-client.h>
#include <xkbcommon/xkbcommon.h>
#include "virtual-keyboard-client.h"
#include "input-method-client.h"
#pragma GCC diagnostic ignored "-Wunused-parameter"

static struct wl_display *display;
static struct wl_seat *seat;
static struct zwp_virtual_keyboard_manager_v1 *manager;
static struct zwp_input_method_manager_v2 *ime_manager;
static struct zwp_input_method_v2 *ime;
static struct zwp_input_method_keyboard_grab_v2 *ime_grab;
static int ime_unavailable;
struct Device {struct zwp_virtual_keyboard_v1 *keyboard;struct xkb_keymap *map;struct xkb_state *state;unsigned char held[256];};
static struct Device devices[2];
static unsigned selected;
static uint32_t millis(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1000+t.tv_nsec/1000000;}
static void global(void *data,struct wl_registry *registry,uint32_t name,const char *interface,uint32_t version){
    if(!strcmp(interface,"wl_seat")&&!seat)seat=wl_registry_bind(registry,name,&wl_seat_interface,1);
    if(!strcmp(interface,"zwp_virtual_keyboard_manager_v1"))manager=wl_registry_bind(registry,name,&zwp_virtual_keyboard_manager_v1_interface,1);
    if(!strcmp(interface,"zwp_input_method_manager_v2"))ime_manager=wl_registry_bind(registry,name,&zwp_input_method_manager_v2_interface,1);
}
static void removed(void *data,struct wl_registry *registry,uint32_t name){}
static const struct wl_registry_listener registry_listener={global,removed};
static void ime_simple(void *data,struct zwp_input_method_v2 *resource){}
static void ime_surrounding(void *data,struct zwp_input_method_v2 *resource,const char *text,uint32_t cursor,uint32_t anchor){}
static void ime_cause(void *data,struct zwp_input_method_v2 *resource,uint32_t cause){}
static void ime_content(void *data,struct zwp_input_method_v2 *resource,uint32_t hint,uint32_t purpose){}
static void ime_unavailable_event(void *data,struct zwp_input_method_v2 *resource){ime_unavailable=1;}
static const struct zwp_input_method_v2_listener ime_listener={ime_simple,ime_simple,ime_surrounding,ime_cause,ime_content,ime_simple,ime_unavailable_event};
static void grab_keymap(void *data,struct zwp_input_method_keyboard_grab_v2 *resource,uint32_t format,int32_t fd,uint32_t size){close(fd);}
static void grab_key(void *data,struct zwp_input_method_keyboard_grab_v2 *resource,uint32_t serial,uint32_t time,uint32_t key,uint32_t state){fprintf(stderr,"{\"imeKey\":%u,\"pressed\":%u}\n",key,state);}
static void grab_modifiers(void *data,struct zwp_input_method_keyboard_grab_v2 *resource,uint32_t serial,uint32_t depressed,uint32_t latched,uint32_t locked,uint32_t group){}
static void grab_repeat(void *data,struct zwp_input_method_keyboard_grab_v2 *resource,int32_t rate,int32_t delay){}
static const struct zwp_input_method_keyboard_grab_v2_listener grab_listener={grab_keymap,grab_key,grab_modifiers,grab_repeat};
static int roundtrip(void){return wl_display_roundtrip(display)<0?-1:0;}
static int replace_map(struct Device *device,const char *layout,const char *options){
    struct xkb_context *context=xkb_context_new(XKB_CONTEXT_NO_FLAGS);
    const int has_variant=!strncmp(options,"variant:",8);
    const struct xkb_rule_names names={.rules="evdev",.model="pc105",.layout=layout,.variant=has_variant?options+8:NULL,.options=has_variant?"":options};
    struct xkb_keymap *map=xkb_keymap_new_from_names(context,&names,XKB_KEYMAP_COMPILE_NO_FLAGS);
    xkb_context_unref(context);if(!map)return -1;
    struct xkb_state *state=xkb_state_new(map);if(!state){xkb_keymap_unref(map);return -1;}
    char *text=xkb_keymap_get_as_string(map,XKB_KEYMAP_FORMAT_TEXT_V1);if(!text){xkb_state_unref(state);xkb_keymap_unref(map);return -1;}
    size_t length=strlen(text)+1;int fd=memfd_create("private-keyboard-policy-map",MFD_CLOEXEC);
    if(fd<0||write(fd,text,length)!=(ssize_t)length){if(fd>=0)close(fd);free(text);xkb_state_unref(state);xkb_keymap_unref(map);return -1;}
    zwp_virtual_keyboard_v1_keymap(device->keyboard,WL_KEYBOARD_KEYMAP_FORMAT_XKB_V1,fd,length);close(fd);free(text);
    if(device->state)xkb_state_unref(device->state);if(device->map)xkb_keymap_unref(device->map);
    device->map=map;device->state=state;
    for(unsigned key=0;key<256;++key)if(device->held[key])xkb_state_update_key(state,key+8,XKB_KEY_DOWN);
    return roundtrip();
}
static void emit_modifiers(struct Device *device){
    zwp_virtual_keyboard_v1_modifiers(device->keyboard,xkb_state_serialize_mods(device->state,XKB_STATE_MODS_DEPRESSED),xkb_state_serialize_mods(device->state,XKB_STATE_MODS_LATCHED),xkb_state_serialize_mods(device->state,XKB_STATE_MODS_LOCKED),xkb_state_serialize_layout(device->state,XKB_STATE_LAYOUT_EFFECTIVE));
}
static int key(struct Device *device,unsigned code,unsigned pressed,int automatic){
    if(!device->keyboard||code>=256||pressed>1)return -1;
    zwp_virtual_keyboard_v1_key(device->keyboard,millis(),code,pressed);
    /* Real repeats do not increment the producer's XKB held-key count. */
    if(device->held[code]!=pressed)xkb_state_update_key(device->state,code+8,pressed?XKB_KEY_DOWN:XKB_KEY_UP);
    device->held[code]=pressed;if(automatic)emit_modifiers(device);return wl_display_flush(display)<0?-1:0;
}
static void drop(struct Device *device){
    if(device->keyboard)zwp_virtual_keyboard_v1_destroy(device->keyboard);
    if(device->state)xkb_state_unref(device->state);if(device->map)xkb_keymap_unref(device->map);
    memset(device,0,sizeof(*device));
}
static int create(struct Device *device){if(device->keyboard)return -1;device->keyboard=zwp_virtual_keyboard_manager_v1_create_virtual_keyboard(manager,seat);return replace_map(device,"us","");}
int main(void){
    const char *runtime=getenv("XDG_RUNTIME_DIR"),*socket=getenv("WAYLAND_DISPLAY");struct stat status;
    if(!runtime||strncmp(runtime,"/tmp/kbn-",9)||stat(runtime,&status)||(status.st_mode&0777)!=0700||status.st_uid!=getuid()||!socket||strchr(socket,'/'))return 20;
    display=wl_display_connect(NULL);if(!display)return 2;
    struct wl_registry *registry=wl_display_get_registry(display);wl_registry_add_listener(registry,&registry_listener,NULL);if(roundtrip()||!manager||!seat)return 3;
    if(create(&devices[0]))return 4;
    char line[200],layout[50],options[80],operation[20];unsigned a,b,c,d;int result=0;
    while(fgets(line,sizeof(line),stdin)){
        struct Device *device=&devices[selected];
        if(sscanf(line,"key %u %u",&a,&b)==2){if(key(device,a,b,1)){result=6;break;}}
        else if(sscanf(line,"raw %u %u",&a,&b)==2){if(key(device,a,b,0)){result=6;break;}}
        else if(sscanf(line,"mods %u %u %u %u",&a,&b,&c,&d)==4){if(!device->keyboard){result=6;break;}xkb_state_update_mask(device->state,a,b,c,0,0,d);zwp_virtual_keyboard_v1_modifiers(device->keyboard,a,b,c,d);}
        else if(!strncmp(line,"auto\n",5)){if(!device->keyboard){result=6;break;}emit_modifiers(device);}
        else if(sscanf(line,"map %49s %79s",layout,options)==2){if(!device->keyboard||replace_map(device,layout,!strcmp(options,"-")?"":options)){result=6;break;}}
        else if(sscanf(line,"device %u",&a)==1){if(a>=2){result=6;break;}selected=a;}
        else if(!strncmp(line,"create\n",7)){if(create(device)){result=6;break;}}
        else if(!strncmp(line,"drop\n",5)){drop(device);if(roundtrip()){result=6;break;}}
        else if(sscanf(line,"sleep %u",&a)==1){if(a>10000){result=6;break;}usleep(a*1000);}
        else if(sscanf(line,"ime %19s",operation)==1){
            if(!strcmp(operation,"on")&&!ime&&ime_manager){ime_unavailable=0;ime=zwp_input_method_manager_v2_get_input_method(ime_manager,seat);zwp_input_method_v2_add_listener(ime,&ime_listener,NULL);if(roundtrip()||ime_unavailable){result=8;break;}ime_grab=zwp_input_method_v2_grab_keyboard(ime);zwp_input_method_keyboard_grab_v2_add_listener(ime_grab,&grab_listener,NULL);if(roundtrip()){result=8;break;}}
            else if(!strcmp(operation,"off")&&ime){zwp_input_method_keyboard_grab_v2_release(ime_grab);zwp_input_method_v2_destroy(ime);ime_grab=NULL;ime=NULL;if(roundtrip()){result=8;break;}}
            else {result=8;break;}
        }
        else if(!strncmp(line,"sync\n",5)){if(roundtrip()){result=9;break;}puts("ready");fflush(stdout);}
        else {result=7;break;}
    }
    for(unsigned index=0;index<2;++index)if(devices[index].keyboard){for(unsigned code=0;code<256;++code)if(devices[index].held[code])key(&devices[index],code,0,1);drop(&devices[index]);}
    if(ime){zwp_input_method_keyboard_grab_v2_release(ime_grab);zwp_input_method_v2_destroy(ime);}
    roundtrip();wl_registry_destroy(registry);wl_display_disconnect(display);return result;
}
