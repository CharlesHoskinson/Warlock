"""Compile actual C/native bridge and couple retained delivery to optimized Elm."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('retirement-native-elm-check-v3-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(root)):sha(p) for p in (root/'native').glob('*') if p.is_file()}
for name in ['qa/retirement-native-elm-roundtrip-v2.js','qa/retirement-native-elm-check-v3.py']:inputs[name]=sha(root/name)
report={'passed':False,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False}
def run(name,args):
    p=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180)
    (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
    report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
    assert p.returncode==0,p.stderr or p.stdout
    return p.stdout
try:
    controls=list(root.glob('qa/retirement-delivery-check-*/report.json'));assert len(controls)==1
    prior=controls[0];proof=json.loads(prior.read_text());assert proof['passed']
    for rel,value in proof['inputs'].items():assert sha(root/rel)==value,rel
    compiled=out/'preview-replay.js';shutil.copy2(prior.parent/'preview-replay.js',compiled)
    report['compiledControls']={'path':str(prior),'sha256':sha(prior),'compiledElmSHA256':sha(compiled)}
    for name in inputs:
        p=out/'inputs'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,p)
    flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
    run('compile',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/retirement-elm-channel-test-v3.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags])
    evidence=json.loads(run('roundtrip',['node','qa/retirement-native-elm-roundtrip-v2.js',str(compiled),str(out/'checks')]))
    assert evidence['passed'] and evidence['normalOwnedExit']
    assert all(sha(root/name)==value for name,value in inputs.items())
    report.update(passed=True,evidence=evidence)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1500]}),flush=True);sys.exit(not report['passed'])
