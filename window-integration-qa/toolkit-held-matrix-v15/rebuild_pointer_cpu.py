"""Compile unchanged producer; execute only its standalone CPU parser fixture."""
from pathlib import Path
import subprocess,json,hashlib,os
B=Path(__file__).resolve().parent/'native-pointer-wheel'
old=json.loads((B/'retained-v13-build-report.json').read_text());records=[]
for cmd in [['/usr/bin/gcc','-std=c11','-Wall','-Wextra','-Werror','-O2','native-pointer.c','virtual-pointer-protocol.c','-lm','-lwayland-client','-o','native-pointer'],['/usr/bin/gcc','-std=c11','-Wall','-Wextra','-Werror','-O2','test-wheel-command.c','-o','test-wheel-command'],[str(B/'test-wheel-command')]]:
 p=subprocess.run(cmd,cwd=B,capture_output=True,text=True,timeout=120);records.append(dict(command=cmd,cwd=str(B),exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr))
 if p.returncode:raise RuntimeError(records[-1])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(B/'native-pointer')=='a68b51faa21c768cee50f973c62b6691e135d7778e36c3cfdfcb0203aa4f6b7a'
old['commands']+=records
for p in B.iterdir():
 if p.is_file() and p.name!='build-report.json':old['inputs'][str(p)]=sha(p);old['inputModes'][str(p)]=p.stat().st_mode&0o7777
old['producer']=str(B/'native-pointer');old['producerSHA256']=sha(B/'native-pointer');old['nativeLaunch']=False;old['nativeInput']=False
fd=os.open(B/'build-report.json',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w')as out:json.dump(old,out,indent=2);out.write('\n')
print('PASS unchanged producer SHA +16 actual standalone CPU cases; no native input')
