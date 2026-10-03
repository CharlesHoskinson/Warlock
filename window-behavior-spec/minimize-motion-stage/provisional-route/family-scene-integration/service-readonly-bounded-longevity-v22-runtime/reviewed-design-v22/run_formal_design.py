from pathlib import Path
import subprocess,json,hashlib,time,re
p=Path(__file__).resolve().parent
sources={str(p/n):hashlib.sha256((p/n).read_bytes()).hexdigest() for n in ['bounded_read_authority.qnt','bounded_read_authority_test.qnt','BOUNDED_AUTHORITY_CONTRACT.md']}
commands=[['quint','typecheck','bounded_read_authority_test.qnt'],['quint','test','bounded_read_authority_test.qnt','--backend=rust','--seed=2026100222'],['quint','run','bounded_read_authority.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100222','--verbosity=0'],['quint','run','bounded_read_authority.qnt','--step=validStep','--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100223','--verbosity=0']]
records=[]
for i,cmd in enumerate(commands):
 log=p/f'design-formal-{i}.log';t=time.monotonic()
 with log.open('wb') as f:r=subprocess.run(cmd,cwd=p,stdout=f,stderr=subprocess.STDOUT)
 records.append({'command':cmd,'exitCode':r.returncode,'elapsedSeconds':time.monotonic()-t,'log':str(log),'sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
 record={'version':1,'named':len(re.findall(r'^ run ',(p/'bounded_read_authority_test.qnt').read_text(),re.M)),'samples':2000,'steps':100,'runs':2,'sourceSHA256':sources,'commands':records,'runtimeCopied':False,'runtimeChanged':False,'nativeLaunch':False,'scopeReviewPending':True,'sourceUnchanged':all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in sources.items()),'passed':all(c['exitCode']==0 for c in records) and len(records)==len(commands) and all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in sources.items())}
 (p/'formal-design-before-runtime.json').write_text(json.dumps(record,indent=2)+'\n')
 if r.returncode:break
