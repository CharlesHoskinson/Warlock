#!/usr/bin/python3
import hashlib,json,pathlib,subprocess,time,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def extract(source,name):
 import re
 match=re.search(r'static [^\n{]+\b'+name+r'\([^\n]*?\)\{',source)
 assert match,name
 start=match.start();pos=match.end();depth=1
 while depth:
  if source[pos]=='{':depth+=1
  elif source[pos]=='}':depth-=1
  pos+=1
 return source[start:pos]
def main():
 out=ROOT/'qa'/f'callbacks-{time.time_ns()}';out.mkdir(mode=0o700);source=(ROOT/'native/gtk-role-client.c').read_text();shutil.copyfile(ROOT/'native/gtk-role-client.c',out/'gtk-role-client.c');shutil.copyfile(__file__,out/'callback-test.py')
 funcs={name:extract(source,name) for name in ['current_controller','pressed','key_pressed','state_changed','close_role']}
 prefix=r'''
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
'''
 body=r'''
int main(void){GtkWidget live={1},old={2},surface={3},foreign={4};GtkEventController current={&live},stale={&old};Role r={.widget=&live,.surface=&surface,.instance=2};
assert(gtk_event_controller_get_widget(&current)==&live);assert(current_controller(&r,&current));assert(!current_controller(&r,&stale));r.widget=NULL;assert(!current_controller(&r,&current));r.widget=&live;
pressed(&stale,1,3,4,&r);assert(emitted==0);pressed(&current,1,3,4,&r);assert(emitted==1);
assert(key_pressed(&stale,1,2,0,&r)==FALSE);assert(emitted==1);assert(key_pressed(&current,1,2,0,&r)==FALSE);assert(emitted==2);
state_changed(&foreign,NULL,&r);assert(emitted==2);state_changed(&surface,NULL,&r);assert(emitted==3);
r.controllers[0]=&current;r.controllers[1]=&stale;r.controllers[2]=&current;r.entry=&live;r.landmark=&live;
close_role(&r);assert(disconnected==5&&destroyed==1);assert(!r.widget&&!r.surface&&!r.entry&&!r.landmark);for(int i=0;i<3;i++)assert(!r.controllers[i]);int previous=emitted;close_role(&r);assert(emitted==previous);
r.widget=&old;r.surface=&foreign;r.instance=3;pressed(&current,1,3,4,&r);assert(emitted==previous);state_changed(&surface,NULL,&r);assert(emitted==previous);
close_role(&r);assert(popdown==1&&unparented==1&&destroyed==1);return 0;}
'''
 report={'passed':False,'nativeAcceptance':False,'sourceSHA256':sha(ROOT/'native/gtk-role-client.c'),'scope':'actual extracted callbacks with mock GTK objects; no GTK display/input/native proof'}
 try:
  def compile_run(directory,functions):
   (directory/'test.c').write_text(prefix+'\n'.join(functions.values())+body);p=subprocess.run(['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(directory/'test.c'),'-o',str(directory/'test')],capture_output=True);(directory/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr;return subprocess.run([str(directory/'test')],capture_output=True).returncode
  assert compile_run(out,funcs)==0
  mutants=[]
  for name,change in [('stale-controller',lambda d:d.update(current_controller=d['current_controller'].replace('r->widget && gtk_event_controller_get_widget(c)==r->widget','(void)c, r->widget!=NULL'))),('missing-controller-disconnect',lambda d:d.update(close_role=d['close_role'].replace('g_signal_handlers_disconnect_by_data(r->controllers[i],r);',''))),('stale-surface',lambda d:d.update(state_changed=d['state_changed'].replace('object!=G_OBJECT(r->surface)||','(void)object, ')))]:
   d=dict(funcs);change(d);directory=out/name;directory.mkdir();code=compile_run(directory,d);assert code!=0,name;mutants.append({'name':name,'exit':code,'rejected':True})
  report.update(passed=True,extracted={name:hashlib.sha256(text.encode()).hexdigest() for name,text in funcs.items()},checks=body.count("assert("),mutants=mutants)
 except Exception as e:report['error']=str(e)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
