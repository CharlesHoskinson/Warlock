#include <wayland-util.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
struct probe { void *seat; bool held[3]; struct wl_listener { struct wl_list link; } seat_destroy; };
static unsigned deliveries;
static void release_all(struct probe *p) { (void)p; deliveries++; }
static void seat_destroyed(struct wl_listener *listener, void *data) {
    (void)data;
    struct probe *probe = wl_container_of(listener, probe, seat_destroy);
    release_all(probe);
    probe->seat = NULL;
    wl_list_remove(&probe->seat_destroy.link);
    wl_list_init(&probe->seat_destroy.link);
}
int main(void) {
 for (unsigned mask=0; mask<8; ++mask) {
  struct wl_list listeners; wl_list_init(&listeners);
  struct probe p={.seat=(void*)1};
  for (unsigned i=0;i<3;i++) p.held[i]=(mask & (1u<<i))!=0;
  wl_list_init(&p.seat_destroy.link); wl_list_insert(&listeners,&p.seat_destroy.link);
  deliveries=0; seat_destroyed(&p.seat_destroy,NULL);
  if(deliveries||p.seat||p.held[0]||p.held[1]||p.held[2]||!wl_list_empty(&listeners)||!wl_list_empty(&p.seat_destroy.link)) return 1;
 }
 puts("8 held-button retirement states passed");return 0;
}
