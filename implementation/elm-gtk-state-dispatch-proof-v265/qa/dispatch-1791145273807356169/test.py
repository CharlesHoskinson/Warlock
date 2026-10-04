"""Actual extracted GTK state API dispatch; no toolkit/native effect inference."""
import hashlib,json,resource,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
FIXTURE=REPO/'implementation/elm-gtk-sibling-role-fixture-v253'
CONSUMER=REPO/'implementation/elm-gtk-sibling-consumer-v257'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
out=ROOT/'qa'/('dispatch-'+str(time.time_ns()));out.mkdir()
report={'passed':False,'nativeAcceptance':False,'gtk02Accepted':False,'checks':[]}
def check(name,ok,**data):
 report['checks'].append({'name':name,'passed':bool(ok),**data});assert ok,name
try:
 for base,expected in [(FIXTURE,'32f0cc1aff70793ef9cc2d1bc76508806500a5be34df386696d5db4aa5cc4758'),(CONSUMER,'a4c4ba426a95b47e39cb94310826d7ceb0cf58c4a856a497890381f06f852817')]:
  manifest=base/'component-manifest.json';check(base.name+':held',sha(manifest)==expected)
  data=json.loads(manifest.read_text())
  for filename in (['native/gtk-role-client.c','native/commands.h'] if base==FIXTURE else ['qa/actor.py']):
   check(filename+':actual-held-source',sha(base/filename)==data['files'][filename]['sha256'])
 body=(FIXTURE/'native/gtk-role-client.c').read_text();start=body.index(" Role*r=c->role=='A'?&roles[0]:&roles[2];")
 dispatch=body[start:body.index('\n}',start)]
 prelude=r'''#define _POSIX_C_SOURCE 200809L
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
'''
 suffix=r'''
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
'''
 (out/'actual-dispatch.txt').write_text(dispatch)
 def run(name,source):
  directory=out/name;directory.mkdir();(directory/'commands.h').write_bytes((FIXTURE/'native/commands.h').read_bytes());(directory/'test.c').write_text(prelude+source+suffix)
  command=['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(directory/'test.c'),'-o',str(directory/'test')]
  p=subprocess.run(command,capture_output=True,timeout=20);(directory/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr
  p=subprocess.run([str(directory/'test')],capture_output=True,timeout=3);(directory/'execute.stderr').write_bytes(p.stderr)
  return p.returncode
 check('actual-four-operations-both-owners-and-refusal',run('production',dispatch)==0)
 for name,old,new in [('wrong-max-api','gtk_window_maximize(w)','gtk_window_unmaximize(w)'),('wrong-owner',"c->role=='A'?&roles[0]:&roles[2]","c->role=='A'?&roles[2]:&roles[0]")]:
  assert dispatch.count(old)==1
  code=run(name,dispatch.replace(old,new,1));check('applied-'+name+'-rejected',code!=0,exit=code)
 report.update(passed=True,sourceSHA256=sha(__file__),inputs={str(p):sha(p) for p in [FIXTURE/'native/gtk-role-client.c',FIXTURE/'native/commands.h',CONSUMER/'qa/actor.py']},compilerSHA256=sha('/usr/bin/cc'))
finally:
 (out/'test.py').write_bytes(Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
if report['passed']:
 manifest=ROOT/'component-manifest.json';assert not manifest.exists()
 files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file()}
 manifest.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'gtk02Accepted':False,'files':files,'externalFiles':report['inputs'],'report':str(out/'report.json')},indent=2)+'\n')
