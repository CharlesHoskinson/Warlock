import copy,hashlib,json,os,pathlib,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
root=pathlib.Path(__file__).resolve().parents[1];base=root.parent
parent=base/'elm-batch-cache-ownership-v730';store=base/'elm-recovery-delivery-integrated-gui-v640'
out=root/'qa'/('producer-candidate-'+str(time.time_ns()));out.mkdir();checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,args,expected=0):
 p=subprocess.run(args,cwd=out,capture_output=True,text=True,timeout=30)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 checks.append({'name':name,'args':args,'exitCode':p.returncode});assert p.returncode==expected,p.stdout+p.stderr
 return p
def check(name,condition):
 checks.append({'name':name,'passed':bool(condition)});assert condition,name
try:
 manifest=parent/'component-manifest.json';assert sha(manifest)=='896fef834db35af5137d4e0b676635b04407be894fdd0d44da7309cc2a65daae'
 inventory=json.loads(manifest.read_text())['files'];held={}
 for p in (parent/'native').iterdir():
  if not p.is_file():continue
  expected=inventory[str(p.relative_to(parent))];assert sha(p)==(expected['sha256'] if isinstance(expected,dict) else expected)
  held[str(p.relative_to(parent))]={'source':str(p),'sha256':sha(p)}
 original=(base/'elm-native-script-loading-diagnostic-v786'/'native/host.c').read_text()
 branch='if (open && !popup_open()) return SURFACE_UNCERTAIN;'
 revised='/* Preflight excludes all effects/launches while open. No request from this\n     * original invocation has entered the backend queue at this boundary. */\n    if (open && !popup_open()) return SURFACE_PREFLIGHT_UNSENT;'
 assert original.count(branch)==1 and (root/'native/host.c').read_text()==original.replace(branch,revised)
 assert (root/'native/shared-host.c').read_bytes()==(base/'elm-catalog-negative-experiment-v778'/'native/shared-host.c').read_bytes()
 for p in (root/'native').iterdir():
  if p.is_file():held['candidate-native/'+p.name]={'source':str(p),'sha256':sha(p)}
 shutil.copytree(root/'native',out/'native');shutil.copytree(store/'adapter',out/'adapter');(out/'qa').mkdir();shutil.copy2(root/'qa/admission-probe.c',out/'qa/admission-probe.c')
 for p in sorted((store/'adapter').rglob('*')):
  if p.is_file():held['adapter/'+str(p.relative_to(store/'adapter'))]={'source':str(p),'sha256':sha(p)}
 effect=parent/'qa/negative-1791166635235653455/checks.json';expected=inventory[str(effect.relative_to(parent))];assert sha(effect)==(expected['sha256'] if isinstance(expected,dict) else expected)
 shutil.copy2(effect,out/'effect-controls.json')
 source=(out/'native/host.c').read_text()
 old='''static void deliver(const char *text) {
    if (shutting_down) return;
    g_autofree char *script=g_strdup_printf("window.receiveNative(%s);",text);
    webkit_web_view_evaluate_javascript(view,script,-1,NULL,"elm-shell://app/adapter.js",NULL,evaluate_done,NULL);
}'''
 new='''static guint qa_delivery_count;static char *qa_delivery;
static void deliver(const char *text) {
    qa_delivery_count++;g_free(qa_delivery);qa_delivery=g_strdup(text);
}'''
 assert source.count(old)==1;(out/'native/host.c').write_text(source.replace(old,new))
 (out/'held-source.json').write_text(json.dumps(held,indent=2)+'\n')
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']).stdout)
 run('compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','qa/admission-probe.c','-o',str(out/'probe'),*flags])
 sys.path.insert(0,str(out/'adapter'));from recovery_store import RecoveryStore
 from endpoint import Refused
 data=json.loads(effect.read_text());request=data['pending']['submitted']['requests'][0]
 bound=request['binding'];lifetime=bound['lifetime'];now=copy.deepcopy(bound);now['frontend']=str(int(now['frontend'])+1)
 wanted={'schema':2,'effectProtocol':request['effectProtocol'],'binding':copy.deepcopy(bound),'intent':copy.deepcopy(request['intent']),'status':'Unknown'}
 validation=['invalid-intent','foreign-binding','multiple-effects'];faults=validation+['partial-write','file-fsync','rename','directory-fsync','directory-fsync-after','partial-write-cleanup','crash-after-rename']
 states={}
 for mode in faults:
  runtime=out/('runtime-'+mode);runtime.mkdir(mode=0o700);config=runtime/'config.json';config.write_text(json.dumps({'runtime':str(runtime),'instance':'Test'}));config.chmod(0o600)
  p=run(mode,[str(out/'probe'),str(out/'effect-controls.json'),str(config),mode],73 if mode=='crash-after-rename' else 0)
  namespace=runtime/'elm-window-recovery'/'Test'/lifetime/'admissions-v1';files=sorted(namespace.iterdir());before={f.name:{'sha256':sha(f),'bytes':f.read_text(),'mode':oct(f.stat().st_mode&0o777)} for f in files}
  check(mode+' no durable acknowledgement','host-intent-durable:' not in p.stdout)
  renamed=mode in ['directory-fsync','directory-fsync-after','crash-after-rename']
  check(mode+' visible final admission exactly matches interruption point',len([f for f in files if len(f.name)==69 and f.name.endswith('.json')])==int(renamed))
  if mode=='partial-write-cleanup':check('cleanup failure preserves actual partial temp evidence',len(files)==1 and files[0].name.startswith('host-pending-') and len(files[0].read_bytes())==7)
  with RecoveryStore(str(runtime),'Test',lifetime) as ledger:
   snapshot=ledger.ledger.synchronization_snapshot();check(mode+' existing store preserves only exact anchored Unknown',snapshot['entries']==([wanted] if renamed else []))
   frames=ledger.recovery_frames(now);unknown=[f['record'] for f in frames if f['kind']=='host-reservation-unknown'];check(mode+' no fabricated or lost Unknown',unknown==([wanted] if renamed else []))
   check(mode+' no inferred release',snapshot['releases']==[])
   if renamed:check(mode+' exact target remains reserved',ledger.ledger.blocked(lifetime,wanted['intent']['incarnation']))
   states[mode]={'beforeReopen':before,'snapshot':snapshot,'frames':frames}
  with RecoveryStore(str(runtime),'Test',lifetime) as ledger:
   check(mode+' repeated reopen conserves Unknown',ledger.ledger.synchronization_snapshot()['entries']==([wanted] if renamed else []))
 (out/'states.json').write_text(json.dumps(states,indent=2)+'\n')
 report={'passed':True,'checks':checks,'nativeAcceptance':False,'scope':'Actual candidate778 C surface_receive and admission producer; GUI deliver captured; real isolated filesystem/syscall before/after injected failures, real owned subprocess cancellation/termination, unchanged copied640 RecoveryStore reopen. Process interruption is not power-loss durability or native authentication.'}
except Exception as error:report={'passed':False,'checks':checks,'error':repr(error),'nativeAcceptance':False}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json');sys.exit(not report['passed'])
