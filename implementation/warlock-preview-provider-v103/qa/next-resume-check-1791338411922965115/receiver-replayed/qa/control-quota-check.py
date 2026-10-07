"""Compile the actual presenter with pinned Elm, then execute retained controls."""
import hashlib,json,os,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'qa'/('control-quota-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
from toolchain import verify
toolchain=verify()
paths=[root/'elm.json',root/'qa/control-quota-check.py',root/'qa/control-quota-roundtrip.js',root/'qa/native-source-fixture.json',*sorted((root/'src').glob('*.elm')),*[p for p in (root/'native').glob('*') if p.is_file()]]
report={'passed':False,'inputs':{str(p.relative_to(root)):sha(p) for p in paths},'commands':[],'elmToolchain':toolchain,'nativeAcceptance':False,'fullReleaseAccepted':False}
def run(name,args):
    verify();p=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180,env=dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')));verify()
    (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
    report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode})
    print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout
    return p.stdout
try:
    for p in paths:
        t=out/'inputs'/p.relative_to(root);t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t)
    shutil.copytree(root/toolchain['elmHome'],out/'mutable-elm-home')
    run('compile',[str(root/toolchain['compiler']),'make','src/PreviewPresenterReplay.elm','--optimize','--output='+str(out/'preview-replay.js')])
    flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
    run('native-compile',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/control-quota-fixture.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags])
    evidence=json.loads(run('controls',['node','qa/control-quota-roundtrip.js',str(out/'preview-replay.js'),str(out/'checks')]))
    assert evidence['passed'] and evidence['normalOwnedExit']
    for name,value in report['inputs'].items():assert sha(root/name)==value,name
    report.update(passed=True,evidence=evidence)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'mutable-elm-home' not in p.parts}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1500]}),flush=True)
sys.exit(not report['passed'])
