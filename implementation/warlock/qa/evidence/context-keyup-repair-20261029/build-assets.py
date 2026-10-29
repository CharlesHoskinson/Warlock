#!/usr/bin/python3
"""Root-reviewed candidate: rebuild assets and qualify existing current host."""
import hashlib,json,os,re,resource,shutil,subprocess,sys,traceback
from pathlib import Path
R=Path('/home/charles/Warlock'); P=R/'implementation/warlock'; H=R/'implementation/warlock-preview-provider-v143'; B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild'); OUT=B/'context-keyup-assets-v1/output'; PREV=B/'launcher-pending-visibility-fix/assets-build-v1/report.json'; HOST=B/'taskbar-host-rebuild-v1/output/report.json'; TUPLE=B/'fresh-pair/tuple.json'
PREV_SHA='d31ddf1174986d902e8c2cecfcbc25bc5e0d9e743c465afadb6d159208eec606'; HOST_SHA='13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a'; TUPLE_SHA='bc225242e30baf4a5b8b1182cef6fdc716cc9c67de90dc35674f90c5fa87830b'; ELM='c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948'; MANIFEST='fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa'; OLD='2ff41ca906dc4e42ae76f65d486cf119b400414dee41ca886f5589709d2b9333'; NEW='e843e72479a6e499a99f4369f145530e8e097c576e7d08926a6a912dbd50bc8d'; HOSTELF='e0a2f0464b090f77c744c7fe7fc8e356a9d0f1ce2ad8a648040379dd2f7c0558'; HOSTSRC='f78d1ba337dff920e50e79e7324d5467cfbfe240a3b4d03c7d4239f52b17850a'; GENERATED={'elm.js','bar.js','popup.js'}
sys.path.insert(0,str(R/'window-integration-qa')); from qa_launch import require_qa_scope
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def files(root):
 paths=sorted(root.rglob('*'))
 if any(p.is_symlink() for p in paths): raise RuntimeError('unexpected symlink: '+str(root))
 return [p for p in paths if p.is_file()]
def snapshot(root): return {str(p):sha(p) for p in files(root)}
def check(m):
 for p,h in m.items():
  if sha(p)!=h: raise RuntimeError('changed input: '+p)
def main():
 scope=require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1): raise RuntimeError('wrong protected core limit')
 OUT.mkdir(exist_ok=False)
 result={'passed':False,'nativeAcceptance':False,'scope':'Fresh assets paired with separately built current native host; no native acceptance','commands':[],'protectedScope':scope,'coreLimit':[1,1],'driverSHA256':sha(__file__)}
 env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','SOURCE_DATE_EPOCH':'0','TZ':'UTC'}
 def run(name,argv,cwd):
  args=[str(a) for a in argv]; p=subprocess.run(args,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=240); a=OUT/(name+'.stdout'); b=OUT/(name+'.stderr'); a.write_bytes(p.stdout); b.write_bytes(p.stderr)
  result['commands'].append({'name':name,'argv':args,'cwd':str(cwd),'exit':p.returncode,'environment':{k:env[k] for k in ('ELM_HOME','SOURCE_DATE_EPOCH','TZ','PYTHONDONTWRITEBYTECODE') if k in env},'stdoutSHA256':sha(a),'stderrSHA256':sha(b)})
  if p.returncode: raise RuntimeError(name+' exited '+str(p.returncode))
  return p.stdout.decode()
 def providers(s):
  if 'not found' in s: raise RuntimeError('missing provider')
  values=set()
  for line in s.splitlines():
   m=re.search(r'(?:=>\s*)?(/[^\s]+)\s+\(0x[0-9a-f]+\)',line)
   if m: values.add(str(Path(m.group(1)).resolve(strict=True)))
  if not values: raise RuntimeError('empty ldd')
  return values
 try:
  assert sha(PREV)==PREV_SHA and sha(HOST)==HOST_SHA and sha(TUPLE)==TUPLE_SHA
  previous=json.loads(PREV.read_text()); host=json.loads(HOST.read_text()); tup=json.loads(TUPLE.read_text()); assert previous['passed'] and host['passed'] and not host['nativeAcceptance'] and host['assetReportSHA256']==PREV_SHA and host['reviewedHostSHA256']==HOSTSRC and host['tupleSHA256']==TUPLE_SHA
  elf=B/'taskbar-host-rebuild-v1/output/elm-host'; assert host['outputs'][str(elf)]==HOSTELF and sha(elf)==HOSTELF
  native=host['nativeSourcesAfter']; assert native==host['nativeSourcesBefore'] and len(native)==239 and native[str(P/'native/host.c')]==HOSTSRC and snapshot(P/'native')==native
  for key in ['historicalDependenciesAdjusted','freshDependenciesAfterCompile','toolHashes','compilerSupportTools','linkedProviders']: check(host[key])
  paths=providers(run('host-ldd-before',['/usr/bin/ldd',elf],R)); assert paths==set(host['linkedProviders'])
  for name,digest in {'core':'b1c58200342f3cb8f5442bc34b92563ca21801194a0d63afc6e74280ca3abd0e','authority':'9ae1626ab46a3993f30890689425ab7a92354b0c9ed604e4283f6d507c5d170c','aquamarine':'667a22d535aade4e4a26134e39028a87fb3f963c28b7bf7ff79da684bb014ecd'}.items():
   row=tup['slots'][name]; assert row['sha256']==digest and sha(row['path'])==digest
  aq=tup['slots']['aquamarine']; alias=Path(aq['sonameAlias']); assert alias.is_symlink() and os.readlink(alias)==aq['aliasTarget'] and alias.resolve()==Path(aq['path']).resolve()
  oldassets={row['path']:row['sha256'] for row in previous['assets'].values()}; check(oldassets)
  sources=previous['sourceAfter']; assert len(sources)==100 and previous['sourceBefore']==sources and len([x for x in sources if x.startswith(str(P/'src')+'/') and x.endswith('.elm')])==96; check(sources)
  assert {str(x) for x in (P/'src').rglob('*.elm')}=={x for x in sources if x.startswith(str(P/'src')+'/') and x.endswith('.elm')}
  static={str(p.relative_to(P/'assets')):sha(p) for p in files(P/'assets') if str(p.relative_to(P/'assets')) not in GENERATED}; expected=dict(previous['staticAfter']); assert expected==previous['staticBefore'] and len(expected)==16 and expected['context.js']==OLD; expected['context.js']=NEW; assert static==expected
  assert sha(H/'qa/toolchain.json')==MANIFEST; manifest=json.loads((H/'qa/toolchain.json').read_text()); assert len(manifest['heldFiles'])==111
  def held():
   assert sha(H/'qa/toolchain.json')==MANIFEST
   for name,row in manifest['heldFiles'].items():
    p=H/name; assert p.is_file() and p.stat().st_size==row['size'] and sha(p)==row['sha256']
   assert manifest['compilerSHA256']==ELM and sha(H/manifest['compiler'])==ELM
  held(); compiler=H/manifest['compiler']
  result.update({'previousAssetReport':{'path':str(PREV),'sha256':PREV_SHA},'hostReport':{'path':str(HOST),'sha256':HOST_SHA},'host':{'path':str(elf),'sha256':HOSTELF,'hostSourceSHA256':HOSTSRC},'tupleSHA256':TUPLE_SHA,'sourcesBefore':sources,'staticBefore':static,'nativeSourcesBefore':native,'historicalAssetHashes':oldassets,'heldManifestSHA256':MANIFEST,'compilerSHA256':ELM,'historicalNewInstanceEvidence':{'assetReportSHA256':PREV_SHA,'sourceInputsUnchanged':True,'checks':previous['newInstanceChecks'],'newExecution':False},'linkedProviders':host['linkedProviders']})
  workspace=OUT/'workspace'; workspace.mkdir(); (workspace/'src').symlink_to(P/'src',target_is_directory=True); shutil.copyfile(P/'elm.json',workspace/'elm.json'); assets=OUT/'assets'; assets.mkdir()
  for name in static:
   dest=assets/name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(P/'assets'/name,dest)
  elmhome=OUT/'elm-home'; shutil.copytree(H/manifest['elmHome'],elmhome); env['ELM_HOME']=str(elmhome)
  for module,target in [('Main','elm.js'),('Bar','bar.js'),('Popup','popup.js')]: run('compile-'+module,[compiler,'make','src/'+module+'.elm','--optimize','--output='+str(assets/target)],workspace)
  output={str(p.relative_to(assets)):{'path':str(p),'sha256':sha(p)} for p in files(assets)}; assert set(output)==set(static)|GENERATED and all(output[n]['sha256']==h for n,h in static.items()); result['assets']=output
  result['sourceAfter']={p:sha(p) for p in sources}; assert result['sourceAfter']==sources; result['staticAfter']={str(p.relative_to(P/'assets')):sha(p) for p in files(P/'assets') if str(p.relative_to(P/'assets')) not in GENERATED}; assert result['staticAfter']==static
  result['nativeSourcesAfter']=snapshot(P/'native'); assert result['nativeSourcesAfter']==native
  for key in ['historicalDependenciesAdjusted','freshDependenciesAfterCompile','toolHashes','compilerSupportTools','linkedProviders']: check(host[key])
  check({v['path']:v['sha256'] for v in output.values()}); assert providers(run('host-ldd-after',['/usr/bin/ldd',elf],R))==paths; check(oldassets); held()
  assert sha(PREV)==PREV_SHA and sha(HOST)==HOST_SHA and sha(TUPLE)==TUPLE_SHA and sha(elf)==HOSTELF and sha(__file__)==result['driverSHA256'] and alias.is_symlink() and os.readlink(alias)==aq['aliasTarget'] and alias.resolve()==Path(aq['path']).resolve()
  for name in ('core','authority','aquamarine'): assert sha(tup['slots'][name]['path'])==tup['slots'][name]['sha256']
  result['passed']=True
 except Exception as e:
  result['error']=repr(e); (OUT/'failure.txt').write_text(traceback.format_exc())
 finally: (OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'passed':result['passed'],'report':str(OUT/'report.json'),'error':result.get('error')}))
 if not result['passed']: raise SystemExit(1)
if __name__=='__main__': main()
