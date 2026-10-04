"""Execute actual popup paint/click callback bodies with instrumented GTK/Cairo."""
import hashlib,json,subprocess,time
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('callbacks',ROOT/'qa/callback-test.py');callbacks=importlib.util.module_from_spec(spec);spec.loader.exec_module(callbacks)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=ROOT/'qa'/('popup-'+str(time.time_ns()));out.mkdir()
source=(ROOT/'native/gtk-role-client.c').read_text();functions={n:callbacks.extract(source,n) for n in ['draw_popup','popover_clicked']}
prefix=r'''
#include <assert.h>
#include <stddef.h>
#include <string.h>
typedef struct Widget{struct Widget*ancestor;}GtkWidget;
typedef GtkWidget GtkButton;typedef GtkWidget GtkDrawingArea;typedef void* gpointer;
typedef struct{GtkWidget*widget,*landmark,*button;}Role;
typedef struct{int unused;}cairo_t;typedef struct{int unused;}JsonBuilder;
#define GTK_WIDGET(x) ((GtkWidget*)(x))
#define GTK_TYPE_POPOVER 1
static int emitted,closed,painted,filled,rectangles;
static double rgb[3],rect[4];static JsonBuilder builder;
static GtkWidget*gtk_widget_get_ancestor(GtkWidget*w,int type){assert(type==GTK_TYPE_POPOVER);return w->ancestor;}
static void cairo_set_source_rgb(cairo_t*c,double r,double g,double b){(void)c;rgb[0]=r;rgb[1]=g;rgb[2]=b;}
static void cairo_paint(cairo_t*c){(void)c;assert(rgb[0]==.1&&rgb[1]==.1&&rgb[2]==.1);painted++;}
static void cairo_rectangle(cairo_t*c,double x,double y,double w,double h){(void)c;rect[0]=x;rect[1]=y;rect[2]=w;rect[3]=h;rectangles++;}
static void cairo_fill(cairo_t*c){(void)c;assert(rgb[0]==1&&rgb[1]==0&&rgb[2]==1);assert(rect[0]==4&&rect[1]==4&&rect[2]==8&&rect[3]==8);filled++;}
static JsonBuilder*record(const char*name,Role*r){assert(r->widget);assert(!strcmp(name,"draw-queued")||!strcmp(name,"popover-button-clicked"));return &builder;}
static void integer(JsonBuilder*b,const char*k,int value){(void)b;assert((!strcmp(k,"drawWidth")&&value==64)||(!strcmp(k,"drawHeight")&&value==40));}
static void emit(JsonBuilder*b){assert(b==&builder);emitted++;}
static void close_role(Role*r){closed++;r->widget=NULL;r->landmark=NULL;r->button=NULL;}
'''
body=r'''
int main(void){
 GtkWidget popup={NULL},foreign={NULL},area={&popup},staleArea={&popup},button={&popup},staleButton={&popup};cairo_t cr={0};Role r={&popup,&area,&button};
 draw_popup(&staleArea,&cr,64,40,&r);assert(emitted==0&&painted==0);
 area.ancestor=&foreign;draw_popup(&area,&cr,64,40,&r);assert(emitted==0&&painted==0);area.ancestor=&popup;
 r.widget=NULL;draw_popup(&area,&cr,64,40,&r);assert(emitted==0&&painted==0);r.widget=&popup;
 draw_popup(&area,&cr,64,40,&r);assert(emitted==1&&painted==1&&filled==1&&rectangles==1);
 popover_clicked(&staleButton,&r);assert(emitted==1&&closed==0&&r.widget==&popup);
 button.ancestor=&foreign;popover_clicked(&button,&r);assert(emitted==1&&closed==0);button.ancestor=&popup;
 popover_clicked(&button,&r);assert(emitted==2&&closed==1&&!r.widget&&!r.landmark&&!r.button);
 draw_popup(&area,&cr,64,40,&r);popover_clicked(&button,&r);assert(emitted==2&&closed==1&&painted==1);
 r.widget=&foreign;r.landmark=&staleArea;r.button=&staleButton;draw_popup(&area,&cr,64,40,&r);popover_clicked(&button,&r);assert(emitted==2&&closed==1&&painted==1);
 return 0;}
'''
report={'passed':False,'nativeAcceptance':False,'sourceSHA256':sha(ROOT/'native/gtk-role-client.c'),'checks':body.count('assert('),'controls':[]}
try:
 def run(name,funcs):
  d=out/name;d.mkdir();(d/'test.c').write_text(prefix+'\n'.join(funcs.values())+body)
  p=subprocess.run(['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],capture_output=True,timeout=20);(d/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr
  p=subprocess.run([str(d/'test')],capture_output=True,timeout=3);(d/'execute.stderr').write_bytes(p.stderr);return p.returncode
 assert run('production',functions)==0
 for name,fn,old,new in [('stale-area','draw_popup','GTK_WIDGET(area)!=r->landmark || ',''),('stale-button','popover_clicked','GTK_WIDGET(button)==r->button && ',''),('foreign-popover','draw_popup','gtk_widget_get_ancestor(GTK_WIDGET(area),GTK_TYPE_POPOVER)!=r->widget','0')]:
  assert functions[fn].count(old)==1
  changed=dict(functions);changed[fn]=changed[fn].replace(old,new,1);code=run(name,changed);assert code!=0,name;report['controls'].append({'name':name,'rejected':True,'exitCode':code})
 report['passed']=True
finally:
 (out/'source.c').write_text(source);(out/'popup-test.py').write_bytes(Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
