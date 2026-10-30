#!/usr/bin/env python3
"""Protected current notification admission regression; never native acceptance."""
import hashlib,json,os,resource,shutil,subprocess,sys,time,traceback
from pathlib import Path
R=Path('/home/charles/Warlock');P=R/'implementation/warlock';H=R/'implementation/warlock-preview-provider-v143';B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 sys.path.insert(0,str(R/'window-integration-qa'))
 from qa_launch import require_qa_scope
 scope=require_qa_scope()
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise RuntimeError('Protected no-argument no-bytecode required')
 out=B/('notification-admission-'+str(time.time_ns()));out.mkdir(mode=0o700)
 report={'passed':False,'nativeAcceptance':False,'requirementAccepted':False,'scope':scope,'commands':[]}
 def run(name,argv,cwd,env):
  argv=list(map(str,argv));a=out/(name+'.stdout');b=out/(name+'.stderr')
  try:p=subprocess.run(argv,cwd=cwd,env=env,capture_output=True,timeout=240)
  except subprocess.TimeoutExpired as e:
   a.write_bytes(e.stdout or b'');b.write_bytes(e.stderr or b'');report['commands'].append({'name':name,'argv':argv,'exit':None,'timedOut':True});raise
  a.write_bytes(p.stdout);b.write_bytes(p.stderr);report['commands'].append({'name':name,'argv':argv,'cwd':str(cwd),'exit':p.returncode,'stdoutSHA256':sha(a),'stderrSHA256':sha(b)})
  if p.returncode:raise RuntimeError(name+' failed')
  return p.stdout.decode()
 try:
  tool=H/'qa/toolchain.json';assert sha(tool)=='fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa';m=json.loads(tool.read_text())
  inputs={str(p):sha(p) for p in (P/'src').rglob('*.elm')}
  extra=['elm.json','qa/NotificationAnnouncementReplay.elm','qa/feedback-replay.js','qa/notification-announcements.qnt','qa/notification-announcements_test.qnt','qa/evidence/pure-announcement-message-20261029/notification-baseline.json','qa/evidence/pure-announcement-message-20261029/notification-current.json']
  inputs.update({str(P/n):sha(P/n) for n in extra});inputs[str(Path(__file__).resolve())]=sha(__file__)
  held={str(H/n):v['sha256'] for n,v in m['heldFiles'].items()}
  def check():
   for n,h in {**inputs,**held}.items():assert sha(n)==h,n
   assert {str(p) for p in (P/'src').rglob('*.elm')}=={n for n in inputs if n.startswith(str(P/'src')+'/')}
  check();compiler=H/m['compiler'];assert sha(compiler)==m['compilerSHA256']
  node=Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node');assert sha(node)=='caa24debe02770c92a70677e2a62ca98890150e7ac1c17bcfe31bcc98cc89943'
  quint=Path('/home/charles/.local/bin/quint').resolve()
  report.update(inputs=inputs,heldFiles=held,tools={str(p):sha(p) for p in [compiler,node,quint]},baselineSourceRevision='8a26e3ac1',inputValidation='passed before compilation')
  work=out/'workspace';(work/'src').mkdir(parents=True);(work/'qa').mkdir()
  for p in (P/'src').rglob('*.elm'):
   target=work/'src'/p.relative_to(P/'src');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
  project=json.loads((P/'elm.json').read_text());project['source-directories']=['src','qa'];(work/'elm.json').write_text(json.dumps(project,indent=2)+'\n')
  for n in extra:
   if n.startswith('qa/') and '/evidence/' not in n:shutil.copyfile(P/n,work/n)
  home=out/'elm-home';shutil.copytree(H/m['elmHome'],home)
  env=dict(os.environ);env.update(LC_ALL='C',TZ='UTC',SOURCE_DATE_EPOCH='0',PYTHONDONTWRITEBYTECODE='1',ELM_HOME=str(home),GHCRTS='-N1');report['environment']={n:env[n] for n in ['PATH','LC_ALL','TZ','SOURCE_DATE_EPOCH','PYTHONDONTWRITEBYTECODE','ELM_HOME','GHCRTS']}
  bundle=out/'notification.js';run('compile',[compiler,'make','qa/NotificationAnnouncementReplay.elm','--optimize','--output='+str(bundle)],work,env)
  replay=out/'replay.cjs';replay.write_text((P/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.NotificationAnnouncementReplay'))
  result=out/'notification.json';run('replay',[node,replay,bundle,result],work,env);current=json.loads(result.read_text())
  old=json.loads((P/extra[-1]).read_text());base=json.loads((P/extra[-2]).read_text());assert old==base,'Retained baseline/current mismatch'
  failures=[n for n,v in old['checks'].items() if v is not True];assert len(failures)==6,failures
  assert len(current['checks'])==24 and set(old['checks'])<=set(current['checks']);assert all(v is True for v in current['checks'].values()),current['checks']
  assert current['notificationFrame']['frame']['mode']=='notifications',current['notificationFrame']
  report.update(baselineFailures=failures,originalChecks=14,currentChecks=24,result=str(result),resultSHA256=sha(result))
  run('quint-version',[quint,'--version'],work,env)
  run('model-typecheck',[quint,'typecheck','qa/notification-announcements.qnt'],work,env)
  run('tests-typecheck',[quint,'typecheck','qa/notification-announcements_test.qnt'],work,env)
  output=run('named-tests',[quint,'test','qa/notification-announcements_test.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79501'],work,env)
  import re
  assert re.search(r'10 passing',output),output
  witnesses=['arrivalWitness','suppressedWitness','politeCriticalWitness','interruptWitness','dndWitness','optInWitness','repeatWitness','baselineWitness']
  output=run('safety-witnesses',[quint,'run','qa/notification-announcements.qnt','--backend=typescript','--invariants=safety','--witnesses',*witnesses,'--max-samples=1000','--max-steps=30','--seed=79502'],work,env)
  counts={n:int(c) for n,c in re.findall(r'(\w+Witness) was witnessed in (\d+) trace',output)}
  assert set(counts)==set(witnesses) and all(counts.values()),counts
  check();report.update(passed=True,witnesses=counts,modelLimits='Finite notification history/policy abstraction; no pointer admission, native speech/braille, AT export, native focus/input, lifetime/resource or release proof.')
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 report['outputs']={str(p.relative_to(out)):sha(p) for p in out.iterdir() if p.is_file()}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
