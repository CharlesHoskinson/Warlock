#!/usr/bin/env python3
"""Root-only protected CPU bridge diagnostic; no GUI or acceptance."""
import hashlib,json,os,pathlib,re,resource,shlex,shutil,subprocess,sys,time,traceback
R=pathlib.Path('/home/charles/Warlock');P=R/'implementation/warlock';H=R/'implementation/warlock-preview-provider-v143';D=pathlib.Path(__file__).resolve().parent
FIX=D/'same-stamp-realm-fixture.cpp';ROUND=D/'same-stamp-roundtrip.js'
PINS={FIX:'b9a6858ba309317bc69290562d9d626bd8d776030328102e68d67d3c800f9455',ROUND:'405928a0f871070cb5dae95cada3d0b655b4aa16edd9c2ecb44960951beb3744',H/'qa/toolchain.json':'fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa',H/'qa/policy-driver-realm-reuse-check-v3.py':'80d8b41f592d7e22926c193d750965ebda046f9b88f02676af37cae9d9971630',H/'qa/policy-driver-realm-reuse-roundtrip.js':'cec615b817b7b803b9e4801e51a6d6774ff178c1705995f2e56b96ae1ee0943a',P/'native/policy-driver-realm-reuse-fixture-v3.cpp':'db652a1be8a3450a7d3a5d75a7dcf46cb1e16501cc6ed6f45055f629c3857658',P/'native/capture-resource-fd-source-fixture.hpp':'88f8f0062bc4a26d237034752d1b2edbc3214e70878838a068de44f627de774c',P/'assets/native-preview-control-outbox.js':'183253d5f781cf8527c4e58f31d44653e1b6fe8be58c0bdc89ce4e3f5e4484'}
ASSET_REPORT=D.parent/'context-keyup-assets-v1/output/report.json'
HOST_REPORT=D.parent/'taskbar-host-rebuild-v1/output/report.json'
PINS[ASSET_REPORT]='69d5b85ad1137c3e851127c2cf5b4d9dcfe16f16e46568cbf106d2f165c77955'
PINS[HOST_REPORT]='13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a'
NODE=pathlib.Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node');NODE_SHA='caa24debe02770c92a70677e2a62ca98890150e7ac1c17bcfe31bcc98cc89943'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def check(path,digest):
 if sha(path)!=digest:raise RuntimeError('Pinned input changed: '+str(path))
def closure():
 pending=['NativePreviewPolicy'];seen={}
 while pending:
  name=pending.pop();path=P/'src'/('/'.join(name.split('.'))+'.elm')
  if not path.is_file() or name in seen:continue
  body=path.read_bytes();seen[name]=(path,hashlib.sha256(body).hexdigest())
  pending.extend(re.findall(r'^import\s+([A-Z][\w.]*)',body.decode(),re.M))
 return seen
def main():
 if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise SystemExit('No arguments; protected no-bytecode launcher only')
 sys.path.insert(0,str(R/'window-integration-qa'));from qa_launch import require_qa_scope
 require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('Core limit must remain (1,1)')
 run=D/('probe-'+str(time.time_ns()));run.mkdir(mode=0o700);report={'passed':False,'nativeAcceptance':False,'requirementAccepted':False,'fullReleaseAccepted':False,'actualWebKit':False,'clock':'monotonic modeled fixture source, not hardware time','commands':[]}
 def execute(name,argv,cwd,env,timeout=180):
  try:p=subprocess.run([str(x) for x in argv],cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout);code=p.returncode;out=p.stdout;err=p.stderr
  except subprocess.TimeoutExpired as e:
   code=None;out=(e.stdout or b'');err=(e.stderr or b'');out=out.decode(errors='replace') if isinstance(out,bytes) else out;err=err.decode(errors='replace') if isinstance(err,bytes) else err;err+='\noriginal command timeout\n'
  (run/(name+'.stdout')).write_text(out);(run/(name+'.stderr')).write_text(err);report['commands'].append({'name':name,'argv':[str(x) for x in argv],'cwd':str(cwd),'exitCode':code,'stdoutSHA256':sha(run/(name+'.stdout')),'stderrSHA256':sha(run/(name+'.stderr'))})
  if code!=0:raise RuntimeError(name+' failed; see retained output')
  return out
 try:
  for p,h in PINS.items():check(p,h)
  check(NODE,NODE_SHA);manifest=json.loads((H/'qa/toolchain.json').read_bytes());compiler=H/manifest['compiler'];check(compiler,'c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948')
  for name,item in manifest['heldFiles'].items():check(H/name,item['sha256'])
  old=closure();native=[P/'native'/n for n in ('preview-policy-driver.cpp','imported-clients.cpp','preview-provider-bootstrap.cpp','preview_uri.cpp','elm-preview-policy.cpp')]
  asset_receipt=json.loads(ASSET_REPORT.read_bytes());host_receipt=json.loads(HOST_REPORT.read_bytes())
  if not asset_receipt.get('passed') or not host_receipt.get('passed'):raise RuntimeError('Qualified build receipts not passed')
  for path,digest in old.values():
   if asset_receipt['sourceAfter'].get(str(path))!=digest:raise RuntimeError('Policy source differs from current asset receipt: '+str(path))
  if asset_receipt['sourceAfter'].get(str(P/'elm.json'))!=sha(P/'elm.json'):raise RuntimeError('Elm config differs from receipt')
  native_current={str(path):sha(path) for path in sorted((P/'native').rglob('*')) if path.is_file()}
  if host_receipt['nativeSourcesAfter']!=native_current:raise RuntimeError('Native input inventory differs from qualified receipt')
  inputs={str(path):digest for path,digest in old.values()};inputs[str(P/'elm.json')]=sha(P/'elm.json')
  for path in sorted((P/'native').glob('*')):
   if path.is_file():inputs[str(path)]=sha(path)
  inputs.update({str(p):sha(p) for p in PINS});report['inputs']=inputs
  work=run/'work';(work/'src').mkdir(parents=True);shutil.copy2(P/'elm.json',work/'elm.json')
  for path,_ in old.values():
   target=work/'src'/path.relative_to(P/'src');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
  home=run/'elm-home';shutil.copytree(H/manifest['elmHome'],home,symlinks=False)
  env=dict(os.environ,ELM_HOME=str(home),PYTHONDONTWRITEBYTECODE='1',LC_ALL='C',TZ='UTC');policy=run/'native-preview-policy.js'
  execute('elm-policy',[compiler,'make','src/NativePreviewPolicy.elm','--optimize','--output='+str(policy)],work,env)
  pkg=pathlib.Path('/usr/bin/pkg-config');cxx=pathlib.Path('/usr/bin/g++');report['tools']={str(p.resolve()):sha(p.resolve()) for p in (pkg,cxx,NODE,compiler)}
  flags=shlex.split(execute('pkg-config',[pkg,'--cflags','--libs','gio-unix-2.0','json-glib-1.0','javascriptcoregtk-4.1'],work,env));objs=[];deps={}
  for i,unit in enumerate([FIX,*native]):
   obj=run/('unit-'+str(i)+'.o');dep=run/('unit-'+str(i)+'.d')
   argv=[cxx,'-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(P/'native'),'-MD','-MF',dep,'-c',unit,'-o',obj,*flags]
   execute('compile-'+str(i),argv,work,env);objs.append(obj)
   body=dep.read_text().replace('\\\n',' ');parts=shlex.split(body.split(':',1)[1]);deps.update({str(pathlib.Path(x).resolve()):sha(pathlib.Path(x).resolve()) for x in parts})
  binary=run/'driver';execute('link',[cxx,'-fsanitize=address,undefined','-fno-omit-frame-pointer',*objs,'-o',binary,*flags],work,env);report['dependencySHA256']=deps
  linked=execute('linked-providers',['/usr/bin/ldd',binary],work,env);report['linkedProviders']={}
  for line in linked.splitlines():
   if 'not found' in line:raise RuntimeError('Missing linked provider')
   match=re.search(r'(?:=>\s*)?(/\S+)\s+\(',line)
   if match:
    provider=pathlib.Path(match.group(1)).resolve();report['linkedProviders'][str(provider)]=sha(provider)
  if not report['linkedProviders']:raise RuntimeError('No linked providers observed')
  failures=[]
  for side in ('near','expired'):
   try:
    stdout=execute('trace-'+side,[NODE,ROUND,binary,policy,P/'assets/native-preview-control-outbox.js',side],run,env);report[side]=json.loads(stdout.strip().splitlines()[-1])
   except Exception as error:failures.append({'side':side,'error':repr(error)})
  report['traceFailures']=failures
  if any(sha(pathlib.Path(k))!=v for k,v in {**inputs,**deps}.items()):raise RuntimeError('Source/dependency changed during run')
  report['artifacts']={str(p):sha(p) for p in run.iterdir() if p.is_file()};report['passed']=not failures
 except BaseException as error:report['error']=repr(error);report['traceback']=traceback.format_exc()
 (run/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(run/'report.json')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
