"""Compile and exercise the actual Native/C/socket retirement observation boundary."""
import hashlib, json, pathlib, resource, shlex, shutil, subprocess, sys, time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('retirement-fair-poll-check-'+str(time.time_ns()));out.mkdir()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
inputs={str(path.relative_to(root)):sha(path) for path in (root/'native').glob('*') if path.is_file()}
inputs[str(pathlib.Path(__file__).relative_to(root))]=sha(pathlib.Path(__file__))
report={'passed':False,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,
 'scope':'Actual C/bootstrap/socket/Native/ImportedClients retained readiness. Exact native query counts before physical/terminal-ACK/other-receiver barriers clear, one-candidate polling with blocked first/eligible neighbor, fresh native confirmation, original actor floor, final processing ACK, byte-identical loss retry, close barrier and normal owned cleanup. Synthetic peer; no real compositor destruction or captured resource qualification.'}
def run(name,args,cwd=None):
 result=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(result.stdout);(out/(name+'.stderr')).write_text(result.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':result.returncode});print(name,result.returncode,flush=True)
 assert result.returncode==0,result.stderr or result.stdout
 return result.stdout
try:
 build=next(root.glob('qa/build-*/report.json'));proof=json.loads(build.read_text());assert proof['passed'] and len(proof['commands'])==95
 for name,value in proof['inputs'].items():assert sha(root/name)==value,name
 report['fullBuild']={'path':str(build),'sha256':sha(build)}
 for name in inputs:
  target=out/'inputs'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,target)
 flags=shlex.split(run('gio-flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
 run('compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/retirement-fair-poll-test.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags])
 controls=[json.loads(run('fair-poll',[str(out/'checks')]))];assert controls[0]['passed'] and controls[0]['normalOwnedExit']
 assert all(sha(root/name)==value for name,value in inputs.items())
 report.update(passed=True,controls=controls,checks=sum(row['checks'] for row in controls))
except Exception as error:report['error']=repr(error)
report['artifacts']={str(path.relative_to(out)):sha(path) for path in out.rglob('*') if path.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}),flush=True);sys.exit(not report['passed'])
