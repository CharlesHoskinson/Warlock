"""Actual all-native aggregate retirement/C/socket ownership tests, CPU scope only."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('actor-retirement-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(root)):sha(p) for p in (root/'native').glob('*') if p.is_file()}
inputs[str(pathlib.Path(__file__).relative_to(root))]=sha(pathlib.Path(__file__))
report={'passed':False,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'actorTurnoverAccepted':False,
'scope':'Actual compiled C/bootstrap/Native/ImportedClients/registry/URI/demand/Broker/ReceiptDelivery exercised against a synthetic own peer-authenticated server. Real reservation, terminal producer proof and exact journal ACK required before all native actor owners disappear. Sequential synthetic subjects greater than256 and retained live neighbor are CPU qualification, not compositor destruction/Elm settlement/pixel/native release acceptance.'}
def run(name,args):
 p=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
 return p.stdout
try:
 for name in inputs:
  p=out/'inputs'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
 run('compile',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/actor-retirement-test.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags])
 evidence=[json.loads(run(mode,[str(out/'checks'),mode])) for mode in ['short','turnover']]
 assert all(p['passed'] and not p['nativeAcceptance'] for p in evidence)
 assert evidence[1]['sequentialSubjects']>256
 assert all(sha(root/name)==value for name,value in inputs.items())
 report.update(passed=True,evidence=evidence,checks=sum(p['checks'] for p in evidence))
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}),flush=True);sys.exit(not report['passed'])
