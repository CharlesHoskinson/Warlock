#define _POSIX_C_SOURCE 200809L
#include <libweston/libweston.h>
#include "libweston/backend.h"
#include "libweston/libweston-internal.h"
#include "parent-input-server.h"
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <assert.h>
#include <stdio.h>
#include <math.h>
/* Actual producer struct copied byte-for-byte by the test runner. */
#include "probe-struct.h"
struct fake_client {pid_t pid;uid_t uid;};
struct fake_resource {struct fake_client *client;uint32_t id;};
static void mock_credentials(struct wl_client *c,pid_t *pid,uid_t *uid,gid_t *gid) {struct fake_client *f=(void*)c;*pid=f->pid;*uid=f->uid;*gid=getegid();}
static struct wl_client *mock_client(struct wl_resource *r) {return (void*)((struct fake_resource*)(void*)r)->client;}
static uint32_t mock_id(struct wl_resource *r) {return ((struct fake_resource*)(void*)r)->id;}
static const char *role="xdg_toplevel";
static const char *mock_role(struct weston_surface *s) {(void)s;return role;}
static bool mock_mapped(struct weston_view *v) {return v->is_mapped;}
static struct weston_pointer *selected_pointer;
static struct weston_pointer *mock_pointer(struct weston_seat *seat) {(void)seat;return selected_pointer;}
static unsigned conversions;
static bool bad_coordinate;
static struct weston_coord_global mock_global(const struct weston_view *view,struct weston_coord_surface coordinate) {
    assert(!view->transform.dirty && coordinate.coordinate_space_id==view->surface);conversions++;
    struct weston_coord_global result={.c=weston_coord(coordinate.c.x+13,coordinate.c.y+17)};
    if (bad_coordinate) result.c.x=NAN;
    return result;
}
#define wl_client_get_credentials mock_credentials
#define wl_resource_get_client mock_client
#define wl_resource_get_id mock_id
#define weston_surface_get_role mock_role
#define weston_view_is_mapped mock_mapped
#define weston_seat_get_pointer mock_pointer
#define weston_coord_surface_to_global mock_global
#include "surface-observer.h"
static unsigned checks;
#define CHECK(value) do {assert(value);checks++;} while(0)
int main(void) {
    char started[21];CHECK(process_started(getppid(),started));CHECK(!process_started(-1,started));CHECK(safe_name("headless-1"));CHECK(!safe_name("unsafe\"name"));
    struct weston_compositor compositor={0};wl_list_init(&compositor.view_list);wl_list_init(&compositor.output_list);
    struct weston_seat seat={0};struct weston_pointer pointer={0};selected_pointer=&pointer;
    struct fake_client controller={.pid=getpid(),.uid=geteuid()},target={.pid=getppid(),.uid=geteuid()};
    struct fake_resource control_resource={.client=&controller,.id=2},surface_resource={.client=&target,.id=19};
    struct weston_surface surface={.resource=(void*)&surface_resource,.width=800,.height=600};surface.buffer_viewport.surface.width=800;surface.buffer_viewport.surface.height=600;
    struct weston_view view={.surface=&surface,.is_mapped=true};wl_signal_init(&view.destroy_signal);wl_list_insert(&compositor.view_list,&view.link);
    struct weston_mode mode={.width=800,.height=600};struct weston_output output={.id=0,.name="headless",.enabled=true,.width=800,.height=600,.current_mode=&mode,.current_scale=1};wl_list_insert(&compositor.output_list,&output.link);
    struct probe probe={.compositor=&compositor,.seat=&seat,.controller=(void*)&control_resource};wl_list_init(&probe.observed_destroy.link);probe.observed_destroy.notify=observed_view_destroyed;
    pointer.focus=&view;pointer.pos.c=weston_coord(100,120);
    char packet[4096];CHECK(observation_packet(&probe,(void*)&controller,1,getppid(),started,packet));
    CHECK(conversions==4 && probe.view_identity==1 && probe.observation_revision==1);CHECK(strstr(packet,"\"corners\":[[13,17],[813,17],[13,617],[813,617]]"));CHECK(strstr(packet,"\"focusedViewId\":1"));puts(packet);
    CHECK(observation_packet(&probe,(void*)&controller,2,getppid(),started,packet));CHECK(probe.view_identity==1 && probe.observation_revision==2);
    CHECK(!observation_packet(&probe,(void*)&controller,0,getppid(),started,packet));CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),"0",packet));
    target.uid=geteuid()+1;CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));target.uid=geteuid();
    role="wl_pointer-cursor";CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));role="xdg_toplevel";
    view.parent_view=&view;CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));view.parent_view=NULL;
    view.transform.dirty=true;unsigned before=conversions;CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));CHECK(conversions==before);view.transform.dirty=false;
    struct weston_view duplicate={.surface=&surface,.is_mapped=true};wl_signal_init(&duplicate.destroy_signal);wl_list_insert(&compositor.view_list,&duplicate.link);CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));wl_list_remove(&duplicate.link);
    surface.width=4097;CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));surface.width=800;
    output.current_scale=3;CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));output.current_scale=1;
    bad_coordinate=true;CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));bad_coordinate=false;
    mode.width=0;CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));mode.width=800;
    mode.height=8193;CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));mode.height=600;
    struct weston_output extra_output={.enabled=true};wl_list_insert(&compositor.output_list,&extra_output.link);CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));wl_list_remove(&extra_output.link);
    selected_pointer=NULL;CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));selected_pointer=&pointer;
    CHECK(!observation_packet(&probe,(void*)&controller,3,getpid(),started,packet));
    CHECK(probe.observation_revision==2);probe.observation_revision=UINT32_MAX;CHECK(!observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));probe.observation_revision=2;
    wl_signal_emit(&view.destroy_signal,&view);CHECK(probe.observed_view==NULL);CHECK(observation_packet(&probe,(void*)&controller,3,getppid(),started,packet));CHECK(probe.view_identity==2);
    wl_signal_emit(&view.destroy_signal,&view);probe.view_identity=UINT32_MAX;CHECK(!observation_packet(&probe,(void*)&controller,4,getppid(),started,packet));
    printf("checks=%u\n",checks);return 0;
}
