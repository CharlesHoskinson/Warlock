#!/usr/bin/env python3
"""Protected production-code differential properties and existing action replays."""
import hashlib,json,os,resource,shutil,subprocess,sys,time,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[3];P=R/'implementation/warlock';H=R/'implementation/warlock-preview-provider-v143';B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild');NODE=Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def checked(p,h):
 body=Path(p).read_bytes()
 if hashlib.sha256(body).hexdigest()!=h:raise RuntimeError('Pinned input changed '+str(p))
 return body
def check(m):
 for p,h in m.items():checked(p,h)
def main():
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise RuntimeError('Protected no-argument no-bytecode launch required')
 sys.path.insert(0,str(R/'window-integration-qa'));from qa_launch import require_qa_scope
 scope=require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('Core limit changed')
 out=B/('snapshot-contracts-'+str(time.time_ns()));out.mkdir(mode=0o700)
 report={'passed':False,'nativeAcceptance':False,'requirementAccepted':False,'scope':scope,'commands':[],'seed':'0x5eed1234','randomValidCaseBudget':200,'shrinking':'No shrinker; complete failing inputs and sequence are retained.','driverSHA256':sha(__file__)}
 def run(name,argv,cwd,env):
  argv=list(map(str,argv));a=out/(name+'.stdout');b=out/(name+'.stderr')
  try:
   p=subprocess.run(argv,cwd=cwd,env=env,capture_output=True,timeout=240)
  except subprocess.TimeoutExpired as error:
   a.write_bytes(error.stdout or b'');b.write_bytes(error.stderr or b'');report['commands'].append({'name':name,'argv':argv,'cwd':str(cwd),'environment':env,'exit':None,'timedOut':True,'timeoutSeconds':240,'stdoutSHA256':sha(a),'stderrSHA256':sha(b)})
   raise RuntimeError(name+' timed out; partial output retained') from error
  a.write_bytes(p.stdout);b.write_bytes(p.stderr);report['commands'].append({'name':name,'argv':argv,'cwd':str(cwd),'environment':env,'exit':p.returncode,'stdoutSHA256':sha(a),'stderrSHA256':sha(b)})
  if p.returncode:raise RuntimeError(name+' failed')
  return p.stdout
 try:
  m=json.loads(checked(H/'qa/toolchain.json','fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa'))
  built=json.loads(checked(B/'surface-snapshot-build-root-v1/output/report.json','58eb125aec928bdb2b6a71cbe6b93e5f1d11db5ba350df2ed7f5a4ab8b4a50fb'))
  if not built['passed']:raise RuntimeError('Current roots not built')
  sources=dict(built['sources']);qa=['SurfaceSnapshotContracts.elm','snapshot-contracts.cjs','ThreeGroupReplay.elm','NativePointerFixture.elm','OutputRetirementReplay.elm','feedback-replay.js']
  for name in qa:sources[str(P/'qa'/name)]=sha(P/'qa'/name)
  sources[str(Path(__file__).resolve())]=sha(__file__);check(sources)
  held={str(H/name):v['sha256'] for name,v in m['heldFiles'].items()};check(held)
  compiler=H/m['compiler'];checked(compiler,'c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948');checked(NODE,'caa24debe02770c92a70677e2a62ca98890150e7ac1c17bcfe31bcc98cc89943')
  baseline=subprocess.run(['git','show','36c804af2:implementation/warlock/src/SurfaceRenderer.elm'],cwd=R,check=True,capture_output=True).stdout
  if hashlib.sha256(baseline).hexdigest()!='48e03f50fd509ea0e42e23d7a1aa26396122350ab824c8dc179952b5bfd28c63':raise RuntimeError('Baseline source differs')
  workspace=out/'workspace';workspace.mkdir();(workspace/'src').symlink_to(P/'src',target_is_directory=True);(workspace/'qa').mkdir();project=json.loads((P/'elm.json').read_text());project['source-directories']=['src','qa'];(workspace/'elm.json').write_text(json.dumps(project,indent=2)+'\n')
  for name in qa:
   if name.endswith('.elm'):shutil.copyfile(P/'qa'/name,workspace/'qa'/name)
  old=baseline.replace(b'module SurfaceRenderer exposing',b'module BaselineSurfaceRenderer exposing',1);(workspace/'qa/BaselineSurfaceRenderer.elm').write_bytes(old)
  home=out/'elm-home';shutil.copytree(H/m['elmHome'],home);env={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','SOURCE_DATE_EPOCH':'0','PYTHONDONTWRITEBYTECODE':'1','ELM_HOME':str(home),'GHCRTS':'-N1'}
  report.update(sources=sources,baselineRevision='36c804af2',baselineSHA256=hashlib.sha256(baseline).hexdigest(),renamedBaselineSHA256=hashlib.sha256(old).hexdigest(),heldFiles=held,compiler={'path':str(compiler),'sha256':sha(compiler)},node={'path':str(NODE),'sha256':sha(NODE)},inputValidation='passed before first compile')
  results={}
  for module in ['SurfaceSnapshotContracts','ThreeGroupReplay','OutputRetirementReplay']:
   bundle=out/(module+'.js');run('compile-'+module,[compiler,'make','qa/'+module+'.elm','--optimize','--output='+str(bundle)],workspace,env)
   if module=='SurfaceSnapshotContracts':
    raw=run('run-properties',[NODE,P/'qa/snapshot-contracts.cjs',bundle],workspace,env);result=json.loads(raw)
    if result.get('seed')!='0x5eed1234' or result.get('caseCount')!=221 or result.get('failures')!=[] or len(result.get('sequenceChecks',{}))!=15 or not all(result['sequenceChecks'].values()):raise RuntimeError('Property result incomplete or failed')
   else:
    runner=out/(module+'.cjs');runner.write_text((P/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.'+module));dest=out/(module+'.json');run('run-'+module,[NODE,runner,bundle,dest],workspace,env);result=json.loads(dest.read_text())
    if not result.get('checks') or not all(v is True for v in result['checks'].values()):raise RuntimeError(module+' assertions failed')
   results[module]=result
  check(sources);check(held)
  if {str(p) for p in (P/'src').rglob('*.elm')}!={p for p in built['sources'] if p.startswith(str(P/'src')+'/') and p.endswith('.elm')}:raise RuntimeError('Source inventory changed')
  report.update(passed=True,sources=sources,baselineRevision='36c804af2',baselineSHA256=hashlib.sha256(baseline).hexdigest(),renamedBaselineSHA256=hashlib.sha256(old).hexdigest(),heldFiles=held,compiler={'path':str(compiler),'sha256':sha(compiler)},node={'path':str(NODE),'sha256':sha(NODE)},results=results,outputs={str(p):sha(p) for p in out.iterdir() if p.is_file()})
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 report['outputs']={str(p):sha(p) for p in out.iterdir() if p.is_file()}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
