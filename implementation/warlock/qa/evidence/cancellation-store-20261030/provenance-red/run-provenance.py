import hashlib,json,pathlib,subprocess,sys,time
D=pathlib.Path(__file__).parent;sys.path.insert(0,'/home/charles/Warlock/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();out=D/('provenance-'+str(time.time_ns()));out.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(D)):sha(p) for p in [*(D/'adapter').glob('*.py'),D/'check-attempt-provenance.py']}
p=subprocess.run([sys.executable,'-B',str(D/'check-attempt-provenance.py'),*sys.argv[1:]],capture_output=True,timeout=30)
(out/'stdout').write_bytes(p.stdout);(out/'stderr').write_bytes(p.stderr)
r={'passed':p.returncode==0,'exitCode':p.returncode,'scope':scope,'arguments':sys.argv[1:],'inputs':inputs};(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(out/'report.json')}));sys.exit(0 if r['passed'] else 1)
