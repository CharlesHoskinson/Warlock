import hashlib,json,pathlib,resource,sys,subprocess,shlex,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];owner=ROOT.parents[1]/'implementation/warlock-family-capture-v2';OUT=ROOT/'qa'/('check-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
paths=[pathlib.Path(__file__),ROOT/'native/family_crop.hpp',ROOT/'native/check.cpp',ROOT/'SPEC.md',owner/'native/preview_png.hpp',owner/'native/preview_uri.hpp'];inputs={str(p):sha(p) for p in paths}
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'qaScope':scope,'inputs':inputs,'scope':'Actual crop geometry/PNG reservation planner only; selected model/native renderer/FD/typed GUI qualification pending'}
try:
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gio-2.0'],text=True));argv=['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','-I'+str(owner/'native'),str(ROOT/'native/check.cpp'),*flags,'-o',str(OUT/'check')];p=subprocess.run(argv,capture_output=True,text=True,timeout=180);(OUT/'compile.stdout').write_text(p.stdout);(OUT/'compile.stderr').write_text(p.stderr);r.update(argv=argv,compileExitCode=p.returncode);assert p.returncode==0,p.stderr
 p=subprocess.run([str(OUT/'check')],capture_output=True,text=True,timeout=5);(OUT/'run.stdout').write_text(p.stdout);(OUT/'run.stderr').write_text(p.stderr);r['exitCode']=p.returncode;assert p.returncode==0,p.stderr;r['evidence']=json.loads(p.stdout);assert r['evidence']['passed'];assert all(sha(p)==h for p,h in inputs.items());r['passed']=True
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};report=OUT/'report.json';report.write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:(ROOT/'qa/check-report.json').write_text(json.dumps({'path':str(report),'sha256':sha(report)},indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(report),'error':r.get('error')}));raise SystemExit(not r['passed'])
