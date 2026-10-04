import hashlib,json,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('checks-'+str(time.time_ns()));OUT.mkdir();SOURCE=REPO/'implementation/elm-stable-surface-publication-v521';held=REPO/'implementation/elm-captured-surface-publication-replay-v538/qa/replay-1791140601401911296'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((held/'report.json').read_text())['passed']
inputs=OUT/'inputs';shutil.copytree(SOURCE/'native',inputs);shutil.copy2(ROOT/'qa/replay.c',inputs/'replay.c')
report={'passed':False,'nativeAcceptance':False,'pointerRaceCausallyResolved':False,'scope':'Actual production C guards against actual compiled Elm full frames with synthetic engine/physical proof and injected DOM-verification result','checks':[],'replayReportSHA256':sha(held/'report.json')}
try:
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0'],text=True));command=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(OUT/'helper.d'),str(inputs/'replay.c'),'-o',str(OUT/'helper'),*flags];report['compileCommand']=command;p=subprocess.run(command,capture_output=True,timeout=180);(OUT/'compile.stdout').write_bytes(p.stdout);(OUT/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode()[-3000:]
 for number in [507,521]:
  witness=held/str(number)/'witness.json';shutil.copy2(witness,OUT/(str(number)+'.json'));p=subprocess.run([str(OUT/'helper'),str(witness),str(number)],capture_output=True,text=True,timeout=10);(OUT/(str(number)+'.stdout')).write_text(p.stdout);(OUT/(str(number)+'.stderr')).write_text(p.stderr);assert p.returncode==0,p.stderr;result=json.loads(p.stdout);assert result['passed'];report['checks'].append({'source':number,**result,'witnessSHA256':sha(witness)})
 report['passed']=True
except Exception as e:report['error']=repr(e)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
