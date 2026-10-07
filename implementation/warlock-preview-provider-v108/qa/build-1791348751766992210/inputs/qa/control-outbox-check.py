"""Qualify exact JS/native metadata transport without product activation."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('control-outbox-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]
names+=['assets/retained-preview-controls.js','qa/control-outbox-roundtrip.js','qa/control-outbox-check.py']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False}
def run(name,args):
    p=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180)
    (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
    report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
    assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
    for rel in names:
        p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
    flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
    run('compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/control-outbox-fixture.cpp','-o',str(out/'checks'),*flags])
    evidence=json.loads(run('roundtrip',['node','qa/control-outbox-roundtrip.js','assets/retained-preview-controls.js',str(out/'checks')]))
    assert evidence['passed'] and evidence['normalOwnedExit'] and not evidence['nativeAcceptance'] and not evidence['fullReleaseAccepted']
    assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
    report.update(passed=True,evidence=evidence)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1500]}),flush=True);sys.exit(not report['passed'])
