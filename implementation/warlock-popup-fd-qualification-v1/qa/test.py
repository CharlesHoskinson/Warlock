import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];owner=REPO/'implementation/warlock-popup-capture-v1'
OUT=ROOT/'qa'/('test-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
paths=[pathlib.Path(__file__),ROOT/'SPEC.md',ROOT/'native/qualify.cpp',*owner.joinpath('native').glob('*.hpp'),owner/'native-build-report.json']
inputs={str(p):sha(p) for p in paths}
for p in paths:shutil.copy2(p,OUT/p.name)
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'qaScope':scope,'inputs':inputs,'scope':'Actual new typed FD decoder and sealed memfd/mmap physical ownership; synthetic CPU PNG, native renderer and GUI separate.'}
try:
 descriptor=json.loads((owner/'native-build-report.json').read_text());assert descriptor['result']=='pass' and sha(descriptor['plugin']['path'])==descriptor['plugin']['sha256']
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gio-2.0'],text=True));argv=['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','-I'+str(OUT),str(OUT/'qualify.cpp'),*flags,'-MD','-MF',str(OUT/'qualify.d'),'-o',str(OUT/'qualify')]
 p=subprocess.run(argv,capture_output=True,text=True,timeout=180);(OUT/'compile.stdout').write_text(p.stdout);(OUT/'compile.stderr').write_text(p.stderr);r.update(argv=argv,compileExitCode=p.returncode);assert p.returncode==0,p.stderr
 p=subprocess.run([str(OUT/'qualify')],capture_output=True,text=True,timeout=5);(OUT/'run.stdout').write_text(p.stdout);(OUT/'run.stderr').write_text(p.stderr);r['exitCode']=p.returncode;assert p.returncode==0,p.stderr
 evidence=json.loads(p.stdout);assert evidence['passed'] and evidence['physicalFDClosed'] and evidence['physicalMappingClosed'] and evidence['chargeReleasedAfterClose']
 assert all(sha(p)==h for p,h in inputs.items());r.update(passed=True,evidence=evidence)
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};report=OUT/'report.json';report.write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:(ROOT/'qa/test-report.json').write_text(json.dumps({'path':str(report),'sha256':sha(report)},indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(report),'error':r.get('error')}),flush=True);raise SystemExit(not r['passed'])
