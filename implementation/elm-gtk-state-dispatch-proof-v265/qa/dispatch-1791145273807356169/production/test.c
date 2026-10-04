#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include "commands.h"
typedef bool gboolean;
typedef struct {void *widget;} Role;
typedef void GtkWindow;
static Role roles[6];
static int operation,emitted;
static void *target;
#define FALSE false
#define TRUE true
#define GTK_WINDOW(w) ((GtkWindow*)(w))
static void gtk_window_minimize(GtkWindow*w){operation=1;target=w;}
static void gtk_window_unminimize(GtkWindow*w){operation=2;target=w;}
static void gtk_window_maximize(GtkWindow*w){operation=3;target=w;}
static void gtk_window_unmaximize(GtkWindow*w){operation=4;target=w;}
static Role *record(const char *event,Role*r){assert(!strcmp(event,"requested-state"));return r;}
static void emit(Role*r){assert(r->widget==target);emitted++;}
static gboolean dispatch(struct command*c){
 Role*r=c->role=='A'?&roles[0]:&roles[2];if(!r->widget)return FALSE;GtkWindow*w=GTK_WINDOW(r->widget);if(!strcmp(c->operation,"minimize"))gtk_window_minimize(w);else if(!strcmp(c->operation,"restore"))gtk_window_unminimize(w);else if(!strcmp(c->operation,"maximize"))gtk_window_maximize(w);else if(!strcmp(c->operation,"unmaximize"))gtk_window_unmaximize(w);else return FALSE;emit(record("requested-state",r));return TRUE;
}
int main(void){
 int ownerA,ownerC;roles[0].widget=&ownerA;roles[2].widget=&ownerC;
 const char *operations[]={"minimize","restore","maximize","unmaximize"};
 for(int role=0;role<2;role++)for(int op=0;op<4;op++){
  struct command c={.sequence=1,.role=role?'C':'A'};strcpy(c.operation,operations[op]);
  operation=0;target=NULL;emitted=0;
  assert(dispatch(&c));assert(operation==op+1);assert(target==(role?(void*)&ownerC:(void*)&ownerA));assert(emitted==1);
 }
 for(int role=0;role<2;role++){
  struct command c={.sequence=1,.role=role?'C':'A'};strcpy(c.operation,"maximize");
  void *saved=roles[role?2:0].widget;roles[role?2:0].widget=NULL;operation=0;emitted=0;
  assert(!dispatch(&c));assert(operation==0&&emitted==0);roles[role?2:0].widget=saved;
 }
 struct command c;assert(!parse_command("1 maximize B",&c));assert(!parse_command("2 unmaximize E",&c));
 return 0;
}
