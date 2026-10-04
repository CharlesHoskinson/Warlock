#define _POSIX_C_SOURCE 200809L
#include "parent-input-client.h"
#include <wayland-client.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
struct client;
static struct client *active;
static unsigned sent, observed, dispatched;
static uint32_t last_key,last_state,last_sequence;
static int32_t last_pid;
static void fake_key(struct elm_parent_input_v1*,uint32_t,uint32_t,uint32_t);
static void fake_observe(struct elm_parent_surface_observer_v1*,uint32_t,int32_t,const char*);
static int fake_dispatch(struct wl_display*);
#define elm_parent_input_v1_key fake_key
#define elm_parent_surface_observer_v1_observe fake_observe
#define wl_display_dispatch fake_dispatch
#define main inherited_main
#include "parent-input-client.c"
#undef main
static void fake_key(struct elm_parent_input_v1*p,uint32_t sequence,uint32_t key,uint32_t state){assert(p==active->probe);sent++;last_key=key;last_state=state;last_sequence=sequence;active->received=true;active->accepted=true;}
static void fake_observe(struct elm_parent_surface_observer_v1*p,uint32_t sequence,int32_t pid,const char*started){assert(p==active->observer);assert(!strcmp(started,"123"));observed++;last_pid=pid;last_sequence=sequence;active->received=true;active->accepted=true;}
static int fake_dispatch(struct wl_display*d){(void)d;dispatched++;return -1;}
static unsigned checks;
#define CHECK(v) do{assert(v);checks++;}while(0)
int main(void){
 struct client c={.probe=(void*)1,.observer=(void*)2,.display=(void*)3};active=&c;
 CHECK(send_key(&c,30,1));CHECK(c.sequence==1&&last_key==30&&last_state==1&&last_sequence==1);
 CHECK(send_observe(&c,27,"123"));CHECK(c.sequence==2&&last_sequence==2&&last_pid==27&&observed==1);
 CHECK(send_key(&c,30,0));CHECK(c.sequence==3&&last_state==0&&sent==2&&dispatched==0);
 CHECK(!send_observe(&c,27,"x"));CHECK(!send_observe(&c,27,""));CHECK(!send_observe(&c,27,"123456789012345678901"));CHECK(c.sequence==3&&observed==1);
 c.sequence=UINT32_MAX;CHECK(!send_observe(&c,27,"123"));CHECK(c.sequence==UINT32_MAX&&observed==1);CHECK(!send_key(&c,30,1));CHECK(sent==2);
 c.sequence=3;c.probe=NULL;CHECK(!send_key(&c,30,1));CHECK(c.sequence==3);c.probe=(void*)1;c.observer=NULL;CHECK(!send_observe(&c,27,"123"));CHECK(c.sequence==3);c.observer=(void*)2;
 c.waiting=19;c.received=false;done(&c,c.probe,18,1);CHECK(!c.received);done(&c,c.probe,19,2);CHECK(!c.received);done(&c,c.probe,19,1);CHECK(c.received&&c.accepted);
 c.received=false;observation(&c,c.observer,18,1,"{}");CHECK(!c.received);observation(&c,c.observer,19,2,"{}");CHECK(!c.received);observation(&c,c.observer,19,1,NULL);CHECK(!c.received);
 char large[4097];memset(large,'x',4096);large[4096]=0;observation(&c,c.observer,19,1,large);CHECK(!c.received);observation(&c,c.observer,19,1,"{\"schema\":1}");CHECK(c.received&&c.accepted);
 printf("checks=%u\n",checks);return 0;
}
