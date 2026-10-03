from pathlib import Path
import subprocess,re,json,hashlib,time
B=Path(__file__).resolve().parent
model=B/'input_block.qnt';names=re.findall(r'^\s*run\s+(\w+)',model.read_text(),re.M)
assert len(names)==14 and len(set(names))==14
commands=[['quint','typecheck','input_block.qnt'],['quint','test','input_block.qnt','--match','^('+'|'.join(names)+')$','--max-samples','1'],['quint','run','input_block.qnt','--invariant','allProps','--max-samples','2000','--max-steps','100','--seed','26100411']]
rows=[]
for i,cmd in enumerate(commands):
 t=time.monotonic();p=subprocess.run(cmd,cwd=B,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);log=B/f'formal-{i}.log';log.write_bytes(p.stdout)
 row=dict(argv=cmd,exitCode=p.returncode,elapsedSeconds=time.monotonic()-t,log=str(log),logSHA256=hashlib.sha256(p.stdout).hexdigest());rows.append(row)
 if i==1:
  got=re.findall(r'^\s*ok\s+(\w+)\s+passed 1 test\(s\)',p.stdout.decode(),re.M)
  row['actualPassedNames']=got;row['actualCount']=len(got);row['exactSelectedNamesPassed']=set(got)==set(names)and len(got)==14
 if p.returncode or i==1 and not row['exactSelectedNamesPassed']:break
passed=len(rows)==3 and all(r['exitCode']==0 for r in rows)and rows[1].get('exactSelectedNamesPassed')is True
(B/'FORMAL_PROOF.json').write_text(json.dumps(dict(sourceModelSHA256=hashlib.sha256(model.read_bytes()).hexdigest(),sourceNamed=names,commands=rows,allPass=passed,actualNamedCount=rows[1].get('actualCount',0)if len(rows)>1 else 0,sourceOnly=True,nativeReachabilityProved=False,runtimeImplemented=False),indent=2)+'\n')
print(json.dumps(dict(allPass=passed,actualNamed=len(rows[1].get('actualPassedNames',[]))if len(rows)>1 else 0)))
raise SystemExit(0 if passed else 1)
