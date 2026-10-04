"""Protected CPU preflight and actual deadline/helper checks; never launches GUI."""
import ast,hashlib,importlib.util,json,pathlib,shutil,sys,time,traceback,types
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def main():
 sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
 scope=require_qa_scope();out=ROOT/'qa'/('source-check-'+str(time.time_ns()));out.mkdir();paths=[ROOT/'qa/native.py',ROOT/'qa/client_evidence.py',ROOT/'candidate_host.py',ROOT/'upstream.json',pathlib.Path(__file__).resolve()];sources={str(p):digest(p) for p in paths};report={'passed':False,'nativeAcceptance':False,'scope':'CPU preflight, extracted helper identity and absolute deadline checks only','qaScope':scope,'sources':sources}
 for p in paths:
  dest=out/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 try:
  spec=importlib.util.spec_from_file_location('v60_cpu_runner',ROOT/'qa/native.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);build,pair,pointer,fixture=runner.preflight()
  upstream=json.loads((ROOT/'upstream.json').read_text())
  parent_path=pathlib.Path(upstream['parentRunner']);assert digest(parent_path)==upstream['parentRunnerSHA256']
  old_tree=ast.parse(parent_path.read_text());new_tree=ast.parse((ROOT/'qa/native.py').read_text())
  class HideOpen(ast.NodeTransformer):
   def visit_FunctionDef(self,node):
    if node.name=='open_menu':node.body=[ast.Pass()];return node
    return self.generic_visit(node)
  assert ast.dump(HideOpen().visit(old_tree),include_attributes=False)==ast.dump(HideOpen().visit(new_tree),include_attributes=False),'Only open_menu may change'
  failure_path=pathlib.Path(upstream['preservedFailureReport']);assert digest(failure_path)==upstream['preservedFailureReportSHA256'];failure=json.loads(failure_path.read_text());assert failure['passed'] is False and failure['cleanupPassed'] is True
  for relative,value in failure['artifacts'].items():assert digest(failure_path.parent/relative)==value,relative
  open_node=next(n for n in ast.walk(ast.parse((ROOT/'qa/native.py').read_text())) if isinstance(n,ast.FunctionDef) and n.name=='open_menu')
  import textwrap
  menu_function=textwrap.dedent(ast.get_source_segment((ROOT/'qa/native.py').read_text(),open_node));route_checks=0
  def route_case(minimized=False,multiple=False,wrong_root=False,available=True):
   identity='1';root={'incarnation':'2' if wrong_root else identity,'minimized':minimized,'available':available,'owner':None,'application':'elm-maximize-probe'};roots=[root]
   if multiple:roots.append({**root,'incarnation':'3'})
   binding={'lifetime':'1','session':'2','frontend':'3'};value={'phase':'Coherent','groups':[{'key':'application:elm-maximize-probe','disabled':False,'point':[200,21]}],'menu':None};clicks=[];picker={'incarnation':identity,'point':[210,100]}
   def pointer(item,button,deadline):
    clicks.append((item['point'],button))
    if len(roots)==1 or item is picker:value['menu']={'incarnation':identity}
   def one_wait(predicate,deadline=None):
    result=predicate()
    if not result:raise RuntimeError('No current eligible identity/state')
    return result
   namespace={'time':types.SimpleNamespace(monotonic=lambda:0),'geometry_row':lambda:{'incarnation':identity,'minimized':minimized},'coherent':lambda:value,'geometry':lambda:{'binding':binding},'incoming':lambda:[{'kind':'action-projection','binding':binding,'scene':{'windows':roots}}],'identity':identity,'wait':one_wait,'check':lambda name,result,**kw:result or (_ for _ in ()).throw(AssertionError(name)),'effects':lambda:[],'parent_pointer':pointer,'row':lambda state:picker if clicks else None}
   exec(menu_function,namespace);namespace['open_menu']('Minimized' if minimized else 'Open',deadline=6);return clicks
  assert route_case()==[([200,21],273)];route_checks+=1
  assert route_case(minimized=True)==[([200,21],273)];route_checks+=1
  assert route_case(multiple=True)==[([200,21],273),([210,100],273)];route_checks+=1
  for kwargs in [{'wrong_root':True},{'available':False}]:
   try:route_case(**kwargs)
   except RuntimeError:route_checks+=1
   else:raise AssertionError('Stale/unavailable root must refuse before click')
  original=pathlib.Path(upstream['clientHelperParent']).read_text();current=(ROOT/'qa/client_evidence.py').read_text();old_nodes={n.name:ast.get_source_segment(original,n) for n in ast.parse(original).body if isinstance(n,ast.FunctionDef)};new_nodes={n.name:ast.get_source_segment(current,n) for n in ast.parse(current).body if isinstance(n,ast.FunctionDef)}
  for name in upstream['extractedFunctions']:
   expected=old_nodes[name]
   if name=='validate_pixels':expected=expected.replace('points = [(x + width // 2, y + height // 2), (x + 12, y + 12), (x + width - 13, y + height - 13)]','points = [(x + width // 2, y + height // 2), (x + 12, max(64, y + 12)), (x + width - 13, y + height - 13)]')
   assert new_nodes[name]==expected,name
  clock=types.SimpleNamespace(value=0);clock.monotonic=lambda:clock.value;clock.sleep=lambda n:setattr(clock,'value',clock.value+n);runner.time=clock;runner.session=types.SimpleNamespace(guard=lambda:None)
  assert runner.wait(lambda:True,deadline=1) is True
  seen=[];assert runner.wait(lambda d:seen.append(d) or True,timed=True,deadline=1) is True and seen==[1]
  def late():clock.value=2;return True
  try:runner.wait(late,deadline=1)
  except RuntimeError:pass
  else:raise AssertionError('Late completion must be rejected, even with truthy predicate')
  for p,value in sources.items():assert digest(p)==value,p
  report.update(passed=True,menuRouteChecks=route_checks,onlyOpenMenuChanged=True,preservedNativeFailureCleanup=True,deadlineChecks=3,extractedFunctions=len(new_nodes),sourceHeld=True,selectedBuild=str(runner.BUILD),selectedBuildSHA256=runner.BUILD_HASH,compiledBinarySHA256=build['binarySHA256'],selectedPair=pair['nativePair'],fixture=fixture,allContractScenariosPassed=False)
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 p=out/'report.json';p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(p),'error':report.get('error')}),flush=True);return not report['passed']
if __name__=='__main__':raise SystemExit(main())
