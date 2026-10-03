import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from qa_launch import require_qa_scope

def main():
 scope=require_qa_scope()
 commands=['dispatch hl.dsp.focus({ '+field+' = "'+value+'" })' for _ in range(3) for field,value in [('monitor','CPU-1'),('workspace','1')]]
 source=Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback/inverses/core/src/debug/HyprCtl.cpp').read_text()
 start=source.index('static std::string dispatchBatch(');end=source.index('\n}',start)+2;body=source[start:end]
 assert body in (HERE/'actual_dispatch_batch.cpp').read_text()
 assert body==json.loads((HERE/'parser-extraction.json').read_text())['exactBody']
 run=subprocess.run([str(HERE/'actual_dispatch_batch')],input='[[BATCH]]'+';'.join(commands)+'\n',capture_output=True,text=True,check=True,timeout=2)
 reply,seen=run.stdout.split('\n---fixture-seen---\n')
 assert seen.splitlines()==commands and len(reply.split('\n\n\n'))==6 and 'error: CPU second action' in reply
 row={'result':'pass','scope':scope,'commands':commands,'reply':reply,'seen':seen.splitlines(),'exitCode':run.returncode,'actualBodyUnchanged':True,'bodySHA256':hashlib.sha256(body.encode()).hexdigest(),
 'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()},
 'limit':'Exact selected primary parser body with recording getReply fixture; no native effects or backend timing claim.'}
 with os.fdopen(os.open(HERE/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'result':'pass','report':str(HERE/'report.json')}))

if __name__=='__main__':main()
