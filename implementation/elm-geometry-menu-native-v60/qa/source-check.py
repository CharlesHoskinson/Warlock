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
  upstream=json.loads((ROOT/'upstream.json').read_text());original=pathlib.Path(upstream['clientHelperParent']).read_text();current=(ROOT/'qa/client_evidence.py').read_text();old_nodes={n.name:ast.get_source_segment(original,n) for n in ast.parse(original).body if isinstance(n,ast.FunctionDef)};new_nodes={n.name:ast.get_source_segment(current,n) for n in ast.parse(current).body if isinstance(n,ast.FunctionDef)}
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
  report.update(passed=True,deadlineChecks=3,extractedFunctions=len(new_nodes),sourceHeld=True,selectedBuild=str(runner.BUILD),selectedBuildSHA256=runner.BUILD_HASH,compiledBinarySHA256=build['binarySHA256'],selectedPair=pair['nativePair'],fixture=fixture,allContractScenariosPassed=False)
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 p=out/'report.json';p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(p),'error':report.get('error')}),flush=True);return not report['passed']
if __name__=='__main__':raise SystemExit(main())
