#!/usr/bin/env python3
"""Fixed private public-reducer probe. Root protected execution only."""
from pathlib import Path
import hashlib, importlib.util, json, os, shutil, signal, subprocess, sys, time
R=Path('/home/hoskinson/Projects/Warlock');HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def main():
 require(len(sys.argv)==3 and sys.argv[1]=='--manifest-sha256','fixed manifest hash argument required')
 mp=HERE/'manifest.json';require(sha(mp)==sys.argv[2],'manifest changed');manifest=json.loads(mp.read_text())
 sys.dont_write_bytecode=True;sys.path[:0]=[str(R/'window-integration-qa'),str(R/'tools')]
 from qa_launch import require_qa_scope
 require_qa_scope()
 started=time.monotonic();end=started+120
 def verify():
  for item in manifest['files']:require(sha(item['path'])==item['sha256'],'private fixture/source changed')
  for path,pin in manifest['sourcePins'].items():require(sha(R/path)==pin,'current source changed: '+path)
  actual={str(p.relative_to(R))for p in (R/'implementation/warlock/src').rglob('*.elm')}
  require(actual==set(manifest['productionElmFiles']),'full production Elm membership changed')
 verify();spec=importlib.util.spec_from_file_location('watch_batch_probe_elm',R/'tools/check_elm_cpu.py');elm=importlib.util.module_from_spec(spec);spec.loader.exec_module(elm);profile=elm.verify_menu_tab_toolchain()
 from arm64_toolchain import inventory
 out=HERE/('actual-root-probe-'+str(time.time_ns()));out.mkdir(mode=0o700);work=out/'work';(work/'src').mkdir(parents=True);(work/'qa').mkdir()
 report={'schema':1,'passed':False,'classification':'not-started','nativeAcceptance':False,'originalAcceptance':False,'assistiveTechnologyAcceptance':False,'sourceInputsUnchanged':False,'cleanupQualified':False,'commands':[],'manifestSha256':sys.argv[2],'sourceHashes':manifest['sourcePins']}
 child=None
 try:
  for relative in manifest['productionElmFiles']+['implementation/warlock/qa/OutputRetirementReplay.elm']:
   source=R/relative;target=work/source.relative_to(R/'implementation/warlock');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);require(sha(source)==sha(target),'stage differs')
  for name in ('Ui011WindowWatchBatchReplay.elm','ui011-window-watch-batch.cjs'):shutil.copyfile(HERE/name,work/'qa'/name)
  config=json.loads((R/'implementation/warlock/elm.json').read_text());config['source-directories']=['src','qa'];(work/'elm.json').write_text(json.dumps(config))
  shutil.copytree(profile['elmHome'],out/'elm-home');require(inventory(out/'elm-home')==profile['trees'][profile['elmHome']],'staged Elm cache differs')
  env=dict(os.environ,ELM_HOME=str(out/'elm-home'),NO_COLOR='1');[env.pop(key,None)for key in ('NODE_OPTIONS','NODE_PATH','FORCE_COLOR')]
  image=out/'Ui011WindowWatchBatchReplay.js';result=out/'window-watch-batch.json'
  commands=[('compile',[profile['elm'],'make','qa/Ui011WindowWatchBatchReplay.elm','--optimize','--output='+str(image)]),('public-reducer',[profile['node'],str(work/'qa/ui011-window-watch-batch.cjs'),str(image),str(result)])]
  for label,argv in commands:
   remaining=end-time.monotonic();require(remaining>0,'original private120s budget exhausted')
   with (out/(label+'.stdout')).open('wb')as stdout,(out/(label+'.stderr')).open('wb')as stderr:
    child=subprocess.Popen(argv,cwd=work,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
    try:code=child.wait(timeout=min(90,remaining))
    except subprocess.TimeoutExpired:
     os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=2);raise
   report['commands'].append({'label':label,'argv':argv,'exit':code});child=None
   if code:break
  verify();require(elm.verify_menu_tab_toolchain()==profile,'toolchain/cache changed');report['sourceInputsUnchanged']=True;report['cleanupQualified']=True
  if result.exists():report['result']=json.loads(result.read_text());report['resultRef']={'path':str(result),'sha256':sha(result)}
  report['classification']=report.get('result',{}).get('classification','compile-or-setup-failed')
  report['passed']=len(report['commands'])==2 and all(row['exit']==0 for row in report['commands'])and report.get('result',{}).get('passed')is True
 except Exception as error:
  report['passed']=False;report['error']=str(error)[:2048]
 finally:
  if child is not None and child.poll()is None:
   os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=2)
  (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'path':str(out/'report.json'),'sha256':sha(out/'report.json'),'passed':report['passed']}));return 0 if report['passed']else 1
if __name__=='__main__':raise SystemExit(main())
