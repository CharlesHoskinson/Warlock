from pathlib import Path
import hashlib,json,os,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path(__file__).resolve().parent.parent;D=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();V8=Path('/home/hoskinson/window-integration-qa/thumbnail-v8-terminal-source-handoff-v1.json');assert sha(V8)=='4a9bb60a64b884cbe87a747446757336e646600a588a7d06e16e1f8511aac5aa';old=json.loads(V8.read_text());assert all(sha(p)==h and Path(p).stat().st_mode&0o7777==old['inputModes'][p]for p,h in old['inputs'].items())
models={n:sha(B/n)for n in ('renderer_collector_binding.qnt','renderer_collector_binding_test.qnt','RENDERER_COLLECTOR_BINDING_CONTRACT.md')};commands=[['quint','typecheck',str(B/'renderer_collector_binding_test.qnt')],['quint','test',str(B/'renderer_collector_binding_test.qnt'),'--backend=rust'],['quint','run',str(B/'renderer_collector_binding.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100704','--verbosity=1']];checks=[]
for i,c in enumerate(commands):
 r=subprocess.run(c,cwd=B,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60);log=D/('check-'+str(i)+'.log')
 with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:f.write(r.stdout)
 checks.append(dict(command=c,exitCode=r.returncode,log=str(log),sha256=sha(log)));print(r.stdout,flush=True)
 if r.returncode:break
stable=all(sha(p)==h and Path(p).stat().st_mode&0o7777==old['inputModes'][p]for p,h in old['inputs'].items())and all(sha(B/n)==h for n,h in models.items());row=dict(result='pass'if len(checks)==3 and all(c['exitCode']==0 for c in checks)and stable else'fail',scope=scope,checks=checks,models=models,inheritedV8Untouched=stable,inheritedV8InputCount=439,selectedV24ManifestSHA256='b017d8d2a126f76c637429fffc2d77d510161fb89d3f3826795abb47d30b9f2c',runtimeEdited=False,nativeLaunch=False,nativeAccepted=False)
with os.fdopen(os.open(D/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
raise SystemExit(row['result']!='pass')
