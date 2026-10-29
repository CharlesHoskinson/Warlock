#!/usr/bin/python3
"""Protected focused compilation of current original launcher-policy witnesses."""
import hashlib,importlib.util,json,os,resource,shutil,subprocess,sys,traceback
from pathlib import Path
R=Path('/home/charles/Warlock');P=R/'implementation/warlock';H=R/'implementation/warlock-preview-provider-v143';OUT=Path(__file__).resolve().parent/'output-v2'
sys.path.insert(0,str(R/'window-integration-qa'));from qa_launch import require_qa_scope
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1);OUT.mkdir(exist_ok=False)
 report={'passed':False,'nativeAcceptance':False,'requirementAccepted':False,'scope':'Current compiled policy and state projection; no native presentation, input or AT acceptance','protectedScope':scope,'driverSHA256':sha(__file__),'commands':[]}
 try:
  paths=sorted((P/'src').rglob('*.elm'))+sorted((P/'qa').glob('*.elm'))+[P/'elm.json',P/'qa/feedback-replay.js']
  assert not any(p.is_symlink() for p in paths)
  before={str(p):sha(p) for p in paths};report['sourcesBefore']=before
  spec=importlib.util.spec_from_file_location('held_search_toolchain',H/'qa/toolchain.py');toolchain=importlib.util.module_from_spec(spec);spec.loader.exec_module(toolchain);pinned=toolchain.verify()
  compiler=H/pinned['compiler'];report['compilerSHA256']=sha(compiler);assert report['compilerSHA256']=='c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948'
  workspace=OUT/'workspace';workspace.mkdir();(workspace/'src').symlink_to(P/'src',target_is_directory=True);(workspace/'qa').symlink_to(P/'qa',target_is_directory=True)
  config=json.loads((P/'elm.json').read_text());config['source-directories']=['src','qa'];(workspace/'elm.json').write_text(json.dumps(config))
  shutil.copytree(H/pinned['elmHome'],OUT/'elm-home');env={**os.environ,'ELM_HOME':str(OUT/'elm-home'),'PYTHONDONTWRITEBYTECODE':'1'}
  def run(name,args):
   proc=subprocess.run([str(x) for x in args],cwd=workspace,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
   for stream,data in [('stdout',proc.stdout),('stderr',proc.stderr)]: (OUT/(name+'.'+stream)).write_bytes(data)
   report['commands'].append({'name':name,'argv':[str(x) for x in args],'exit':proc.returncode,'stdoutSHA256':sha(OUT/(name+'.stdout')),'stderrSHA256':sha(OUT/(name+'.stderr'))})
   assert proc.returncode==0,(name,proc.returncode)
  run('compile',[compiler,'make','qa/SearchReplay.elm','--optimize','--output='+str(OUT/'search.js')])
  node=(P/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.SearchReplay');(OUT/'replay.js').write_text(node)
  nodeExecutable=Path(shutil.which('node')).resolve(strict=True);report['node']={'path':str(nodeExecutable),'sha256':sha(nodeExecutable)}
  run('replay',[nodeExecutable,OUT/'replay.js',OUT/'search.js',OUT/'replay.json']);assert sha(nodeExecutable)==report['node']['sha256']
  rows=json.loads((OUT/'replay.json').read_text());report['observations']=rows
  assert rows['rank']==['z-exact','a-prefix','b-token'] and rows['keyword']==['z-exact'] and rows['generic']==['b-token','z-exact'] and rows['unicode']==['c-unicode']
  assert rows['refreshClearsSettledRefusal'] and rows['refreshPreservesUnknown'] and rows['queryEditHasNoEffects'] and rows['staleQueryRejected']
  assert 'No matching' in rows['noMatchStatus'] and rows['queryRetained']=='nonexistent'
  checks=rows['policyChecks'];assert checks and all(type(v)is bool and v for v in checks.values());report['checks']=checks
  report['sourcesAfter']={str(p):sha(p) for p in paths};assert report['sourcesAfter']==before;toolchain.verify();assert sha(__file__)==report['driverSHA256'];report['passed']=True
 except Exception as e: report['error']=repr(e);(OUT/'failure.txt').write_text(traceback.format_exc())
 finally:(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}))
 if not report['passed']:raise SystemExit(1)
if __name__=='__main__':main()
