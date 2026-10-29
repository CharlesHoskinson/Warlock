#!/usr/bin/env python3
"""Root-only protected Elm decoder observation; retains failed oracle results."""
import hashlib,json,os,pathlib,resource,shutil,subprocess,sys,time,traceback
R=pathlib.Path('/home/charles/Warlock'); P=R/'implementation/warlock'; H=R/'implementation/warlock-preview-provider-v143'; D=pathlib.Path(__file__).resolve().parent
NODE=pathlib.Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1': raise RuntimeError('protected no-bytecode run required')
 sys.path.insert(0,str(R/'window-integration-qa')); from qa_launch import require_qa_scope
 require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1): raise RuntimeError('core limit differs')
 run=D/('run-'+str(time.time_ns())); run.mkdir(mode=0o700); report={'passed':False,'requirementAccepted':False,'nativeAcceptance':False,'commands':[]}
 try:
  pins=json.loads((D/'pins.json').read_text())
  for name,sha in pins['files'].items():
   if digest(pathlib.Path(name))!=sha: raise RuntimeError('input drift: '+name)
  tool=json.loads((H/'qa/toolchain.json').read_text()); compiler=H/tool['compiler']
  for name,item in tool['heldFiles'].items():
   if digest(H/name)!=item['sha256']: raise RuntimeError('held cache drift: '+name)
  work=run/'work'; (work/'src').mkdir(parents=True)
  for name in pins['modules']:
   src=P/'src'/name; dst=work/'src'/name; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
  shutil.copy2(D/'DecoderReplay.elm',work/'src/DecoderReplay.elm')
  (work/'elm.json').write_text(json.dumps({'type':'application','source-directories':['src'],'elm-version':'0.19.2','dependencies':{'direct':{'elm/core':'1.0.5','elm/json':'1.1.3'},'indirect':{}},'test-dependencies':{'direct':{},'indirect':{}}}))
  home=run/'elm-home'; shutil.copytree(H/tool['elmHome'],home)
  env=dict(os.environ,ELM_HOME=str(home),LC_ALL='C',TZ='UTC',PYTHONDONTWRITEBYTECODE='1')
  for name,argv in [('compile',[str(compiler),'make','src/DecoderReplay.elm','--optimize','--output='+str(run/'decoder.js')]),('replay',[str(NODE),str(D/'replay.js'),str(run/'decoder.js')])]:
   p=subprocess.run(argv,cwd=work,env=env,capture_output=True,timeout=120)
   (run/(name+'.stdout')).write_bytes(p.stdout); (run/(name+'.stderr')).write_bytes(p.stderr)
   report['commands'].append({'argv':argv,'cwd':str(work),'exit':p.returncode,'stdoutSHA256':digest(run/(name+'.stdout')),'stderrSHA256':digest(run/(name+'.stderr'))})
   if p.returncode: raise RuntimeError(name+' failed; retained output')
  report['result']=json.loads((run/'replay.stdout').read_text()); report['sourceHashes']=pins['files']; report['pinsSHA256']=digest(D/'pins.json')
  for name,sha in pins['files'].items():
   if digest(pathlib.Path(name))!=sha: raise RuntimeError('input changed during run: '+name)
  report['passed']=True
 except BaseException as e: report['error']=repr(e); report['traceback']=traceback.format_exc()
 (run/'report.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps({'report':str(run/'report.json'),'passed':report['passed']})); return 0 if report['passed'] else 1
if __name__=='__main__': sys.exit(main())
