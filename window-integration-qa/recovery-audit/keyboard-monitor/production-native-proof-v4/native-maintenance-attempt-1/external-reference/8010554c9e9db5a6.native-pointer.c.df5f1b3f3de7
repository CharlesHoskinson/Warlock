#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L
#include <wayland-client.h>
#include "virtual-pointer-client.h"
#include "private-producer-guard.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <time.h>
#include <math.h>
static struct zwlr_virtual_pointer_manager_v1* manager;
static void global(void* data,struct wl_registry* registry,uint32_t name,const char* iface,uint32_t version) {
    (void)data;
    if(!strcmp(iface,"zwlr_virtual_pointer_manager_v1"))manager=wl_registry_bind(registry,name,&zwlr_virtual_pointer_manager_v1_interface,version>2?2:version);
}
static void removed(void* data,struct wl_registry* registry,uint32_t name){(void)data;(void)registry;(void)name;}
static uint32_t now(void){struct timespec ts;clock_gettime(CLOCK_MONOTONIC,&ts);return (uint32_t)(ts.tv_sec*1000+ts.tv_nsec/1000000);}
int main(void) {
    int fd=private_producer_connect();if(fd<0)return 20;
    struct wl_display* connection=wl_display_connect_to_fd(fd);if(!connection){fprintf(stderr,"private pointer Wayland connection failed\n");return 3;}
    struct wl_registry* registry=wl_display_get_registry(connection);
    const struct wl_registry_listener listener={global,removed};wl_registry_add_listener(registry,&listener,NULL);
    if(wl_display_roundtrip(connection)<0||!manager){fprintf(stderr,"private pointer registry/manager unavailable\n");return 4;}
    struct zwlr_virtual_pointer_v1* pointer=zwlr_virtual_pointer_manager_v1_create_virtual_pointer(manager,NULL);
    char line[256];
    while(fgets(line,sizeof(line),stdin)) {
        double x,y,width,height;unsigned button,state;
        if(sscanf(line,"absolute %lf %lf %lf %lf",&x,&y,&width,&height)==4) {
            if(!isfinite(x)||!isfinite(y)||!isfinite(width)||!isfinite(height)||width<=0||height<=0||x<0||y<0||x>width||y>height||width>400000||height>400000)return 5;
            zwlr_virtual_pointer_v1_motion_absolute(pointer,now(),(uint32_t)llround(x*10000),(uint32_t)llround(y*10000),(uint32_t)llround(width*10000),(uint32_t)llround(height*10000));
            zwlr_virtual_pointer_v1_frame(pointer);
        } else if(sscanf(line,"relative %lf %lf",&x,&y)==2) {
            if(!isfinite(x)||!isfinite(y)||fabs(x)>4096||fabs(y)>4096)return 5;
            zwlr_virtual_pointer_v1_motion(pointer,now(),wl_fixed_from_double(x),wl_fixed_from_double(y));zwlr_virtual_pointer_v1_frame(pointer);
        } else if(sscanf(line,"button %u %u",&button,&state)==2) {
            zwlr_virtual_pointer_v1_button(pointer,now(),button,state);zwlr_virtual_pointer_v1_frame(pointer);
        } else if(!strcmp(line,"sync\n")) {
            if(wl_display_roundtrip(connection)<0)return 6;
            puts("ready");fflush(stdout);
        } else return 5;
    }
    zwlr_virtual_pointer_v1_destroy(pointer);zwlr_virtual_pointer_manager_v1_destroy(manager);
    wl_registry_destroy(registry);wl_display_roundtrip(connection);wl_display_disconnect(connection);return 0;
}
