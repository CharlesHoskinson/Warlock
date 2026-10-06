"""Compile the actual shared importer witness from the protected provider build."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('build-'+str(time.time_ns()));OUT.mkdir();sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r={'passed':False,'scope':scope,'nativeAcceptance':False,'fullReleaseAccepted':False,'commands':[]}
def run(name,cmd):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=120,cwd=OUT);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'argv':cmd,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr;return p.stdout
try:
 provider=REPO/'implementation/warlock-preview-provider-v24';reports=list(provider.glob('qa/build-*/report.json'));assert len(reports)==1;built=json.loads(reports[0].read_text());assert built['passed']
 inputs={str(reports[0]):sha(reports[0])}
 for rel,h in built['inputs'].items():
  assert sha(provider/rel)==h
  if rel.startswith('native/'):inputs[str(provider/rel)]=h
 for p in [ROOT/'native/witness.cpp',ROOT/'SPEC.md',ROOT/'ANCESTRY.json',pathlib.Path(__file__).resolve()]:inputs[str(p)]=sha(p)
 r['inputs']=inputs;shutil.copytree(provider/'native',OUT/'native');shutil.copy2(ROOT/'native/witness.cpp',OUT/'witness.cpp')
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','json-glib-1.0','gio-unix-2.0']))
 binary=OUT/'witness';run('compile',['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','-I'+str(OUT/'native'),'-MD','-MF',str(OUT/'witness.d'),str(OUT/'witness.cpp'),str(OUT/'native/preview_uri.cpp'),str(OUT/'native/preview-provider-bootstrap.cpp'),str(OUT/'native/imported-clients.cpp'),'-o',str(binary),*flags])
 r.update(binary=str(binary),binarySHA256=sha(binary));assert all(sha(p)==h for p,h in inputs.items());r['passed']=True
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
