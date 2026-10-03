import hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from qa_launch import require_qa_scope
def stamp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':p.stat().st_mode&0o7777}
def main():
 scope=require_qa_scope();inputs={str(p):stamp(p)for p in (HERE/'hidden_capture.qnt',HERE/'hidden_capture_test.qnt',HERE/'formal-before-runtime.json',HERE/'formal_driver.py',Path(__file__))}
 names=re.findall(r'^ run ([A-Za-z0-9_]+)=', (HERE/'hidden_capture_test.qnt').read_text(),re.M);assert len(names)==18
 command=['quint','test','hidden_capture_test.qnt','--match=^('+'|'.join(names)+')$','--backend=rust','--seed=2026100229']
 with os.fdopen(os.open(HERE/'named-exact.log',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as out:r=subprocess.run(command,cwd=HERE,stdout=out,stderr=subprocess.STDOUT,timeout=60)
 text=(HERE/'named-exact.log').read_text();assert r.returncode==0 and '18 passing' in text and all('ok '+name+' passed' in text for name in names)
 assert inputs=={p:stamp(Path(p))for p in inputs}
 original=json.loads((HERE/'formal-before-runtime.json').read_text());assert all(c['exitCode']==0 for c in original['checks'])
 row={'result':'pass','scope':scope,'named':18,'names':names,'command':command,'exitCode':r.returncode,'log':str(HERE/'named-exact.log'),'logSHA256':stamp(HERE/'named-exact.log')['sha256'],'retainedInvariantProof':str(HERE/'formal-before-runtime.json'),'samples':2000,'steps':100,'sources':inputs,'correction':'Original default test selected zero named runs; only explicit anchored run names supply named authority. Broad match diagnostic is failed and supplies none.','runtimeApplied':False}
 with os.fdopen(os.open(HERE/'formal-complete.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
 print(json.dumps({'result':'pass','named':18,'report':str(HERE/'formal-complete.json')}))
if __name__=='__main__':main()
