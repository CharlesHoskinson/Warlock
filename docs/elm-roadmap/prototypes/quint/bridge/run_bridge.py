#!/usr/bin/env python3
"""Bounded CPU-only bridge model experiments; every Quint process is protected."""
import hashlib,json,os,re,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RECEIPTS=ROOT/'receipts'
RECEIPTS.mkdir(exist_ok=True)
QUINT='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
PREFIX=['/usr/bin/python3','-B','/home/hoskinson/window-integration-qa/qa_run.py','--',QUINT]
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
records=[]
def run(name,args,expected=0):
    command=PREFIX+args
    started=time.time()
    p=subprocess.run(command,cwd=ROOT,env=ENV,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    log=RECEIPTS/(name+'.log');log.write_text(p.stdout)
    record={'name':name,'command':command,'seed':'20261003' if '--seed' in args else None,'exitCode':p.returncode,'expectedExitCode':expected,'expectedOutcomeObserved':p.returncode==expected,'seconds':round(time.time()-started,3),'logSha256':hashlib.sha256(log.read_bytes()).hexdigest()}
    records.append(record)
    print(json.dumps(record),flush=True)
    return p.returncode
source=(ROOT/'bridge.qnt').read_text()
run('version',['--version'])
run('typecheck',['typecheck','bridge.qnt'])
run('named-tests',['test','bridge.qnt','--match','Test$','--seed','20261003','--max-samples','1','--out-itf',str(RECEIPTS/'correct-{test}-{seq}.itf.json')])
run('simulation',['run','bridge.qnt','--invariants','safety','--seed','20261003','--max-samples','2000','--max-steps','40','--out-itf',str(RECEIPTS/'simulation-{seq}.itf.json')])
mutations=[
 ('ignore-epoch','s.reqEpoch == s.epoch','true','nativeEpochChangedTest'),
 ('ignore-incarnation','s.reqIncarnation == s.incarnation','true','incarnationReuseTest'),
 ('ignore-revision','s.reqRevision == s.revision','true','revisionChangeTest'),
 ('ignore-gap','or n != s.seq + 1','or false','gapBarrierTest'),
 ('cancel-noop','s.with("status", "Cancelled")','s','cancelBeforeCommitTest'),
 ('dedup-disabled','s.used.contains(id) or s.barrier','false or s.barrier','duplicateCommitTest'),
 ('deadline-disabled','s.clock < s.reqDeadline','true','expiredDeadlineTest'),
 ('unknown-dependency','s.dependency == "Committed" and not(s.barrier)','s.dependency != "Refused" and not(s.barrier)','unknownDependencyTest'),
 ('dependency-incarnation','s.depIncarnation == s.incarnation','true','staleDependencyTest'),
]
for name,old,new,test in mutations:
    assert old in source,(name,old)
    path=ROOT/(name+'.qnt');path.write_text(source.replace(old,new,1))
    run(name,['test',path.name,'--main','bridge','--match',test,'--seed','20261003','--max-samples','1','--out-itf',str(RECEIPTS/(name+'-{test}-{seq}.itf.json'))],1)
manifest={'schema':1,'status':'CPU model experiment only; implementation/native acceptance pending','requirements':['ELM-ARC-006','ELM-ARC-007','ELM-ARC-008','ELM-ARC-012','ELM-REV-007','ELM-REV-008','ELM-REV-011','ELM-REV-012'], 'namedTests':re.findall(r'run (\w+Test)',source),'records':records,'artifacts':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and p.name!='manifest.json'},'limitations':['Finite request IDs 1/2; native identities abstract integer tokens, not serialization proof.','Atomic commit/cancel abstraction does not establish actual native thread locking.','Snapshot action assumes native coherent snapshot; no transport parser or socket implementation.','Monotonic tick clock is abstract; no real latency or deadline measurement.','Dependency receipts are authenticated model inputs; no wire authentication proof.','Simulation samples are not exhaustive formal verification and not native/UI acceptance.']}
(RECEIPTS/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
raise SystemExit(0 if all(r['expectedOutcomeObserved'] for r in records) else 1)
