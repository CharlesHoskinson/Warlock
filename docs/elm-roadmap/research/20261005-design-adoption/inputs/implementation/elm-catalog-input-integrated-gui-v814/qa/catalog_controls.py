import hashlib,json,os,pathlib,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
from toolchain import verify
root=pathlib.Path(__file__).resolve().parents[1];base=root.parent
out=root/'qa'/('catalog-controls-'+str(time.time_ns()));out.mkdir();checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,args,cwd=None):
 p=subprocess.run(args,cwd=cwd or out/'inputs',env=dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')),capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 checks.append({'name':name,'args':args,'exitCode':p.returncode});assert p.returncode==0,p.stdout+p.stderr
 return p.stdout
try:
 tc=verify();shutil.copytree(root/tc['elmHome'],out/'mutable-elm-home');shutil.copytree(root/'src',out/'inputs/src');shutil.copytree(root/'native',out/'inputs/native');shutil.copy2(root/'elm.json',out/'inputs/elm.json');(out/'inputs/qa').mkdir()
 for name in ['catalog-probe.c','catalog-controls.cjs','catalog_controls.py']:shutil.copy2(root/'qa'/name,out/'inputs/qa'/name)
 held={str(p.relative_to(out/'inputs')):{'sha256':sha(p),'size':p.stat().st_size} for p in (out/'inputs').rglob('*') if p.is_file()};(out/'held-source.json').write_text(json.dumps(held,indent=2)+'\n')
 run('elm',[str(root/tc['compiler']),'make','src/BatchReplay.elm','--optimize','--output='+str(out/'worker.js')])
 source=(out/'inputs/native/host.c').read_text();old='''static void surface_eval(WebKitWebView *target,const char *function,JsonNode *value) {
    g_autofree char *wire=json_to_string(value,FALSE);
    g_autofree char *script=g_strdup_printf("window.%s(%s);",function,wire);
    webkit_web_view_evaluate_javascript(target,script,-1,NULL,NULL,NULL,evaluate_done,NULL);
}'''
 new='''static JsonNode *qa_capture;static guint qa_capture_count;
static void surface_eval(WebKitWebView *target,const char *function,JsonNode *value) {
    (void)target;if(!g_str_equal(function,"receiveBatchDisposition"))return;
    qa_capture_count++;if(qa_capture)json_node_unref(qa_capture);qa_capture=json_node_copy(value);
}'''
 assert source.count(old)==1;(out/'inputs/native/host.c').write_text(source.replace(old,new));shutil.copy2(out/'inputs/native/host.c',out/'instrumented-host.c')
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']))
 run('c-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(out/'probe.d'),'qa/catalog-probe.c','-o',str(out/'probe'),*flags])
 parent=base/'elm-batch-cache-ownership-v730';baseline=parent/'qa/negative-1791166635235653455/worker.js';effect=parent/'qa/negative-1791166635235653455/checks.json';ready=base/'elm-topology-batch-channel-model-v709/qa/ready-events.json'
 for name,p in [('baseline-worker.js',baseline),('effect-controls.json',effect),('ready-events.json',ready)]:shutil.copy2(p,out/name)
 run('controls',['node',str(out/'inputs/qa/catalog-controls.cjs'),str(out/'worker.js'),str(out/'ready-events.json'),str(out/'baseline-worker.js'),str(out/'probe'),str(out/'effect-controls.json'),str(out/'packet.json'),str(out/'controls.json')])
 run('open-effect-control',[str(out/'probe'),str(out/'packet.json'),'open-effect'])
 verify();report={'passed':True,'checks':checks,'heldSource':held,'nativeAcceptance':False,'scope':'Compiled actual original/candidate Elm and owning C; ONLY GUI delivery capture, controlled NULL-monitor output; no native/auth/deadline or full GUI acceptance'}
except Exception as error:report={'passed':False,'checks':checks,'error':repr(error),'nativeAcceptance':False}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json');sys.exit(not report['passed'])
