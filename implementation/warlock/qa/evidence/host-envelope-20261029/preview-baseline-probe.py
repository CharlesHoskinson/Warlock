#!/usr/bin/python3
"""Root-only protected build and run of actual shared-host admission witness."""
import hashlib,json,os,pathlib,resource,subprocess,sys,traceback
from pathlib import Path
R=Path('/home/charles/Warlock'); B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild'); D=Path(__file__).resolve().parent; O=D/'output'; REPORT=B/'arc004-build-terra2-v1/output/report.json'; OLD=B/'taskbar-host-rebuild-v1/output/report.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(m):
 for p,h in m.items():
  if sha(p)!=h: raise RuntimeError('input drift: '+str(p))
def main():
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1': raise RuntimeError('protected no-bytecode scope required')
 sys.path.insert(0,str(R/'window-integration-qa'));from qa_launch import require_qa_scope
 scope=require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1): raise RuntimeError('incorrect core limit')
 O.mkdir(exist_ok=False); result={'passed':False,'requirementAccepted':False,'nativeAcceptance':False,'scope':scope,'commands':[],'driverSHA256':sha(__file__)}
 env={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','SOURCE_DATE_EPOCH':'0','PYTHONDONTWRITEBYTECODE':'1'}
 def run(name,cmd):
  p=subprocess.run(list(map(str,cmd)),cwd=R,env=env,capture_output=True,timeout=120);out=O/(name+'.stdout');err=O/(name+'.stderr');out.write_bytes(p.stdout);err.write_bytes(p.stderr)
  result['commands'].append({'argv':list(map(str,cmd)),'exit':p.returncode,'stdoutSHA256':sha(out),'stderrSHA256':sha(err)})
  if p.returncode: raise RuntimeError(name+' failed; retained evidence')
 try:
  check({REPORT:'1c35c3c24cbc2011176affe84191f111bbc96caa4ea32a17ff737dd32f658ef6',OLD:'13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a'})
  new=json.loads(REPORT.read_text()); old=json.loads(OLD.read_text())
  if not new['passed'] or not old['passed']:raise RuntimeError('receipt not passed')
  shared='/home/charles/Warlock/implementation/warlock/native/shared-host.c'; expected_shared='add8a73915bf2dc3ee8b20516b8c7085a05fd518e7459385def8ec83cabb27cb'
  inputs={}
  for key in ('nativeSources','freshHostDeps','retainedObjects','linkedProviders'):
   values=dict(new[key])
   if shared in values: values[shared]=expected_shared
   check(values);inputs.update(values)
  result['inputs']=inputs
  for key in ('toolHashes','compilerSupportTools','freshDependenciesAfterCompile'): 
   values=dict(old[key]); host=str(R/'implementation/warlock/native/host.c')
   if host in values: values[host]=new['nativeSources'][host]
   if shared in values: values[shared]=expected_shared
   check(values)
  check(new['outputs']); check({D/'host-witness.c':'ab7092b04346d3097bc7f5c7632167b6165f59ac6672333029a199a3e3348b89'}); result['witnessSHA256']=sha(D/'host-witness.c')
  command=next(x['argv'] for x in new['commands'] if x['name']=='compile-shared-host'); compile_cmd=list(command)
  compile_cmd[compile_cmd.index('-MF')+1]=str(O/'host-witness.d'); compile_cmd[compile_cmd.index('-o')+1]=str(O/'host-witness.o'); compile_cmd[compile_cmd.index('-c')+1]=str(D/'host-witness.c')
  run('compile',compile_cmd)
  command=next(x['argv'] for x in new['commands'] if x['name']=='link-host'); link=list(command); link[1]=str(O/'host-witness.o');link[link.index('-o')+1]=str(O/'host-witness');run('link',link)
  result['binarySHA256']=sha(O/'host-witness');run('witness',[O/'host-witness']);check(inputs);result['passed']=True
 except Exception as e:result['error']=repr(e);result['traceback']=traceback.format_exc()
 (O/'report.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps({'passed':result['passed'],'report':str(O/'report.json')}));return 0 if result['passed'] else 1
if __name__=='__main__':sys.exit(main())
