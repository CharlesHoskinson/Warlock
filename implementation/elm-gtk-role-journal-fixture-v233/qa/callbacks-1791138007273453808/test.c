
#include <stdbool.h>
#include <stdint.h>
#include <assert.h>
typedef int gboolean;typedef unsigned guint;typedef unsigned GdkModifierType;typedef void* gpointer;typedef void GParamSpec;typedef struct{int id;} GtkWidget;typedef struct{GtkWidget*widget;} GtkEventController;typedef GtkEventController GtkEventControllerKey;typedef GtkEventController GtkGestureClick;typedef GtkEventController GtkGestureSingle;typedef GtkWidget GObject;typedef GtkWidget GdkSurface;typedef struct{int unused;} JsonBuilder;
typedef struct{char name;GtkWidget*widget,*entry,*landmark;GtkEventController*controllers[3];GdkSurface*surface;uint64_t instance,generation;}Role;
#define GTK_EVENT_CONTROLLER(x) ((GtkEventController*)(x))
#define GTK_GESTURE_SINGLE(x) ((GtkGestureSingle*)(x))
#define G_OBJECT(x) ((GObject*)(x))
#define GTK_IS_WINDOW(x) ((x)->id==1)
#define GTK_WINDOW(x) (x)
#define GTK_POPOVER(x) (x)
#define TRUE 1
#define FALSE 0
#define g_clear_object(p) (*(p)=NULL)
#include <stddef.h>
static int emitted,disconnected,destroyed,popdown,unparented;static JsonBuilder builder;
static GtkWidget*gtk_event_controller_get_widget(GtkEventController*c){return c->widget;}
static JsonBuilder*record(const char*event,Role*r){(void)event;(void)r;return &builder;}
static JsonBuilder*input_record(const char*event,Role*r,GtkEventController*c){(void)c;return record(event,r);}
static unsigned gtk_gesture_single_get_current_button(GtkGestureSingle*c){(void)c;return 1;}
static void integer(JsonBuilder*b,const char*key,long n){(void)b;(void)key;(void)n;}
static void number(JsonBuilder*b,const char*key,double n){(void)b;(void)key;(void)n;}
static void emit(JsonBuilder*b){(void)b;emitted++;}
static void g_signal_handlers_disconnect_by_data(void*object,Role*r){assert(object);assert(r);disconnected++;}
static void gtk_window_destroy(GtkWidget*w){assert(w);destroyed++;}
static void gtk_popover_popdown(GtkWidget*w){assert(w);popdown++;}
static void gtk_widget_unparent(GtkWidget*w){assert(w);unparented++;}
static gboolean current_controller(Role*r,GtkEventController*c){return r->widget && gtk_event_controller_get_widget(c)==r->widget;}
static void pressed(GtkGestureClick *c,int count,double x,double y,gpointer data){if(!current_controller(data,GTK_EVENT_CONTROLLER(c)))return;JsonBuilder*b=input_record("button-press",data,GTK_EVENT_CONTROLLER(c));integer(b,"button",gtk_gesture_single_get_current_button(GTK_GESTURE_SINGLE(c)));integer(b,"clickCount",count);number(b,"widgetX",x);number(b,"widgetY",y);emit(b);}
static gboolean key_pressed(GtkEventControllerKey*c,guint key,guint code,GdkModifierType state,gpointer data){if(!current_controller(data,GTK_EVENT_CONTROLLER(c)))return FALSE;JsonBuilder*b=input_record("key-press",data,GTK_EVENT_CONTROLLER(c));integer(b,"keyval",key);integer(b,"keycode",code);integer(b,"modifiers",state);emit(b);return FALSE;}
static void state_changed(GObject *object,GParamSpec *spec,gpointer data){(void)spec;Role*r=data;if(object!=G_OBJECT(r->surface)||!r->widget)return;emit(record("surface-state",r));}
static void close_role(Role*r){if(!r->widget)return;emit(record("destroy-request",r));for(int i=0;i<3;i++){if(r->controllers[i]){g_signal_handlers_disconnect_by_data(r->controllers[i],r);g_clear_object(&r->controllers[i]);}}r->entry=NULL;r->landmark=NULL;if(r->surface){g_signal_handlers_disconnect_by_data(r->surface,r);g_clear_object(&r->surface);}g_signal_handlers_disconnect_by_data(r->widget,r);if(GTK_IS_WINDOW(r->widget))gtk_window_destroy(GTK_WINDOW(r->widget));else{gtk_popover_popdown(GTK_POPOVER(r->widget));gtk_widget_unparent(r->widget);}g_clear_object(&r->widget);emit(record("local-destroy",r));}
int main(void){GtkWidget live={1},old={2},surface={3},foreign={4};GtkEventController current={&live},stale={&old};Role r={.widget=&live,.surface=&surface,.instance=2};
assert(gtk_event_controller_get_widget(&current)==&live);assert(current_controller(&r,&current));assert(!current_controller(&r,&stale));r.widget=NULL;assert(!current_controller(&r,&current));r.widget=&live;
pressed(&stale,1,3,4,&r);assert(emitted==0);pressed(&current,1,3,4,&r);assert(emitted==1);
assert(key_pressed(&stale,1,2,0,&r)==FALSE);assert(emitted==1);assert(key_pressed(&current,1,2,0,&r)==FALSE);assert(emitted==2);
state_changed(&foreign,NULL,&r);assert(emitted==2);state_changed(&surface,NULL,&r);assert(emitted==3);
r.controllers[0]=&current;r.controllers[1]=&stale;r.controllers[2]=&current;r.entry=&live;r.landmark=&live;
close_role(&r);assert(disconnected==5&&destroyed==1);assert(!r.widget&&!r.surface&&!r.entry&&!r.landmark);for(int i=0;i<3;i++)assert(!r.controllers[i]);int previous=emitted;close_role(&r);assert(emitted==previous);
r.widget=&old;r.surface=&foreign;r.instance=3;pressed(&current,1,3,4,&r);assert(emitted==previous);state_changed(&surface,NULL,&r);assert(emitted==previous);
close_role(&r);assert(popdown==1&&unparented==1&&destroyed==1);return 0;}
