from pathlib import Path
import hashlib,json,os,subprocess,sys
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent));from qa_launch import require_qa_scope
scope=require_qa_scope();command=['/usr/bin/python3','-B','-m','unittest','discover','-s',str(B),'-p','test*.py','-v'];result=subprocess.run(command,capture_output=True,text=True,timeout=30)
assert result.returncode==0 and 'Ran 12 tests' in result.stderr and 'skipped' not in result.stderr,result.stderr
sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in B.iterdir() if p.is_file() and p.name!='offline-checkpoint.json'}
fd=os.open(B/'offline-checkpoint.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
with os.fdopen(fd,'w') as stream:json.dump(dict(result='pass',scope=scope,command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,tests=12,sources=sources,nativeCommands=False,mainWrites=False,producerImports=False,fullHeld52Accepted=False),stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
print(json.dumps(dict(result='pass',tests=12,nativeCommands=False)))
