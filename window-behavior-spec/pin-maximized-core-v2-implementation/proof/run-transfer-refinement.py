from pathlib import Path
import subprocess,json,time,hashlib,re
source=Path('pin_transfer_refinement.qnt'); commands=[['quint','typecheck',str(source)],['quint','test',str(source),'--max-samples=1','--match','^('+ '|'.join(re.findall(r'run (\w+)',source.read_text())) +')$'],['quint','run',str(source),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=2026100241']]
rows=[]
for i,cmd in enumerate(commands):
 path=Path('proof')/f'transfer-refinement-before-implementation-{i}.log';start=time.time();p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(p.stdout);rows.append({'argv':cmd,'exitCode':p.returncode,'elapsed':time.time()-start,'log':str(path),'logSha256':hashlib.sha256(p.stdout).hexdigest()})
 if p.returncode:break
Path('proof/transfer-refinement-before-implementation.json').write_text(json.dumps({'runtimeRefinementImplemented':False,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'commands':rows,'passed':len(rows)==3 and all(r['exitCode']==0 for r in rows),'nativeAuthorized':False},indent=2)+'\n')
print(rows[-1]['exitCode']);print(rows[-1]['log'])
