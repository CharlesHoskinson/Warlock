import hashlib,json,pathlib,shlex,shutil,subprocess,sys,time,os
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope()
r=pathlib.Path(__file__).resolve().parents[1];out=r/'qa'/('ownership-'+str(time.time_ns()));out.mkdir();checks=[];shutil.copy2(r/'qa/ownership.py',out/'runner-source.py');shutil.copy2(r/'qa/ownership-probe.c',out/'probe-source.c')
parent=r.parent/'elm-topology-negative-disposition-experiment-v710'
packet=parent/'qa/negative-1791164368163016761/packet.json';shutil.copy2(packet,out/'packet.json')
flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0'],text=True))
def prepare(name,base,owned,mutant=None):
 d=out/name;shutil.copytree(base/'native',d/'native');(d/'qa').mkdir();shutil.copy2(r/'qa/ownership-probe.c',d/'qa/ownership-probe.c')
 s=(base/'native/shared-host.c').read_text()
 instrumentation='''#define surface_eval inherited_surface_eval
#include "../native/host.c"
#undef surface_eval
static JsonNode *captured_packet;
static guint captured_count,owned_allocated,owned_freed;
static void surface_eval(WebKitWebView *target,const char *function,JsonNode *packet){(void)target;if(g_str_equal(function,"receiveBatchDisposition")){captured_count++;if(captured_packet)json_node_unref(captured_packet);captured_packet=json_node_copy(packet);}}
'''
 s=s.replace('#include "host.c"',instrumentation).replace('#include "context-keys.h"','#include "../native/context-keys.h"').replace('#include "shared-context.h"','#include "../native/shared-context.h"')
 decl='static void hook(JsonNode *,const char *,SharedBatchRecord *,gboolean);\n'
 needle='static void shared_commit(JsonNode *root,const char *original) {';assert needle in s;s=s.replace(needle,decl+needle)
 needle='record=shared_batch_reserve(root,original,&duplicate);';assert s.count(needle)==1;s=s.replace(needle,needle+'hook(root,original,record,duplicate);')
 if owned:
  s=s.replace('g_ref_count_init(&row->refs);','g_ref_count_init(&row->refs);owned_allocated++;')
  s=s.replace('g_free(row);}}','owned_freed++;g_free(row);}}')
  if mutant:
   old,new=mutant;assert old in s;s=s.replace(old,new)
 else:s=s.replace('static guint captured_count,owned_allocated,owned_freed;','static guint captured_count;')
 (d/'qa/instrumented-shared-host.c').write_text(s)
 cmd=['cc','-std=c11','-g','-O1','-fsanitize=address','-fno-omit-frame-pointer','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-Wno-misleading-indentation','-DOWNED730='+str(int(owned)),'qa/ownership-probe.c','-o',str(d/'probe'),*flags]
 p=subprocess.run(cmd,cwd=d,capture_output=True,text=True);(d/'compile.stdout').write_text(p.stdout);(d/'compile.stderr').write_text(p.stderr);assert p.returncode==0,p.stderr
 return d
try:
 original=prepare('original710',parent,False)
 d=prepare('candidate730',r,True)
 m=prepare('mutant-borrowed-reference',r,True,('shared_batch_highest=publication;return shared_batch_ref(row);','shared_batch_highest=publication;return row;'))
 leak=prepare('mutant-leaked-caller',r,True,('g_autoptr(SharedBatchRecord) record=','SharedBatchRecord *record='))
 provisional=prepare('mutant-provisional-processing',r,True,('!row || !row->finished ||','!row ||'))
 overwrite=prepare('mutant-rewrite-first',r,True,('if(!row->finished){','if(TRUE){'))
 relabel=prepare('mutant-old-binding-emit',r,True,(' || !json_node_equal(json_object_get_member(json_node_get_object(row->certificate),"binding"),authority_binding)',''))
 for name,base,mode,expected in [('original710-nested17',original,'nested-17','asan'),('candidate-nested17',d,'nested-17','pass'),('candidate-binding-reset',d,'binding-reset','pass'),('candidate-processing-duplicate',d,'processing-duplicate','pass'),('candidate-immutable-first',d,'immutable-first','pass'),('candidate-normal',d,'normal','pass'),('mutant-borrowed-reference',m,'nested-17','asan'),('mutant-leaked-caller',leak,'normal','assertion'),('mutant-provisional-processing',provisional,'processing-duplicate','assertion'),('mutant-rewrite-first',overwrite,'immutable-first','assertion'),('mutant-old-binding-emit',relabel,'binding-reset','assertion')]:
  p=subprocess.run([str(base/'probe'),str(out/'packet.json'),mode],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1'),timeout=30);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
  if expected=='pass':assert p.returncode==0,p.stdout+p.stderr
  elif expected=='asan':assert p.returncode!=0 and 'heap-use-after-free' in p.stderr,p.stdout+p.stderr
  else:assert p.returncode!=0 and ('assertion failed' in p.stderr or 'assertion failed' in p.stdout),p.stdout+p.stderr
  checks.append({'name':name,'mode':mode,'exitCode':p.returncode,'expected':expected,'passed':True})
 report={'passed':True,'checks':checks,'nativeAcceptance':False,'ownershipTrigger':'Synthetic nested shared_commit hook immediately after actual reserve; capture stub replaces surface_eval only. No observed native nested callback or crash claim.','FIFOTransportGate':'OPEN','sourceSHA256':hashlib.sha256((r/'native/shared-host.c').read_bytes()).hexdigest(),'originalSHA256':hashlib.sha256((parent/'native/shared-host.c').read_bytes()).hexdigest(),'packetSHA256':hashlib.sha256(packet.read_bytes()).hexdigest()}
except Exception as e:report={'passed':False,'checks':checks,'error':repr(e),'nativeAcceptance':False}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json');sys.exit(not report['passed'])
