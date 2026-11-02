import hashlib,json,os,re,resource,subprocess,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parent
QA=Path('/home/charl/warlock-live-usability-typed-model-20261102T000451Z/qa-mocks')
EXPECTED_MANIFEST='c73504f1804bb48204d0e9b906abc5d67ac6c9a460f7c12fbbdcf430e991b4b3'
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope

def digest(p):
 with Path(p).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def pin(p):
 p=Path(p);s=p.stat()
 return dict(path=str(p),resolvedPath=str(p.resolve()),device=str(s.st_dev),inode=str(s.st_ino),size=str(s.st_size),sha256=digest(p))
def require(ok,why):
 if not ok:raise RuntimeError(why)
def main():
 os.umask(0o077);scope=require_qa_scope();require(resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'core1')
 require(digest(BASE/'qa-manifest.json')==EXPECTED_MANIFEST,'manifest changed')
 manifest=json.loads((BASE/'qa-manifest.json').read_text())
 def inputs():
  for name,sha in manifest['qaInputs'].items():
   p=BASE/name;require(p.is_file() and not p.is_symlink() and digest(p)==sha,'input changed:'+name)
 inputs();logs=BASE/'logs';logs.mkdir(mode=0o700);report=dict(schema=1,passed=False,scope=scope,core=[1,1],sourceManifestSHA256=EXPECTED_MANIFEST,commands=[],variants={},nativeAccepted=False,releaseAccepted=False)
 env={'PATH':'/usr/bin:/bin','HOME':'/home/charl','LANG':'C','LC_ALL':'C','GHC_ENVIRONMENT':'-','CABAL_DIR':'/home/charl/warlock-mvp-20261101T1058Z/build-dynamic/cabal-home'}
 def run(label,argv,cwd,expected=0,timeout=120):
  started=time.monotonic();forced=False
  with (logs/(label+'.stdout')).open('xb') as out,(logs/(label+'.stderr')).open('xb') as err:
   try:r=subprocess.run(argv,cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,timeout=timeout,check=False);code=r.returncode
   except subprocess.TimeoutExpired:forced=True;code=None
  row=dict(label=label,argv=argv,exit=code,expected=expected,forced=forced,elapsedSeconds=time.monotonic()-started,stdoutSHA256=digest(logs/(label+'.stdout')),stderrSHA256=digest(logs/(label+'.stderr')));report['commands'].append(row)
  require(not forced and code==expected,label+' unexpected exit/timeout');return (logs/(label+'.stdout')).read_text()
 try:
  report['tools']={name:pin('/usr/bin/'+name) for name in ['ghc','hsc2hs','cabal','python3','readelf','ldd']}
  run('versions',['/usr/bin/cabal','--version'],BASE)
  for name in ['red','green','full']:
   work=BASE/name;target='store-settled-controls' if name=='full' else 'acquisition-failure-controls';package='warlock-store-retirement-qa' if name=='full' else 'warlock-store-acquisition-witness'
   common=['/usr/bin/cabal','--config-file=/home/charl/warlock-mvp-20261101T1058Z/build-dynamic/cabal.config']
   options=['--offline','--project-file='+str(work/'cabal.project'),'--builddir='+str(BASE/'build'/name),'--with-compiler=/usr/bin/ghc','--with-hsc2hs=/usr/bin/hsc2hs','--enable-executable-dynamic','--jobs=2']
   run(name+'-build',common+['build']+options+[package+':exe:'+target],work)
   raw=run(name+'-list-bin',common+['list-bin','--offline','--project-file='+str(work/'cabal.project'),'--builddir='+str(BASE/'build'/name),package+':exe:'+target],work)
   paths=raw.splitlines();require(len(paths)==1,'one executable expected');image=Path(paths[0]);require(image.is_relative_to(BASE/'build'/name) and image.is_file() and not image.is_symlink(),'unowned binary');imagepin=pin(image)
   dynamic=run(name+'-readelf',['/usr/bin/readelf','-d',str(image)],work,timeout=10)
   linked=run(name+'-ldd',['/usr/bin/ldd',str(image)],work,timeout=10);require('not found' not in linked,'unresolved dependency')
   deps=set(re.findall(r'=> (/[^\s]+)',linked));deps.update(re.findall(r'^\s*(/[^\s]+)\s+\(',linked,re.M));require(deps,'dependencies absent');before={p:pin(p) for p in sorted(deps)}
   args=[str(image)]
   if name=='full':
    private=BASE/'fresh-owned-files';private.mkdir(mode=0o700);args.append(str(private))
   output=run(name+'-execute',args,work,expected=manifest['variants'][name]['expectedExecutionExit'],timeout=10)
   observed=None
   if name!='full':
    lines=output.splitlines();require(len(lines)==1,'one raw witness expected');observed=json.loads(lines[0]);require(observed['acquisitionEvents']==1 and observed['bodyCalls']==0 and observed['releaseCalls']==0 and observed['retryBodyCalls']==0,'literal event counts')
    require(observed['retireStoreOwnerResult']==(name=='red') and observed['retainedRecordsBeforeRetirement']==(0 if name=='red' else 1),'actual old/new retirement')
    require(observed['passed']==(name=='green'),'actual witness verdict');require(all(v is True for k,v in observed['checks'].items() if k!='actualRetireStoreOwnerIsUnconfirmed'),'unrelated witness failure')
   else:require(output.strip()=='Store acquisition/publication and settled-only controls passed','full controls marker')
   require(pin(image)==imagepin and {p:pin(p) for p in sorted(deps)}==before,'artifact/dependencies changed')
   inputs();report['variants'][name]=dict(image=imagepin,dependencies=before,observed=observed,expectedExit=manifest['variants'][name]['expectedExecutionExit'],passed=True)
  report['passed']=True
 except BaseException as error:report['error']=type(error).__name__+': '+str(error)
 finally:
  report['finishedMonotonic']=time.monotonic();(BASE/'store-controls-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['passed','nativeAccepted','releaseAccepted']}),flush=True)
 return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
