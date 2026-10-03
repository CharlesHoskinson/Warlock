"""Source-stable complete CPU/formal/parser/closure gate; no GUI/native launch."""
from pathlib import Path
import hashlib,json,os,subprocess
import helper_observer as observer
B=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[p for p in B.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.suffix in ('.py','.qnt','.qml','.c','.h')]
before={str(p):dict(sha256=sha(p),mode=p.stat().st_mode&0o7777)for p in files}
child=subprocess.Popen(['/usr/bin/python3',str(B/'offline_review.py')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
identity=observer.process(child.pid);stdout,stderr=child.communicate(timeout=1800)
changes=[n for n,w in before.items()if sha(Path(n))!=w['sha256']or Path(n).stat().st_mode&0o7777!=w['mode']]
row=dict(result='pass'if child.returncode==0 and not changes else 'fail',exitCode=child.returncode,stdout=stdout,stderr=stderr,processIdentity=identity,actualChildGone=not observer.still_live(identity),sourceWitnesses=before,changedSources=changes,nativeLaunch=False,nativeLoaded=False)
fd=os.open(B/'final-offline-source-stable-v2.json',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps({k:v for k,v in row.items()if k!='sourceWitnesses'}));raise SystemExit(row['result']!='pass')
