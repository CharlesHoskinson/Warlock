import hashlib,json,pathlib,resource,shlex,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('check-'+str(time.time_ns()));OUT.mkdir()
flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','hyprutils'],text=True));cmd=['g++','-std=c++23',str(ROOT/'qa/projection.cpp'),'-o',str(OUT/'projection'),*flags];p=subprocess.run(cmd,capture_output=True,text=True);(OUT/'compile.stderr').write_text(p.stderr);r={'passed':False,'argv':cmd,'compileExitCode':p.returncode,'nativeAcceptance':False}
if not p.returncode:
 p=subprocess.run([str(OUT/'projection')],capture_output=True,text=True);(OUT/'projection.stdout').write_text(p.stdout);r.update(exitCode=p.returncode,matrix=json.loads(p.stdout),passed=p.returncode==0)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));raise SystemExit(not r['passed'])
