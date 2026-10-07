"""Compiled unsafe derivatives must fail the unchanged current output oracles."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('output-custody-guards-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bases={'reservation':root/'qa/policy-driver-output-gate-check-1791377264204546838','returned-priority':root/'qa/policy-driver-quarantined-output-check-1791378292903443577'}
reports={k:json.loads((p/'report.json').read_text()) for k,p in bases.items()}
names=sorted(set(n for d in reports.values() for n in d['inputs'])|{'qa/output-custody-guards.py'})
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'compiledNativeVariants':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Two labeled unsafe compiled derivatives remove the pre-effect reservation check or early returned-event priority. The unchanged accepted pressure and late-quarantine Native/C/JSC oracles must reject them. Failed variants are deliberately terminated and never establish normal closure, actual output queue exhaustion, GUI or release acceptance.'}
def run(name,args,cwd,required=True):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for key,base in bases.items():
  d=reports[key];assert d['passed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted']
  for n,h in d['inputs'].items():assert sha(root/n)==h,(key,n)
  for n,h in d['artifacts'].items():assert sha(base/n)==h,(key,n)
 for n in names:
  p=out/'inputs'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/n,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0','javascriptcoregtk-4.1'],out).stdout)
 variants={
 'reservation':('preview-policy-driver-output-gate.cpp','if(!output_room(self->returned_events.size(),self->returned_bytes))','if(false && !output_room(self->returned_events.size(),self->returned_bytes))','policy-driver-output-gate-fixture.cpp','policy-driver-output-gate-roundtrip.js','Original output reservation gate refuses before native effect'),
 'returned-priority':('preview-policy-driver.cpp','if(!self->returned_events.empty()) {\n        g_autoptr(JsonParser) cache','if(false && !self->returned_events.empty()) {\n        g_autoptr(JsonParser) cache','policy-driver-positive-fixture.cpp','policy-driver-quarantined-output-roundtrip.js','Exactly one original admitted offer processed before further effect output')}
 for key,(filename,old,new,fixture,oracle,expected) in variants.items():
  folder=out/key;shutil.copytree(out/'inputs',folder/'inputs');cwd=folder/'inputs';shutil.copy2(bases[key]/'inputs/native/capture-resources.hpp',cwd/'native/capture-resources.hpp')
  source=cwd/'native'/filename;s=source.read_text();assert s.count(old)==1;source.write_text(s.replace(old,new));binary=folder/'driver'
  files=['native/'+fixture]+([] if key=='reservation' else ['native/preview-policy-driver.cpp'])+['native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','native/elm-preview-policy.cpp']
  run('compile-'+key,['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative',*files,'-o',str(binary),*flags],cwd)
  observed=run('guard-'+key,['node',str(cwd/'qa'/oracle),str(binary),str(bases[key]/'policy.js'),str(cwd/'assets/native-preview-control-outbox.js')],folder,False)
  assert observed.returncode!=0 and 'AssertionError' in observed.stderr and expected in observed.stderr,(key,observed.stderr)
  assert (folder/'failed-steps.json').is_file()
  report['compiledNativeVariants'].append({'name':key,'sourceSHA256':sha(source),'detected':True,'expectedAssertion':expected,'normalCloseClaimed':False})
 assert all(sha(root/n)==h for n,h in report['inputs'].items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2200]}),flush=True);sys.exit(not report['passed'])
