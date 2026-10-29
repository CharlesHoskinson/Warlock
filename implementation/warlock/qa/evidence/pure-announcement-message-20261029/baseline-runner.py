#!/usr/bin/env python3
"""Protected announcement encoder differential and existing policy replays."""
import hashlib,json,os,resource,shutil,subprocess,sys,time,traceback
from pathlib import Path
R=Path('/home/charles/Warlock');P=R/'implementation/warlock';H=R/'implementation/warlock-preview-provider-v143';B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild');NODE=Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node')
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
 out=B/('announcement-policy-baseline-'+str(time.time_ns()));out.mkdir(mode=0o700)
 report={'passed':False,'nativeAcceptance':False,'requirementAccepted':False,'scope':scope,'commands':[],'seed':'0x0a110c10','generatedEncoderCaseBudget':200,'shrinking':'No shrinker; complete failing inputs and sequence are retained.','driverSHA256':sha(__file__)}
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
  built=json.loads(checked(B/'announcement-message-build-root-v1/output/report.json','aa73031b7642dba0433247f5d78f969938fcf9038fbb63d27fb6e538904fd449'))
  if not built['passed']:raise RuntimeError('Current roots not built')
  sources=dict(built['sources']);qa=['AnnouncementMessageContracts.elm','announcement-message-contracts.cjs','AnnouncementReplay.elm','NotificationAnnouncementReplay.elm','SnapReplay.elm','NativePointerFixture.elm','feedback-replay.js']
  for name in qa:sources[str(P/'qa'/name)]=sha(P/'qa'/name)
  sources[str(Path(__file__).resolve())]=sha(__file__);check(sources)
  held={str(H/name):v['sha256'] for name,v in m['heldFiles'].items()};check(held)
  compiler=H/m['compiler'];checked(compiler,'c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948');checked(NODE,'caa24debe02770c92a70677e2a62ca98890150e7ac1c17bcfe31bcc98cc89943')
  baseline=subprocess.run(['git','show','abe216442:implementation/warlock/src/Announcement.elm'],cwd=R,check=True,capture_output=True).stdout
  if hashlib.sha256(baseline).hexdigest()!='71bc1e29724266c26301716ea0a1c7452f02c9f67e140e1bd1ec33c5166d402f':raise RuntimeError('Baseline source differs')
  workspace=out/'workspace';workspace.mkdir();(workspace/'src').mkdir();(workspace/'qa').mkdir();project=json.loads((P/'elm.json').read_text());project['source-directories']=['src','qa'];(workspace/'elm.json').write_text(json.dumps(project,indent=2)+'\n')
  overrides={'Announcement.elm':'71bc1e29724266c26301716ea0a1c7452f02c9f67e140e1bd1ec33c5166d402f','OutcomeAnnouncements.elm':'158b22f574983da656838c4388c93cca1c7d9b044aaae83ee21153eae29b7586'}
  baselineInputs={}
  for source in (P/'src').glob('*.elm'):
   target=workspace/'src'/source.name
   if source.name in overrides:
    raw=subprocess.run(['git','show','abe216442:implementation/warlock/src/'+source.name],cwd=R,check=True,capture_output=True).stdout
    if hashlib.sha256(raw).hexdigest()!=overrides[source.name]:raise RuntimeError('Original baseline source differs '+source.name)
    target.write_bytes(raw)
   else:target.symlink_to(source)
   baselineInputs[str(target)]=sha(target)
  report.update(scopeDescription='Same production notification replay with exact two pre-extraction source overrides; all other sources current and unchanged',baselineOverrides=overrides,baselineAvailableSourceInventory=baselineInputs,originalRevision='abe216442',policyAcceptance=False)
  for name in qa:
   if name.endswith('.elm'):shutil.copyfile(P/'qa'/name,workspace/'qa'/name)
  old=baseline.replace(b'module Announcement exposing',b'module BaselineAnnouncement exposing',1);(workspace/'qa/BaselineAnnouncement.elm').write_bytes(old)
  home=out/'elm-home';shutil.copytree(H/m['elmHome'],home);env={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','SOURCE_DATE_EPOCH':'0','PYTHONDONTWRITEBYTECODE':'1','ELM_HOME':str(home),'GHCRTS':'-N1'}
  report.update(sources=sources,baselineRevision='abe216442',baselineSHA256=hashlib.sha256(baseline).hexdigest(),renamedBaselineSHA256=hashlib.sha256(old).hexdigest(),heldFiles=held,compiler={'path':str(compiler),'sha256':sha(compiler)},node={'path':str(NODE),'sha256':sha(NODE)},inputValidation='passed before first compile')
  results={}
  for module in ['NotificationAnnouncementReplay']:
   bundle=out/(module+'.js');run('compile-'+module,[compiler,'make','qa/'+module+'.elm','--optimize','--output='+str(bundle)],workspace,env)
   if module=='AnnouncementMessageContracts':
    raw=run('run-properties',[NODE,P/'qa/announcement-message-contracts.cjs',bundle],workspace,env);result=json.loads(raw)
    if result.get('seed')!='0x0a110c10' or result.get('generated')!=200 or result.get('caseCount')!=216 or result.get('positiveCounters')!=['0','1','9007199254740992','9007199254740993','18446744073709551615'] or result.get('failures')!=[]:raise RuntimeError('Property result incomplete or failed')
   else:
    runner=out/(module+'.cjs');runner.write_text((P/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.'+module));dest=out/(module+'.json');run('run-'+module,[NODE,runner,bundle,dest],workspace,env);result=json.loads(dest.read_text())
    report['observedBaselineChecks']=result.get('checks',{})
    if not result.get('checks') or not all(v is True for v in result['checks'].values()):raise RuntimeError(module+' assertions failed')
   results[module]=result
  check(sources);check(held)
  if {str(p) for p in (P/'src').rglob('*.elm')}!={p for p in built['sources'] if p.startswith(str(P/'src')+'/') and p.endswith('.elm')}:raise RuntimeError('Source inventory changed')
  report.update(passed=True,sources=sources,baselineRevision='abe216442',baselineSHA256=hashlib.sha256(baseline).hexdigest(),renamedBaselineSHA256=hashlib.sha256(old).hexdigest(),heldFiles=held,compiler={'path':str(compiler),'sha256':sha(compiler)},node={'path':str(NODE),'sha256':sha(NODE)},results=results,outputs={str(p):sha(p) for p in out.iterdir() if p.is_file()})
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 report['caseScope']='No encoder or randomized cases run in this baseline; only NotificationAnnouncementReplay executes.'
 report['outputs']={str(p):sha(p) for p in out.iterdir() if p.is_file()}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
