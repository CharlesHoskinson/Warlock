"""quint-llm-kit UI-004 focus/visibility projection and actual adapter contract; native/AT separate."""
import copy,hashlib,importlib.util,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
assert sys.argv[1:] in ([],['--init']);initial=bool(sys.argv[1:])
out=root/'qa/runs'/('taskbar-output-focus-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r=dict(passed=False,scope=__doc__,nativeAcceptance=False,protectedScope=scope,commands=[])
def run(name,args):
 p=subprocess.run(list(map(str,args)),capture_output=True,timeout=180)
 (out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append(dict(name=name,command=list(map(str,args)),exitCode=p.returncode))
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-2000:]+p.stdout.decode(errors='replace')[-1000:])
 return p.stdout.decode()
try:
 model=root/'qa/taskbar-output-focus.qnt';tests=root/'qa/taskbar-output-focus_test.qnt'
 r['inputs']={str(p.relative_to(root)):sha(p) for p in [model,tests] if p.exists()}
 run('typecheck',['quint','typecheck',model])
 run('init',['quint','run',model,'--backend=typescript','--invariants=safety','--max-samples=1','--max-steps=1','--seed=91000'])
 if not initial:
  run('named',['quint','test',tests,'--backend=typescript','--match=Test$','--max-samples=1','--seed=91001'])
  names=('ghostSuppressed','activated','minimized','restored','barCustody','popupCustody')
  witnesses=run('witnesses',['quint','run',model,'--backend=typescript','--witnesses',*names,'--max-samples=1000','--max-steps=20','--seed=91002'])
  r['witnessCounts']={n:int(c) for n,c in re.findall(r'(\w+) was witnessed in (\d+) trace',witnesses)}
  assert all(r['witnessCounts'].get(n,0)>0 for n in names)
  run('safety',['quint','run',model,'--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=20','--seed=91003'])
  adapter=root/'adapter/taskbar_projection.py';r['inputs'][str(adapter.relative_to(root))]=sha(adapter)
  spec=importlib.util.spec_from_file_location('actual_taskbar_projection',adapter);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  row={'incarnation':'2','owner':None,'application':'GTK Application','workspace':'2','workspaceVisible':False,'hidden':False,'minimized':False,'attention':False}
  facts={'revision':'8','outputGeneration':'6','attentionProtocol':1,'facts':{'focused':'2','windows':[row]}}
  snapshot={'windows':[{'incarnation':'2','application':'GTK Application','label':'Draft','minimized':False}]}
  r['adapterCases']=[]
  def check(name,condition):
   r['adapterCases'].append({'name':name,'passed':bool(condition)})
   assert condition,name
  scene=module.coherent_scene(facts,snapshot,copy.deepcopy(facts))
  check('InvisibleNativeFocusDoesNotOfferMinimize',scene['focused'] is None and scene['windows'][0]['available'] and facts['facts']['focused']=='2')
  visible=copy.deepcopy(facts);visible['facts']['windows'][0]['workspaceVisible']=True
  check('VisibleDesktopFocusSurvivesShellKeyboardCustody',module.coherent_scene(visible,snapshot,copy.deepcopy(visible))['focused']=='2')
  hidden=copy.deepcopy(visible);hidden['facts']['windows'][0]['hidden']=True
  check('HiddenNativeFocusNotActive',module.coherent_scene(hidden,snapshot,copy.deepcopy(hidden))['focused'] is None)
  minimized=copy.deepcopy(visible);minimized['facts']['windows'][0]['minimized']=True;min_snapshot=copy.deepcopy(snapshot);min_snapshot['windows'][0]['minimized']=True
  check('MinimizedNativeFocusNotActive',module.coherent_scene(minimized,min_snapshot,copy.deepcopy(minimized))['focused'] is None)
  no_focus=copy.deepcopy(visible);no_focus['facts']['focused']=None
  check('NoNativeFocusNeverInventsActiveMember',module.coherent_scene(no_focus,snapshot,copy.deepcopy(no_focus))['focused'] is None)
  special=copy.deepcopy(visible);special['facts']['windows'][0]['workspace']='-1'
  check('SpecialWorkspaceCannotOfferPrimaryMinimize',module.coherent_scene(special,snapshot,copy.deepcopy(special))['focused'] is None)
  changed=copy.deepcopy(visible);changed['facts']['windows'][0]['workspaceVisible']=False
  check('MixedVisibilitySnapshotRefusesProjection',module.coherent_scene(visible,snapshot,changed) is None)
  generation=copy.deepcopy(visible);generation['outputGeneration']='7'
  check('ChangedOutputGenerationRefusesProjection',module.coherent_scene(visible,snapshot,generation) is None)
  membership=copy.deepcopy(snapshot);membership['windows']=[]
  check('ChangedMembershipRefusesProjection',module.coherent_scene(visible,membership,visible) is None)
  check('ChangedMinimizedSnapshotRefusesProjection',module.coherent_scene(visible,min_snapshot,visible) is None)
 r['passed']=True
except Exception as e:r['error']=repr(e)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=r['passed'],report=str(out/'report.json'),error=r.get('error'))));raise SystemExit(not r['passed'])
