#!/usr/bin/env python3
"""Protected actual-production shortcut editor baseline; preserves failure traces."""
import argparse,hashlib,json,os,resource,shutil,subprocess,sys,time,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[3];P=R/'implementation/warlock';H=R/'implementation/warlock-preview-provider-v143';B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild');NODE=Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def checked(p,h):
 raw=Path(p).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=h:raise RuntimeError('Input changed '+str(p))
 return raw
def check(rows):
 for p,h in rows.items():checked(p,h)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['baseline','candidate'],required=True);ap.add_argument('--build-report',type=Path);ap.add_argument('--build-sha256');args=ap.parse_args()
 if os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise RuntimeError('No-bytecode protected launch required')
 sys.path.insert(0,str(R/'window-integration-qa'));from qa_launch import require_qa_scope
 scope=require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('Core limit changed')
 out=B/('shortcut-draft-'+args.mode+'-'+str(time.time_ns()));out.mkdir(mode=0o700);report={'passed':False,'nativeAcceptance':False,'requirementAccepted':False,'mode':args.mode,'scope':scope,'commands':[],'driverSHA256':sha(__file__)}
 def run(name,argv,cwd,env):
  argv=list(map(str,argv));a=out/(name+'.stdout');b=out/(name+'.stderr')
  try:p=subprocess.run(argv,cwd=cwd,env=env,capture_output=True,timeout=240)
  except subprocess.TimeoutExpired as e:
   a.write_bytes(e.stdout or b'');b.write_bytes(e.stderr or b'');report['commands'].append({'name':name,'argv':argv,'cwd':str(cwd),'environment':env,'timedOut':True,'stdoutSHA256':sha(a),'stderrSHA256':sha(b)});raise
  a.write_bytes(p.stdout);b.write_bytes(p.stderr);report['commands'].append({'name':name,'argv':argv,'cwd':str(cwd),'environment':env,'exit':p.returncode,'stdoutSHA256':sha(a),'stderrSHA256':sha(b)})
  if p.returncode:raise RuntimeError(name+' failed')
  return p.stdout
 try:
  if args.mode=='baseline':checked(P/'src/ShortcutPreferences.elm','d9196adaae768e57e2531b78ad2cd8fd22a2a81ad952d27c7c88d0fc72da8322')
  else:
   if not args.build_report or not args.build_sha256:raise RuntimeError('Reviewed current three-root build receipt required')
   build=json.loads(checked(args.build_report,args.build_sha256))
   if not build.get('passed') or {c['module'] for c in build['commands']}!={'Main','Bar','Popup'} or any(c['exit'] for c in build['commands']):raise RuntimeError('Build did not pass all roots')
   check(build['sources']);report['buildReceipt']={'path':str(args.build_report),'sha256':args.build_sha256}
  m=json.loads(checked(H/'qa/toolchain.json','fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa'));held={str(H/q):v['sha256'] for q,v in m['heldFiles'].items()};check(held)
  compiler=H/m['compiler'];checked(compiler,'c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948');checked(NODE,'caa24debe02770c92a70677e2a62ca98890150e7ac1c17bcfe31bcc98cc89943')
  sources={str(q):sha(q) for q in (P/'src').glob('*.elm')};qa=['ShortcutDraftReplay.elm','NativePointerFixture.elm','feedback-replay.js']
  if args.mode=='candidate':qa+=['ShortcutPreferencesReplay.elm','ShortcutDraftProperties.elm','shortcut-draft-contracts.cjs']
  for name in qa:sources[str(P/'qa'/name)]=sha(P/'qa'/name)
  sources[str(P/'elm.json')]=sha(P/'elm.json');sources[str(Path(__file__).resolve())]=sha(__file__);check(sources)
  report.update(sources=sources,heldFiles=held,compiler={'path':str(compiler),'sha256':sha(compiler)},node={'path':str(NODE),'sha256':sha(NODE)},inputValidation='Current source hashes checked before and after execution; baseline source enforced only in baseline mode.')
  w=out/'workspace';w.mkdir();(w/'src').symlink_to(P/'src',target_is_directory=True);(w/'qa').mkdir();project=json.loads((P/'elm.json').read_text());project['source-directories']=['src','qa'];(w/'elm.json').write_text(json.dumps(project,indent=2)+'\n')
  for name in qa:
   if name.endswith('.elm'):shutil.copyfile(P/'qa'/name,w/'qa'/name)
  home=out/'elm-home';shutil.copytree(H/m['elmHome'],home);env={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','SOURCE_DATE_EPOCH':'0','PYTHONDONTWRITEBYTECODE':'1','ELM_HOME':str(home),'GHCRTS':'-N1'}
  bundle=out/'draft-replay.js';run('compile-draft',[compiler,'make','qa/ShortcutDraftReplay.elm','--optimize','--output='+str(bundle)],w,env)
  runner=out/'run-replay.cjs';runner.write_text((P/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.ShortcutDraftReplay'));dest=out/'draft-replay.json';run('run-draft',[NODE,runner,bundle,dest],w,env)
  result=json.loads(dest.read_text());report['result']=result;checks=result.get('checks',{});failures=[name for name,value in checks.items() if value is not True];expected={'sameRevisionRetainsDirty','reopenRetainsDirty','invalidInventoryKeepsIntentAndBlocksReady','changedRevisionKeepsLocalIntent','unknownMismatchStaysPending'}
  report.update(baselineWitnessValid=len(checks)==15 and set(failures)==expected,failedContracts=failures)
  if args.mode=='candidate':
   report['baselineWitnessValid']=None
   legacy=out/'legacy-replay.js';run('compile-legacy',[compiler,'make','qa/ShortcutPreferencesReplay.elm','--optimize','--output='+str(legacy)],w,env)
   legacyRunner=out/'run-legacy.cjs';legacyRunner.write_text((P/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.ShortcutPreferencesReplay'));legacyDest=out/'legacy-replay.json';run('run-legacy',[NODE,legacyRunner,legacy,legacyDest],w,env)
   legacyResult=json.loads(legacyDest.read_text());report['legacyResult']=legacyResult
   legacyChecks=legacyResult.get('checks',{})
   if len(legacyChecks)!=15 or any(v is not True for v in legacyChecks.values()):raise RuntimeError('Existing production replay regression')
   properties=out/'draft-properties.js';run('compile-properties',[compiler,'make','qa/ShortcutDraftProperties.elm','--optimize','--output='+str(properties)],w,env)
   propertyRaw=run('run-properties',[NODE,P/'qa/shortcut-draft-contracts.cjs',properties],w,env);propertiesResult=json.loads(propertyRaw);report['properties']=propertiesResult
   if propertiesResult['sequences']!=200 or propertiesResult['failures']:raise RuntimeError('Seeded production properties failed')
  check(sources);check(held)
  if {str(q) for q in (P/'src').glob('*.elm')}!={q for q in sources if q.startswith(str(P/'src')+'/')}:raise RuntimeError('Source inventory changed')
  if not checks or failures:raise RuntimeError('Production draft contracts fail; baseline retained')
  report['passed']=True
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 report['outputs']={str(p):sha(p) for p in out.iterdir() if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'baselineWitnessValid':report.get('baselineWitnessValid'),'report':str(out/'report.json'),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
