"""Actual Snap-style subprocess behavior; observes only the original gated CPU child."""
from pathlib import Path
import hashlib,json,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
from test_delegate_diagnostics import WRAPPER
B=Path(__file__).resolve().parent

def main():
 scope=require_qa_scope();path=B/'observer-kernel-proof/snap-style-descendant';path.mkdir(mode=0o700)
 script="import os,subprocess;raw=subprocess.check_output(['/usr/bin/python3','-IS','-c',\"import os;os.write(1,b'actual child query\\\\n')\"],timeout=4);os.write(1,raw);os.write(2,b'original backend stderr\\n')"
 cmd=['/usr/bin/python3','-IS','-c',WRAPPER,str(B),str(path),script];child=subprocess.run(cmd,capture_output=True,timeout=10);summary=json.loads((path/'summary.json').read_text());rows=[json.loads(line) for line in (path/'trace.jsonl').read_text().splitlines()]
 entries=[row for row in rows if row['event']=='stdio-write-entry'];execs=[row for row in rows if row['event']=='backend-exec'];target=summary['delegate']
 passed=child.returncode==0 and child.stdout==b'actual child query\n' and child.stderr==b'original backend stderr\n' and summary['summary']['complete'] is True and summary['summary']['exitCode']==0 and len(execs)==1 and all(row['identity']==target for row in execs) and [bytes.fromhex(row['offeredBytesHex']) for row in entries]==[child.stdout,child.stderr]
 for p in path.iterdir():p.chmod(0o600)
 result=dict(result='pass' if passed else 'fail',scope=scope,command=cmd,wrapperExit=child.returncode,stdoutHex=child.stdout.hex(),stderrHex=child.stderr.hex(),originalDelegate=target,originalDelegateExit=summary['summary']['exitCode'],observerComplete=summary['summary']['complete'],onlyOriginalExecObserved=len(execs)==1,traceSHA256=hashlib.sha256((path/'trace.jsonl').read_bytes()).hexdigest(),genuineSignals=[r['signal'] for r in rows if r['event']=='genuine-signal-forward'],sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'delegate_diagnostics.py',B/'test_delegate_diagnostics.py',Path('/usr/bin/python3').resolve(),B/'observer_descendant_checkpoint.py')},noDesktopLaunch=True,noDescendantAttach=True)
 report=B/'observer-descendant-checkpoint.json'
 with report.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 report.chmod(0o600);print(json.dumps(dict(result=result['result'],kernelCase='original delegate with untraced subprocess',noDesktopLaunch=True)));return int(not passed)
if __name__=='__main__':raise SystemExit(main())
