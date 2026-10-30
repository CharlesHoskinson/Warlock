import hashlib,json,pathlib,subprocess,sys,time
D=pathlib.Path(__file__).parent;sys.path.insert(0,'/home/charles/Warlock/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();out=D/('restart-'+str(time.time_ns()));out.mkdir()
p=subprocess.run([sys.executable,'-B',str(D/'check-restart.py'),*sys.argv[1:]],capture_output=True,timeout=30)
(out/'stdout').write_bytes(p.stdout);(out/'stderr').write_bytes(p.stderr)
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
r={'passed':p.returncode==0,'exitCode':p.returncode,'scope':scope,'arguments':sys.argv[1:],'inputs':{str(q.relative_to(D)):sha(q) for q in [D/'check-restart.py',*(D/'adapter').glob('*.py')]}}
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(out/'report.json')}));sys.exit(0 if r['passed'] else 1)
