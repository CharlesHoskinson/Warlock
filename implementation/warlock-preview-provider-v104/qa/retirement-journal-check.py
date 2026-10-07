"""Actual bounded native completion journal and retained ancestor zero-floor failure."""
import hashlib,json,pathlib,resource,shlex,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('retirement-journal-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'actorTurnoverAccepted':False,'fullReleaseAccepted':False,'inputs':{},'commands':[],
 'scope':'Actual C++ native transport journal: synthetic exact observations/final facts, bounded retained delivery, readiness correlation and original epoch. No physical proof generation, original Broker/Elm coupling, WebKit delivery or native actor-turnover acceptance.'}
def run(name,args,expected=0):
 p=subprocess.run(args,capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==expected,p.stderr or p.stdout
 return p
try:
 ancestor=root.parent/'warlock-preview-provider-v89';held=json.loads((ancestor/'component-manifest.json').read_text());assert held['passed'] and held['sourceHeld']
 for p in [*root.joinpath('native').glob('*.hpp'),root/'qa/retirement-journal-checks.cpp',pathlib.Path(__file__),ancestor/'native/preview_retirement.hpp']:
  report['inputs'][str(p)]=sha(p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']).stdout)
 base=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer']
 run('ancestor-compile',[*base,'-DANCESTOR_FLOOR','-I'+str(ancestor/'native'),str(root/'qa/retirement-journal-checks.cpp'),'-o',str(out/'ancestor-check'),*flags])
 failed=run('ancestor-zero-floor',[str(out/'ancestor-check')],1);assert failed.stderr.strip()=='Positive wire identity'
 report['retainedAncestorZeroFloorFailure']={'source':str(ancestor/'native/preview_retirement.hpp'),'sha256':sha(ancestor/'native/preview_retirement.hpp'),'reason':failed.stderr.strip()}
 run('compile',[*base,'-I'+str(root/'native'),str(root/'qa/retirement-journal-checks.cpp'),'-o',str(out/'checks'),*flags])
 report['evidence']=json.loads(run('controls',[str(out/'checks')]).stdout);assert report['evidence']['passed'] and report['evidence']['sequentialCompletions']==280
 assert all(sha(pathlib.Path(p))==h for p,h in report['inputs'].items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1000]}),flush=True);sys.exit(not report['passed'])
