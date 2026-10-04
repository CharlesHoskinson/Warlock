import hashlib,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('test-'+str(time.time_ns()));OUT.mkdir();report={'passed':False,'nativeAcceptance':False,'fullAcceptance':False,'authenticatedTransportImplemented':False};sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
try:
 elm=shutil.which('elm');node=shutil.which('node');assert elm and node
 (OUT/'inputs/src').mkdir(parents=True)
 for p in (ROOT/'src').glob('*.elm'):shutil.copyfile(p,OUT/'inputs/src'/p.name)
 shutil.copyfile(ROOT/'elm.json',OUT/'inputs/elm.json');cmd=[elm,'make','src/Replay.elm','--output='+str(OUT/'replay.js')];r=subprocess.run(cmd,cwd=OUT/'inputs',stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60);(OUT/'compile.stdout').write_bytes(r.stdout);(OUT/'compile.stderr').write_bytes(r.stderr);assert r.returncode==0
 runner=OUT/'run.cjs';runner.write_text("const {Elm}=require('./replay.js');Elm.Replay.init().ports.report.subscribe(rows=>{process.stdout.write(JSON.stringify(rows)+'\\n');process.exit(rows.every(x=>x.passed)?0:1)});setTimeout(()=>process.exit(2),2000);\n")
 r=subprocess.run([node,str(runner)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=3);(OUT/'stdout').write_bytes(r.stdout);(OUT/'stderr').write_bytes(r.stderr);assert r.returncode==0
 checks=json.loads(r.stdout);assert len(checks)>=35 and all(row['passed'] is True for row in checks)
 report.update(passed=True,checks=checks,compileCommand=cmd,sourceInputs={str(p):sha(p) for p in (ROOT/'src').glob('*.elm')},tools={str(Path(p).resolve()):sha(p) for p in [elm,node]},binarySHA256=sha(OUT/'replay.js'))
finally:
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json')}))
