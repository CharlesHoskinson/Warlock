import hashlib,json,os,pathlib,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope()
from toolchain import verify
r=pathlib.Path(__file__).resolve().parents[1];out=r/'qa'/('negative-'+str(time.time_ns()));out.mkdir();checks=[]
def run(name,args,cwd=None):
 p=subprocess.run(args,cwd=cwd or out/'inputs',env=dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')),capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);checks.append({'name':name,'args':args,'exitCode':p.returncode});assert p.returncode==0,p.stdout+p.stderr;return p.stdout
try:
 tc=verify();shutil.copytree(r/tc['elmHome'],out/'mutable-elm-home');shutil.copytree(r/'src',out/'inputs/src');shutil.copytree(r/'native',out/'inputs/native');shutil.copy2(r/'elm.json',out/'inputs/elm.json');(out/'inputs/qa').mkdir();shutil.copy2(r/'qa/negative-probe.c',out/'inputs/qa/negative-probe.c');shutil.copy2(r/'qa/negative.cjs',out/'inputs/qa/negative.cjs');shutil.copy2(r/'qa/negative.py',out/'inputs/qa/negative.py')
 held={str(p.relative_to(out/'inputs')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (out/'inputs').rglob('*') if p.is_file()};(out/'source-before.json').write_text(json.dumps(held,indent=2)+'\n')
 source=(r/'native/shared-host.c').read_text();needle='#include "host.c"';assert source.count(needle)==1
 instrumentation='#define surface_eval inherited_surface_eval\n#include "../native/host.c"\n#undef surface_eval\nstatic JsonNode *captured_packet;\nstatic guint captured_count;\nstatic void surface_eval(WebKitWebView *target,const char *function,JsonNode *packet){(void)target;if(g_str_equal(function,"receiveBatchDisposition")){captured_count++;if(captured_packet)json_node_unref(captured_packet);captured_packet=json_node_copy(packet);}}\n'
 (out/'inputs/qa/instrumented-shared-host.c').write_text(source.replace(needle,instrumentation).replace('#include "context-keys.h"','#include "../native/context-keys.h"').replace('#include "shared-context.h"','#include "../native/shared-context.h"'))
 run('elm',[str(r/tc['compiler']),'make','src/BatchReplay.elm','--optimize','--output='+str(out/'worker.js')])
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']))
 run('probe-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(out/'probe.d'),'qa/negative-probe.c','-o',str(out/'probe'),*flags])
 run('controls',['node',str(out/'inputs/qa/negative.cjs'),str(out/'worker.js'),str(r.parent/'elm-topology-batch-channel-model-v709/qa/ready-events.json'),str(out/'packet.json'),str(out/'probe'),str(out/'checks.json'),str(r.parent/'elm-topology-batch-channel-model-v709/qa/original-1791163383225147012/worker.js')]);verify()
 report={'passed':True,'checks':checks,'nativeAcceptance':False,'qualification':False,'FIFOTransportGate':'OPEN','heldSource':held,'result':str(out/'checks.json'),'instrumentation':'Exact shared-host source with only delivery capture stub and includes relocated; inherited host.c unchanged'}
except Exception as e:report={'passed':False,'checks':checks,'error':repr(e),'nativeAcceptance':False}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json');sys.exit(not report['passed'])
