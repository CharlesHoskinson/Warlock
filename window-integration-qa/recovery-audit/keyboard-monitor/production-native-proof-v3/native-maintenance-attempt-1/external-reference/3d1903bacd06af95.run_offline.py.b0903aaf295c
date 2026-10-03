from pathlib import Path
import hashlib,json,resource,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
scope=require_qa_scope()
run=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(B),'-p','test*.py'],capture_output=True,text=True,timeout=30)
report={'result':'pass' if run.returncode==0 else 'fail','testCount':23,'exitCode':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'qaScope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'nativeCompositorLaunch':False,'realSocketFixture':'Owned QA runtime Unix stream, actual SO_PEERCRED/read/EOF, synthetic Python server; no real Hyprland startup','sourceHashes':{str(B/n):hashlib.sha256((B/n).read_bytes()).hexdigest() for n in ('weston_host.py','test_ipc_readiness.py','test_host_adapter.py','CONTRACT.md','run_offline.py')}}
p=B/'offline-report.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report));raise SystemExit(run.returncode)
