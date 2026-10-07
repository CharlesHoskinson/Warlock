"""Actual original Bootstrap receipt detach/reattach through strict C close."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('uri-capability-check-v2-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]+[str(pathlib.Path(__file__).relative_to(root))]
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual controlled C owners and one original Bootstrap reused across two settled realm epochs, its own ReceiptDelivery channels, original synthetic authenticated Native socket/Endpoint/Broker/permanent-incarnation retirement/final processing/independent-confirmation close. Each original refused close retains borrowed delivery. A different actual Native Bootstrap refuses before settled owner mutation. Strict owning close releases receipt before Endpoint destruction; later lookup/poll refuse safely, next original realm attaches new channel on unchanged binding. No live-window detachment/actual Core/WebKit acceptance.'}
def run(name,args,cwd=None,required=True):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']).stdout)
 args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/uri-capability-test.cpp','native/preview-uri-router.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags]
 run('compile',args);e=json.loads(run('actual-scoped-detachment-and-live-subject-reenrollment',[str(out/'checks')]).stdout);assert e['passed'] and e['actualSealedFDs']==4 and e['staleCapabilityRefused'] and e['independentCallbackReference'] and e['actualFDsClosed'] and not e['actualWebKitCallback']
 mutants=[]
 for name,header,old,new,witness in [
  ('ignore-captured-receiver-epoch','native/preview_uri.cpp',' && found->second.epoch==epoch_','', 'Stale native read capability refuses before reader allocation'),
  ('reset-router-frontier-on-clear','native/preview-uri-router.cpp','router->route.reset();return TRUE;','router->route.reset();router->through=0;return TRUE;','Clear refuses old current realm rebind'),
  ('allow-reader-after-endpoint-destruction','native/preview_uri.cpp','const auto lifetime=r.lifetime.lock();if(!lifetime || !lifetime->active)return false;',';','Original reader authority is revoked independently of retained physical storage')]:
  target=out/name;shutil.copytree(out/'inputs',target);p=target/header;s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  changed=[*args];changed[changed.index('-o')+1]=str(target/'checks');run(name+'-compile',changed,target)
  result=run(name+'-witness',[str(target/'checks')],target,False);assert result.returncode==1 and witness in result.stderr.splitlines(),(name,result.stderr)
  mutants.append({'name':name,'compiled':True,'failedOriginalAssertion':witness})
 report.update(unsafeCompiledVariantsDetected=3,mutants=mutants)
 assert all(sha(root/rel)==v for rel,v in report['inputs'].items())
 report.update(passed=True,evidence=e,actualSyntheticNativeActiveFact=False,actualWaylandWindowAcceptance=False,scope='Actual C router/native read capability/Endpoint/Broker/GIO/sealed memfd storage. Exact lifetime/receiver epoch/Native binding/token/source/time guards and creator thread/monotonic router/independent callback reference are exercised. Four real mapped descriptors close. Synthetic direct-native fixture source and PNG signature bytes; no Core server/Wayland window/WebKit callback or frontend activation acceptance.')
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1600]}),flush=True);sys.exit(not report['passed'])
