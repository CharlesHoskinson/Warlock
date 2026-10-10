"""UI-006 empty workspace inventory model and strict observer boundary."""
import copy,hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
out=root/'qa/runs'/('workspace-inventory-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'protectedScope':scope,'commands':[],'inputs':{str(p):sha(p) for p in [root/'qa/workspace-inventory.qnt',root/'qa/workspace-inventory_test.qnt']},'scope':'Correlated current geometry/workspace inventory, empty browsing/active marker, retirement/authority and observation-only dismissal. Native navigation, grants, transport timing, painting and AT excluded.','nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 for name,path,args in [('typecheck','workspace-inventory.qnt',['typecheck']),('tests-typecheck','workspace-inventory_test.qnt',['typecheck']),('named','workspace-inventory_test.qnt',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=79561']),('witness-safety','workspace-inventory.qnt',['run','--backend=typescript','--invariants=safety','--witnesses','emptyWitness','activeEmptyWitness','retiredWitness','replacementWitness','--max-samples=1000','--max-steps=30','--seed=79562'])]:
  command=['quint',args[0],str(root/'qa'/path),*args[1:]];p=subprocess.run(command,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'command':command,'exitCode':p.returncode});assert p.returncode==0,p.stdout+p.stderr
  if name=='witness-safety':
   counts={n:int(c) for n,c in re.findall(r'(\w+Witness) was witnessed in (\d+) trace',p.stdout)};assert len(counts)==4 and all(counts.values());report['witnesses']=counts
 if sys.argv[1:]!=['--model-only']:
  assert not sys.argv[1:];sys.path.insert(0,str(root/'adapter'));from geometry_endpoint import workspace_inventory;from endpoint import Refused
  facts={'focused':None,'inputBlocked':False,'windows':[],'workspaces':[{'identity':'1','generation':'1','monitor':'0','outputOwnershipGeneration':'1'},{'identity':'3','generation':'3','monitor':'0','outputOwnershipGeneration':'1'}],'activeWorkspace':'3'}
  assert workspace_inventory(facts)==facts['workspaces'];checks={'currentEmptyWithNativeActive':True}
  legacy={k:facts[k] for k in ['focused','inputBlocked','windows']};assert workspace_inventory(legacy) is None;checks['legacyExplicitlyUnsupported']=True
  mutations={'duplicateWorkspace':lambda f:f['workspaces'].append(copy.deepcopy(f['workspaces'][0])),'zeroWorkspace':lambda f:f['workspaces'][0].update(identity='0'),'negativeWorkspace':lambda f:f['workspaces'][0].update(identity='-1'),'noncanonicalWorkspace':lambda f:f['workspaces'][0].update(identity='03'),'signedOverflow':lambda f:f['workspaces'][0].update(identity=str(1<<63)),'zeroOwner':lambda f:f['workspaces'][0].update(generation='0'),'noncanonicalMonitor':lambda f:f['workspaces'][0].update(monitor='01'),'zeroOutputOwner':lambda f:f['workspaces'][0].update(outputOwnershipGeneration='0'),'unknownActive':lambda f:f.update(activeWorkspace='2'),'missingActive':lambda f:f.pop('activeWorkspace'),'missingWorkspaces':lambda f:f.pop('workspaces'),'unknownRowField':lambda f:f['workspaces'][0].update(extra=True),'unknownFactField':lambda f:f.update(extra=True),'workspaceBound':lambda f:f.update(workspaces=f['workspaces']*129),'nonlist':lambda f:f.update(workspaces={})}
  for name,mutate in mutations.items():
   bad=copy.deepcopy(facts);mutate(bad)
   try:workspace_inventory(bad)
   except Refused:checks[name]=True
   else:raise AssertionError(name)
  report['decoderChecks']=checks;report['inputs'][str(root/'adapter/geometry_endpoint.py')]=sha(root/'adapter/geometry_endpoint.py')
 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
