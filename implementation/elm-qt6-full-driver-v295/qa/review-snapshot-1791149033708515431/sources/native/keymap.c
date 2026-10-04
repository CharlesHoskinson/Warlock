#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <wayland-client.h>
#include <stdbool.h>
#include <sys/socket.h>
#include "private-runtime.h"
#include <xkbcommon/xkbcommon.h>
struct state {struct wl_seat *seat;struct wl_keyboard *keyboard;uint32_t seat_name;int failed,received;};
static void keymap(void *data,struct wl_keyboard *keyboard,uint32_t format,int32_t fd,uint32_t size){
 (void)keyboard;struct state*s=data;struct stat st;
 if(s->received||format!=WL_KEYBOARD_KEYMAP_FORMAT_XKB_V1||size<2||size>1024*1024||fstat(fd,&st)||st.st_size<(off_t)size){close(fd);s->failed=1;return;}
 char *raw=mmap(NULL,size,PROT_READ,MAP_PRIVATE,fd,0);close(fd);
 if(raw==MAP_FAILED){s->failed=1;return;}
 if(raw[size-1]!=0||memchr(raw,0,size-1)){munmap(raw,size);s->failed=1;return;}
 struct xkb_context*c=xkb_context_new(XKB_CONTEXT_NO_FLAGS);struct xkb_keymap*k=c?xkb_keymap_new_from_string(c,raw,XKB_KEYMAP_FORMAT_TEXT_V1,XKB_KEYMAP_COMPILE_NO_FLAGS):NULL;
 xkb_mod_index_t shift=k?xkb_keymap_mod_get_index(k,XKB_MOD_NAME_SHIFT):XKB_MOD_INVALID;
 if(!k||shift>=32){s->failed=1;}else{
  FILE*f=fopen("keymap.xkb","wx");
  if(!f||fwrite(raw,1,size-1,f)!=size-1){s->failed=1;}else{s->received=1;printf("{\"seatRegistryId\":%u,\"xkbShiftMask\":%u,\"format\":1,\"keymapBytes\":%u}\n",s->seat_name,UINT32_C(1)<<shift,size-1);}
  if(f&&fclose(f))s->failed=1;
 }
 if(k)xkb_keymap_unref(k);
 if(c)xkb_context_unref(c);
 munmap(raw,size);
}
static void enter(void*d,struct wl_keyboard*k,uint32_t s,struct wl_surface*w,struct wl_array*a){(void)d;(void)k;(void)s;(void)w;(void)a;}
static void leave(void*d,struct wl_keyboard*k,uint32_t s,struct wl_surface*w){(void)d;(void)k;(void)s;(void)w;}
static void key(void*d,struct wl_keyboard*k,uint32_t s,uint32_t t,uint32_t v,uint32_t st){(void)d;(void)k;(void)s;(void)t;(void)v;(void)st;}
static void modifiers(void*d,struct wl_keyboard*k,uint32_t s,uint32_t a,uint32_t b,uint32_t c,uint32_t g){(void)d;(void)k;(void)s;(void)a;(void)b;(void)c;(void)g;}
static void repeat(void*d,struct wl_keyboard*k,int32_t r,int32_t delay){(void)d;(void)k;(void)r;(void)delay;}
static const struct wl_keyboard_listener kl={keymap,enter,leave,key,modifiers,repeat};
static void capabilities(void*d,struct wl_seat*seat,uint32_t caps){struct state*s=d;if(!(caps&WL_SEAT_CAPABILITY_KEYBOARD)){s->failed=1;return;}if(!s->keyboard){s->keyboard=wl_seat_get_keyboard(seat);if(!s->keyboard||wl_keyboard_add_listener(s->keyboard,&kl,s))s->failed=1;}}
static void name(void*d,struct wl_seat*s,const char*n){(void)d;(void)s;(void)n;}
static const struct wl_seat_listener sl={capabilities,name};
static void global(void*d,struct wl_registry*r,uint32_t id,const char*iface,uint32_t version){struct state*s=d;if(strcmp(iface,wl_seat_interface.name))return;if(s->seat||version<5){s->failed=1;return;}s->seat_name=id;s->seat=wl_registry_bind(r,id,&wl_seat_interface,5);if(!s->seat||wl_seat_add_listener(s->seat,&sl,s))s->failed=1;}
static void removed(void*d,struct wl_registry*r,uint32_t id){(void)r;struct state*s=d;if(id==s->seat_name)s->failed=1;}
static const struct wl_registry_listener rl={global,removed};
int main(int argc,char**argv){
 (void)argv;const char*gate=getenv("ELM_GTK_ROLE_QA"),*display_name=getenv("WAYLAND_DISPLAY");
 if(argc!=1||!gate||strcmp(gate,"1")||!canonical_private_runtime(getenv("XDG_RUNTIME_DIR"))||!display_name||!*display_name||!strcmp(display_name,".")||!strcmp(display_name,"..")||strchr(display_name,'/')){fputs("private owned QA launcher required\n",stderr);return 2;}
 struct wl_display*display=wl_display_connect(NULL);if(!display)return 2;struct ucred peer;socklen_t length=sizeof peer;
 if(getsockopt(wl_display_get_fd(display),SOL_SOCKET,SO_PEERCRED,&peer,&length)||length!=sizeof peer||peer.uid!=geteuid()){wl_display_disconnect(display);return 2;}
 fprintf(stderr,"keymap-peer-pid:%d\n",peer.pid);
 struct state s={0};struct wl_registry*r=wl_display_get_registry(display);wl_registry_add_listener(r,&rl,&s);
 for(int i=0;i<3&&!s.failed&&!s.received;i++)if(wl_display_roundtrip(display)<0)s.failed=1;
 int result=s.failed||!s.received;
 if(s.keyboard)wl_keyboard_release(s.keyboard);
 if(s.seat)wl_seat_release(s.seat);
 wl_registry_destroy(r);wl_display_flush(display);wl_display_disconnect(display);return result?6:0;
}
