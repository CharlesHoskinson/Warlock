#define _GNU_SOURCE
/* CPU-only protocol shim. Never links into the actual physical-keyboard driver. */
#include <wayland-client.h>
#include <wayland-client-core.h>
#include "virtual-keyboard-client.h"
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <openssl/sha.h>
static int objects[5],connection=-1,roundtrips;
static const struct wl_registry_listener*listener;
static void*listener_data;
static FILE*logfile;
static void record(const char*kind,unsigned a,unsigned b){
 if(!logfile){const char*path=getenv("CPU_KEYBOARD_EVENT_LOG");if(!path)abort();logfile=fopen(path,"a");if(!logfile)abort();}
 fprintf(logfile,"{\"kind\":\"%s\",\"a\":%u,\"b\":%u}\n",kind,a,b);fflush(logfile);
}
struct wl_display*wl_display_connect_to_fd(int fd){connection=fd;record("connect",0,0);return(struct wl_display*)&objects[0];}
void wl_display_disconnect(struct wl_display*d){(void)d;record("disconnect",0,0);if(connection>=0)close(connection);connection=-1;if(logfile)fclose(logfile);logfile=NULL;}
int wl_display_roundtrip(struct wl_display*d){
 (void)d;++roundtrips;record("roundtrip",roundtrips,0);
 if(roundtrips==1&&listener){listener->global(listener_data,(struct wl_registry*)&objects[1],101,"wl_seat",1);listener->global(listener_data,(struct wl_registry*)&objects[1],102,"zwp_virtual_keyboard_manager_v1",1);if(getenv("CPU_DUPLICATE_SEAT"))listener->global(listener_data,(struct wl_registry*)&objects[1],103,"wl_seat",1);}
 const char*removed=getenv("CPU_REMOVAL_AT");if(removed&&roundtrips==atoi(removed)&&listener)listener->global_remove(listener_data,(struct wl_registry*)&objects[1],102);
 const char*failure=getenv("CPU_FAIL_AT");return failure&&roundtrips==atoi(failure)?-1:0;
}
int wl_proxy_add_listener(struct wl_proxy*p,void(**implementation)(void),void*data){if(p==(struct wl_proxy*)&objects[1]){listener=(const struct wl_registry_listener*)implementation;listener_data=data;}return 0;}
uint32_t wl_proxy_get_version(struct wl_proxy*p){(void)p;return 1;}
void wl_proxy_destroy(struct wl_proxy*p){(void)p;record("local_destroy",0,0);}
struct wl_proxy*wl_proxy_marshal_flags(struct wl_proxy*p,uint32_t opcode,const struct wl_interface*interface,uint32_t version,uint32_t flags,...){
 (void)version;va_list args;va_start(args,flags);struct wl_proxy*result=NULL;
 if(interface==&wl_registry_interface)result=(struct wl_proxy*)&objects[1];
 else if(interface==&wl_seat_interface)result=(struct wl_proxy*)&objects[2];
 else if(interface==&zwp_virtual_keyboard_manager_v1_interface)result=(struct wl_proxy*)&objects[3];
 else if(interface==&zwp_virtual_keyboard_v1_interface){result=(struct wl_proxy*)&objects[4];record("create_keyboard",0,0);}
 else if(p==(struct wl_proxy*)&objects[4]&&opcode==0){
  unsigned format=va_arg(args,unsigned);int fd=va_arg(args,int);unsigned size=va_arg(args,unsigned);struct stat st;if(fstat(fd,&st)||st.st_size!=size||format!=WL_KEYBOARD_KEYMAP_FORMAT_XKB_V1||fcntl(fd,F_GET_SEALS)!=(F_SEAL_SEAL|F_SEAL_SHRINK|F_SEAL_GROW|F_SEAL_WRITE)||!(fcntl(fd,F_GETFD)&FD_CLOEXEC))abort();
  unsigned char*bytes=malloc(size),hash[32];if(!bytes||pread(fd,bytes,size,0)!=(ssize_t)size||bytes[size-1]!=0||!SHA256(bytes,size,hash))abort();free(bytes);record("keymap",size,format);
 }else if(p==(struct wl_proxy*)&objects[4]&&opcode==1){unsigned time=va_arg(args,unsigned),wire=va_arg(args,unsigned),state=va_arg(args,unsigned);if(time!=0)abort();record("key",wire,state);}
 else if(p==(struct wl_proxy*)&objects[4]&&opcode==2){unsigned depressed=va_arg(args,unsigned),latched=va_arg(args,unsigned),locked=va_arg(args,unsigned),group=va_arg(args,unsigned);if(latched||locked||group)abort();record("modifiers",depressed,latched);}
 else if(p==(struct wl_proxy*)&objects[4]&&flags==WL_MARSHAL_FLAG_DESTROY)record("destroy_keyboard",0,0);
 va_end(args);return result;
}
