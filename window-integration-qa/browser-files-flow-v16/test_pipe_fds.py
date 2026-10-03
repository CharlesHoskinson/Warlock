"""Actual subprocess fd3/fd4 exchange without starting browser/display."""
from pathlib import Path
import argparse,json,os,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path);args=parser.parse_args()
scope=require_qa_scope();cases=[]
for collision in ('original','destination-swap','high'):
 rd,wr=os.pipe();rr,ww=os.pipe()
 child='''import os,sys
sys.path.insert(0,sys.argv[1]);from browser_exec import remap_pipe
rd,wr=int(sys.argv[2]),int(sys.argv[3])
'''
 if collision=='destination-swap':
  child+='''import fcntl
r=fcntl.fcntl(rd,fcntl.F_DUPFD_CLOEXEC,20);w=fcntl.fcntl(wr,fcntl.F_DUPFD_CLOEXEC,20)
os.dup2(r,4);os.dup2(w,3);os.close(r);os.close(w);rd,wr=4,3
'''
 if collision=='high':
  child+='''import fcntl
rd=fcntl.fcntl(rd,fcntl.F_DUPFD_CLOEXEC,20);wr=fcntl.fcntl(wr,fcntl.F_DUPFD_CLOEXEC,20)
'''
 child+='''remap_pipe(rd,wr)
value=os.read(3,1024);os.write(4,b"returned:"+value)
assert os.get_inheritable(3) and os.get_inheritable(4)
'''
 p=subprocess.Popen([sys.executable,'-c',child,str(B),str(rd),str(ww)],pass_fds=(rd,ww),stderr=subprocess.PIPE)
 os.close(rd);os.close(ww);os.write(wr,b'actual-pipe\x00');os.close(wr);value=os.read(rr,1024);os.close(rr);_,error=p.communicate(timeout=5)
 assert p.returncode==0 and value==b'returned:actual-pipe\x00',(collision,error,value)
 cases.append({'name':collision,'passed':True,'returncode':p.returncode,'readwriteDescriptors':[3,4]})
report={'scope':scope,'cases':cases,'browserExecuted':False}
if args.report:
 with args.report.open('x') as handle:json.dump(report,handle,indent=2)
 args.report.chmod(0o600)
print(json.dumps(report))
