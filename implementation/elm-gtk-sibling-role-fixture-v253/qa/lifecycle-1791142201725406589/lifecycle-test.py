"""Actual retirement/reparent code with mock GTK relationships; no native proof."""
import hashlib,json,subprocess,time
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
ROOT=Path(__file__).resolve().parents[1]
spec=spec_from_file_location('extract_callbacks',ROOT/'qa/callback-test.py');m=module_from_spec(spec);spec.loader.exec_module(m)
source=(ROOT/'native/gtk-role-client.c').read_text()
functions={name:m.extract(source,name) for name in ['retire_role','reparent_sibling']}
prefix=r'''
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
'''
body=r'''
int main(void){
reset();retire_role(&roles[1]);assert(closed==2&&order[0]==3&&order[1]==1);assert(roles[5].widget==&widgets[5]&&roles[0].widget&&roles[2].widget);
reset();assert(reparent_sibling('B'));assert(widgets[5].parent==&widgets[1]);assert(event.role==&roles[5]&&event.parent==&widgets[1]);assert(roles[5].instance==42&&roles[5].generation==3&&roles[5].entry==&widgets[5]&&roles[5].surface==&widgets[5]);
retire_role(&roles[1]);assert(closed==3&&order[0]==3&&order[1]==5&&order[2]==1);assert(roles[0].widget&&roles[2].widget);
reset();assert(reparent_sibling('B'));assert(reparent_sibling('A'));retire_role(&roles[1]);assert(roles[5].widget&&widgets[5].parent==&widgets[0]);
reset();retire_role(&roles[0]);assert(closed==5&&order[0]==4&&order[1]==3&&order[2]==1&&order[3]==5&&order[4]==0);assert(roles[2].widget);retire_role(&roles[0]);assert(closed==5);
reset();widgets[5].parent=&widgets[1];retire_role(&roles[0]);assert(closed==5&&order[0]==4&&order[1]==3&&order[2]==5&&order[3]==1&&order[4]==0);assert(roles[2].widget);
reset();assert(!reparent_sibling('C'));assert(!reparent_sibling('E'));assert(widgets[5].parent==&widgets[0]);roles[1].widget=NULL;assert(!reparent_sibling('B'));assert(widgets[5].parent==&widgets[0]);roles[5].widget=NULL;assert(!reparent_sibling('A'));
return 0;}
'''
out=ROOT/'qa'/('lifecycle-'+str(time.time_ns()));out.mkdir()
report={'passed':False,'nativeAcceptance':False,'sourceSHA256':hashlib.sha256(source.encode()).hexdigest(),'scope':'actual extracted relationship functions with mock GTK; no display, input or native parent qualification'}
try:
 (out/'source.c').write_text(source);(out/'lifecycle-test.py').write_bytes(Path(__file__).read_bytes())
 def run(directory,funcs):
  directory.mkdir(exist_ok=True);(directory/'test.c').write_text(prefix+'\n'.join(funcs.values())+body)
  result=subprocess.run(['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(directory/'test.c'),'-o',str(directory/'test')],capture_output=True,timeout=30)
  (directory/'compile.stderr').write_bytes(result.stderr);assert result.returncode==0,result.stderr.decode()
  result=subprocess.run([str(directory/'test')],capture_output=True,timeout=3);(directory/'run.stderr').write_bytes(result.stderr);return result.returncode
 assert run(out,functions)==0
 controls=[]
 for label,func,old,new in [('wrong-parent','reparent_sibling','GTK_WINDOW(p->widget));','GTK_WINDOW(roles[0].widget));'),('retire-unrelated-sibling','retire_role','==GTK_WINDOW(r->widget)','!=NULL')]:
  changed=dict(functions);assert old in changed[func];changed[func]=changed[func].replace(old,new);code=run(out/label,changed);assert code!=0,label;controls.append({'name':label,'exitCode':code,'rejected':True})
 report.update(passed=True,assertions=body.count('assert('),unsafeControls=controls)
except BaseException as error:report['error']=repr(error)
finally:
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
raise SystemExit(0 if report['passed'] else 1)
