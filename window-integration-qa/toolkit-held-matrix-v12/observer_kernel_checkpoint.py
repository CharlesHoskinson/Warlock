"""Retain real owned CPU/kernel traces without desktop launch or stream redirection."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
from test_delegate_diagnostics import WRAPPER
B=Path(__file__).resolve().parent

def main():
 scope=require_qa_scope();root=B/'observer-kernel-proof';root.mkdir(mode=0o700);records=[]
 scenarios=[('inherited-streams',"import os;os.write(1,b'actual stdout\\x00bytes');os.write(2,b'actual stderr\\n')",False,False),('shebang-chain',"import os,sys;assert sys.argv[1:]==['list','--json'];os.write(1,b'actual query\\n')",False,True),('actual-epipe',"import os;\ntry:os.write(1,b'actual offered JSON\\n')\nexcept OSError as e:os.write(2,('actual errno='+str(e.errno)+'\\n').encode());os._exit(120)",True,False),('genuine-signal',"import os,signal;os.kill(os.getpid(),signal.SIGTERM)",False,False),('unknown-stop-refusal',"import os,signal;signal.signal(signal.SIGTRAP,lambda *a:os.write(1,b'original trap handler\\n'));os.kill(os.getpid(),signal.SIGTRAP)",False,False)]
 for name,script,closed,shebang in scenarios:
  path=root/name;path.mkdir(mode=0o700);command=['/usr/bin/python3','-IS','-c',WRAPPER,str(B),str(path),script]+(['shebang'] if shebang else [])
  child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  if closed:child.stdout.close();stdout=None;stderr=child.stderr.read();child.wait(timeout=10);child.stderr.close()
  else:stdout,stderr=child.communicate(timeout=10)
  summary=json.loads((path/'summary.json').read_text());rows=[json.loads(line) for line in (path/'trace.jsonl').read_text().splitlines()]
  expected={'inherited-streams':(0,True),'shebang-chain':(0,True),'actual-epipe':(120,True),'genuine-signal':(-15,True),'unknown-stop-refusal':(0,False)}[name]
  okay=child.returncode==0 and (summary['summary']['exitCode'],summary['summary']['complete'])==expected
  if name=='actual-epipe':okay=okay and stderr==b'actual errno=32\n' and any(r['event']=='stdio-write-return' and r['fd']==1 and r['kernelReturn']==-32 and r['errno']==32 for r in rows)
  for p in path.iterdir():
   if p.is_file():p.chmod(0o600 if p.name!='actual-backend' else 0o700)
  records.append(dict(name=name,command=command,wrapperExit=child.returncode,stdoutHex=stdout.hex() if stdout is not None else None,stderrHex=stderr.hex(),passed=okay,traceSHA256=hashlib.sha256((path/'trace.jsonl').read_bytes()).hexdigest(),summarySHA256=hashlib.sha256((path/'summary.json').read_bytes()).hexdigest(),originalDelegateExit=summary['summary']['exitCode'],observerComplete=summary['summary']['complete']))
 result=dict(result='pass' if all(r['passed'] for r in records) else 'fail',scope=scope,records=records,noDesktopLaunch=True,actualKernelEvidence=True,timingAcceptance=False,sourceSHA256=hashlib.sha256((B/'delegate_diagnostics.py').read_bytes()).hexdigest(),fixtureSHA256=hashlib.sha256((B/'test_delegate_diagnostics.py').read_bytes()).hexdigest())
 path=B/'observer-kernel-checkpoint.json'
 with path.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
 path.chmod(0o600);print(json.dumps(dict(result=result['result'],kernelScenarios=len(records),noDesktopLaunch=True)));return int(result['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
