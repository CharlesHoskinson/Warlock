import pathlib,json,hashlib,subprocess,time,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity');out=root/'implementation/warlock/qa/runs'/('caption-original-models-'+str(time.time_ns()));out.mkdir()
r={'passed':False,'protectedScope':require_qa_scope(),'nativeAcceptance':False,'scope':'Frozen caption_drag/native_drag original named cases and sampled safety, unchanged models; no native acceptance.','inputs':{},'commands':[]}
try:
 for model in ['caption_drag','native_drag']:
  for suffix in ['', '_test']:
   p=root/'window-behavior-spec'/(model+suffix+'.qnt');r['inputs'][str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
  for name,args in [('typecheck',['typecheck',str(root/'window-behavior-spec'/(model+'.qnt'))]),('named',['test',str(root/'window-behavior-spec'/(model+'_test.qnt')),'--backend=typescript','--match=Test$','--max-samples=1','--seed=79940']),('safety',['run',str(root/'window-behavior-spec'/(model+'.qnt')),'--backend=typescript','--invariants=allProps','--max-samples=1000','--max-steps=30','--seed=79941'])]:
   cmd=['quint',*args];p=subprocess.run(cmd,capture_output=True,text=True,timeout=180);(out/(model+'-'+name+'.stdout')).write_text(p.stdout);(out/(model+'-'+name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':model+'-'+name,'command':cmd,'exitCode':p.returncode});assert p.returncode==0,p.stdout+p.stderr
 r['passed']=True
except Exception as e:r['error']=repr(e)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(out/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
