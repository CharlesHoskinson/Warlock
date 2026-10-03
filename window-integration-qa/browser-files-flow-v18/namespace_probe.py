"""Namespace-only offline proof. Does not execute browser or compositor."""
import argparse,json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
from network_guard import network_authority
B=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--child',action='store_true');p.add_argument('--parent');p.add_argument('--uid',type=int);p.add_argument('--report',type=Path);args=p.parse_args()
scope=require_qa_scope()
if args.child:
 print(json.dumps({'scope':scope,'network':network_authority(args.parent,args.uid),'browserExecuted':False}));raise SystemExit(0)
parent=os.readlink('/proc/self/ns/net')
proc=subprocess.run(['/usr/bin/unshare','--user','--map-current-user','--net','--',sys.executable,str(B/'namespace_probe.py'),'--child','--parent',parent,'--uid',str(os.getuid())],capture_output=True,text=True,timeout=10)
report={'result':'pass' if proc.returncode==0 else 'fail','scope':scope,'parentNetNamespace':parent,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'browserExecuted':False}
if proc.returncode==0:report['child']=json.loads(proc.stdout)
if args.report:
 with args.report.open('x') as handle:json.dump(report,handle,indent=2)
 args.report.chmod(0o600)
print(json.dumps(report));raise SystemExit(proc.returncode)
