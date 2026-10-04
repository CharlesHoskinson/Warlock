import hashlib,json,resource,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=Path(__file__).resolve().parents[1];repo=root.parents[1]
current=repo/'implementation/elm-focus-recovery-integrated-gui-v333/assets/context.js';before=repo/'implementation/elm-responsive-confirmation-gui-v301/assets/context.js'
out=root/'qa'/('checks-'+str(time.time_ns()));out.mkdir()
paths=[current,before,root/'SPEC.md',root/'qa/probe.cjs',Path(__file__).resolve()]
inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
result=subprocess.run(['node',str(root/'qa/probe.cjs'),str(current),str(before)],capture_output=True,text=True,timeout=20)
(out/'stdout.json').write_text(result.stdout);(out/'stderr').write_text(result.stderr)
report={'passed':False,'nativeAcceptance':False,'scope':'Declared inert DOM adapter controls only','inputs':inputs,'exitCode':result.returncode}
try:
 data=json.loads(result.stdout);report.update(data);assert result.returncode==0 and report['passed']
 for p,d in inputs.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==d
except Exception as e:report.update(passed=False,error=repr(e))
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json')}));raise SystemExit(not report['passed'])
