
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
typedef int gboolean;
typedef struct Widget {int index;bool window;struct Widget*parent;} GtkWidget;
typedef struct {char name;GtkWidget*widget,*entry,*landmark,*surface;unsigned long instance,generation;} Role;
typedef struct {Role*role;GtkWidget*parent;} JsonBuilder;
#define TRUE 1
#define FALSE 0
#define GTK_WINDOW(x) (x)
#define GTK_IS_WINDOW(x) ((x)->window)
static Role roles[6];static GtkWidget widgets[6];static int order[6],closed;static JsonBuilder event;
static GtkWidget*gtk_window_get_transient_for(GtkWidget*w){return w->parent;}
static void gtk_window_set_transient_for(GtkWidget*w,GtkWidget*p){w->parent=p;}
static JsonBuilder*record(const char*name,Role*r){(void)name;event.role=r;event.parent=r->widget->parent;return &event;}
static void emit(JsonBuilder*b){assert(b==&event);}
static void close_role(Role*r){if(r->widget){assert(closed<6);order[closed++]=r->widget->index;r->widget=NULL;}}
static void reset(void){closed=0;for(int i=0;i<6;i++){widgets[i]=(GtkWidget){.index=i,.window=i!=4};roles[i]=(Role){.widget=&widgets[i],.entry=&widgets[i],.surface=&widgets[i],.instance=42,.generation=3};}widgets[1].parent=&widgets[0];widgets[3].parent=&widgets[1];widgets[5].parent=&widgets[0];}
static void retire_role(Role*r){
 if(!r->widget)return;
 if(r==&roles[0])close_role(&roles[4]);
 if(GTK_IS_WINDOW(r->widget))for(int i=0;i<6;i++){
  Role*child=&roles[i];
  if(child!=r && child->widget && GTK_IS_WINDOW(child->widget) && (child==&roles[5] || gtk_window_get_transient_for(GTK_WINDOW(child->widget))==GTK_WINDOW(r->widget)))retire_role(child);
 }
 close_role(r);
}
static gboolean reparent_sibling(char parent){
 Role*e=&roles[5];Role*p=parent=='A'?&roles[0]:parent=='B'?&roles[1]:NULL;
 if(!e->widget || !p || !p->widget)return FALSE;
 gtk_window_set_transient_for(GTK_WINDOW(e->widget),GTK_WINDOW(p->widget));
 emit(record("requested-parent",e));return TRUE;
}
int main(void){
reset();retire_role(&roles[1]);assert(closed==2&&order[0]==3&&order[1]==1);assert(roles[5].widget==&widgets[5]&&roles[0].widget&&roles[2].widget);
reset();assert(reparent_sibling('B'));assert(widgets[5].parent==&widgets[1]);assert(event.role==&roles[5]&&event.parent==&widgets[1]);assert(roles[5].instance==42&&roles[5].generation==3&&roles[5].entry==&widgets[5]&&roles[5].surface==&widgets[5]);
retire_role(&roles[1]);assert(closed==3&&order[0]==3&&order[1]==5&&order[2]==1);assert(roles[0].widget&&roles[2].widget);
reset();assert(reparent_sibling('B'));assert(reparent_sibling('A'));retire_role(&roles[1]);assert(roles[5].widget&&widgets[5].parent==&widgets[0]);
reset();retire_role(&roles[0]);assert(closed==5&&order[0]==4&&order[1]==3&&order[2]==1&&order[3]==5&&order[4]==0);assert(roles[2].widget);retire_role(&roles[0]);assert(closed==5);
reset();widgets[5].parent=&widgets[1];retire_role(&roles[0]);assert(closed==5&&order[0]==4&&order[1]==3&&order[2]==5&&order[3]==1&&order[4]==0);assert(roles[2].widget);
reset();assert(!reparent_sibling('C'));assert(!reparent_sibling('E'));assert(widgets[5].parent==&widgets[0]);roles[1].widget=NULL;assert(!reparent_sibling('B'));assert(widgets[5].parent==&widgets[0]);roles[5].widget=NULL;assert(!reparent_sibling('A'));
return 0;}
