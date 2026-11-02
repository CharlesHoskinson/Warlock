import hashlib,json,os,re,resource,subprocess,sys,time,uuid
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,'/home/charl/warlock-live-usability-typed-model-20261102T000451Z/qa-mocks')
from qa_launch import require_qa_scope
EXPECTED='c96e6ed77321ddcf0b08328c54640c98763d57e29136e2059af6e6ed580cbfc9'
def digest(p):
 with Path(p).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def require(ok,message):
 if not ok:raise RuntimeError(message)
def main():
 os.umask(0o077);scope=require_qa_scope();require(resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'core1');require(digest(BASE/'store-model-manifest.json')==EXPECTED,'model manifest changed')
 m=json.loads((BASE/'store-model-manifest.json').read_text());tool=json.loads((BASE/'model-toolchain.json').read_text());tc=BASE/'model-toolchain';node=tc/'node';cli=tc/'quint/dist/src/cli.js'
 def inputs():
  for row in m['canonicalModels'].values():require(digest(BASE/row['localName'])==row['sha256'],'model changed')
  require(digest(node)==tool['nodeSHA256'],'node changed')
  rows={};root=tc/'quint'
  for p in sorted(root.rglob('*')):
   name=str(p.relative_to(root))
   if p.is_symlink():rows[name]={'symlink':p.readlink().as_posix(),'sha256':digest(p) if p.is_file() else None}
   elif p.is_file():rows[name]={'sha256':digest(p)}
  require(len(rows)==tool['files'] and hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()==tool['treeSHA256'],'quint tree changed')
 inputs();out=BASE/('model-run-'+uuid.uuid4().hex);out.mkdir(mode=0o700);home=out/'home';home.mkdir(mode=0o700);env={'PATH':'/usr/bin:/bin','HOME':str(home),'LANG':'C','LC_ALL':'C','NO_COLOR':'1'}
 report=dict(schema=1,passed=False,scope=scope,manifestSHA256=EXPECTED,commands=[],samples=m['samples'],maxSteps=m['maxSteps'],seed=m['seed'],backend='typescript',nodeSHA256=tool['nodeSHA256'],quintTreeSHA256=tool['treeSHA256'],nativeAccepted=False,releaseAccepted=False)
 def run(label,args,timeout=240):
  start=time.monotonic();forced=False
  with (out/(label+'.stdout')).open('xb') as stdout,(out/(label+'.stderr')).open('xb') as stderr:
   try:r=subprocess.run(args,cwd=BASE,env=env,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,timeout=timeout);code=r.returncode
   except subprocess.TimeoutExpired:forced=True;code=None
  report['commands'].append(dict(label=label,argv=args,exit=code,forced=forced,elapsedSeconds=time.monotonic()-start,stdoutSHA256=digest(out/(label+'.stdout')),stderrSHA256=digest(out/(label+'.stderr'))));require(code==0 and not forced,label+' failed');return (out/(label+'.stdout')).read_text()
 try:
  require(run('node-version',[str(node),'--version']).strip()=='v24.22.1','node version')
  require(run('quint-version',[str(node),str(cli),'--version']).strip()=='0.33.0','Quint version')
  common=[str(node),'--max-old-space-size=1024',str(cli)];model=BASE/'store-retirement.qnt';tests=BASE/'store-retirement_test.qnt'
  names=re.findall(r'^\s*run\s+(\w+)\s*=',tests.read_text(),re.M);require(len(names)==14 and len(set(names))==14,'named cases empty/mismatched')
  run('typecheck',common+['typecheck',str(model)]);run('test-typecheck',common+['typecheck',str(tests)])
  directed=run('directed',common+['test',str(tests),'--main=store_retirement_test','--match=^(?:'+'|'.join(names)+')$','--backend=typescript','--verbosity=2']);require(re.findall(r'\b(\d+) passing\b',directed)==['14'],'exact14notexecuted')
  sampled=run('safety',common+['run',str(model),'--main=store_retirement','--backend=typescript','--invariant=safety','--witnesses',*m['witnesses'],'--seed='+str(m['seed']),'--max-samples='+str(m['samples']),'--max-steps='+str(m['maxSteps']),'--verbosity=1'])
  counts={name:int(n) for name,n in re.findall(r'(witness\w+) was witnessed in (\d+) trace',sampled)};require(set(counts)==set(m['witnesses']) and all(n>0 for n in counts.values()),'witness missing/zero')
  inputs();report.update(passed=True,namedCases=names,witnessCounts=counts,interpretation='No counterexample observed in executed bounded14traces and10000sampled40step traces; not exhaustive verification or physical cleanup proof.')
 except BaseException as error:report['error']=type(error).__name__+': '+str(error)
 finally:(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=report['passed'],report=str(out/'report.json'),error=report.get('error'),nativeAccepted=False)),flush=True)
 return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
