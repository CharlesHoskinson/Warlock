#define main fixture_main
#include "xdg-origin-client.c"
#undef main
static unsigned connections;
struct wl_display *__wrap_wl_display_connect(const char *name){(void)name;++connections;return NULL;}
int main(void){
 struct client c={.surface=(struct wl_surface *)(uintptr_t)1};
 pointer_enter(&c,NULL,5,c.surface,4224,6208);
 pointer_button(&c,NULL,6,100,272,1);
 pointer_button(&c,NULL,7,101,272,0);
 pointer_enter(&c,NULL,8,(struct wl_surface *)(uintptr_t)2,4224,6208);
 pointer_button(&c,NULL,9,102,272,1);
 printf("{\"connections\":%u}\n",connections);return connections?1:0;
}
