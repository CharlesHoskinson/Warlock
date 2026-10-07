"""Qualify actual native aggregate retirement with independent quota barriers."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('imported-controlled-c-check-v2-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(root)):sha(p) for p in (root/'native').glob('*') if p.is_file()};inputs[str(pathlib.Path(__file__).relative_to(root))]=sha(pathlib.Path(__file__))
report={'passed':False,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual opt-in controlled C factory, one original native transport namespace, creator thread and receipt Endpoint guards, native issued immutable purpose tickets, actual contiguous C dispatch, exact retries and failed-handler receipts, confirmed predecessor suppression, original actor transaction and independent frontend confirmations.260 actual metadata actors on authenticated synthetic Native socket/C bootstrap/Coordinator/Broker/Endpoint/retirement journal.1041 original uninterrupted tickets; final original receipt and confirmation after actual synthetic core normal exit. No real windows, capture/FD/backend locks/Elm/WebKit/live-window binding detachment or full native release acceptance.'}
def run(name,args):
 p=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
 return p.stdout
try:
 for rel in inputs:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
 run('compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/imported-controlled-c-test-v2.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags])
 result=json.loads(run('native-control-retirement',[str(out/'checks')]));assert result['passed'] and result['normalOwnedExit'] and result['actorsTurnedOver']==260 and result['nativeIssuedPrefix']==1041
 assert all(sha(root/rel)==value for rel,value in inputs.items());report.update(passed=True,controls=[result],checks=result['checks'])
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1400]}),flush=True);sys.exit(not report['passed'])
