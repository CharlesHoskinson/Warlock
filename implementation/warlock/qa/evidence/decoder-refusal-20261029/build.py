#!/usr/bin/python3
"""Root-reviewed protected rebuild: 3 Elm assets, one C unit, 10 retained objects."""
import argparse,hashlib,json,os,pathlib,re,resource,shlex,shutil,subprocess,sys,traceback
from pathlib import Path
R=Path('/home/charles/Warlock'); P=R/'implementation/warlock'; H=R/'implementation/warlock-preview-provider-v143'; B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild'); D=Path(__file__).resolve().parent; O=D/'output'; OLD=B/'taskbar-host-rebuild-v1/output'; AR=B/'context-keyup-assets-v1/output/report.json'; HR=OLD/'report.json'; T=B/'fresh-pair/tuple.json'; M=H/'qa/toolchain.json'
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def checks(m):
 for p,h in m.items():
  if sha(p)!=h: raise RuntimeError('changed input '+str(p))
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--shell-sha256',required=True); ap.add_argument('--host-sha256',required=True); args=ap.parse_args()
 if any(not re.fullmatch('[0-9a-f]{64}',x) for x in (args.shell_sha256,args.host_sha256)): raise RuntimeError('reviewed source hashes required')
 sys.path.insert(0,str(R/'window-integration-qa')); from qa_launch import require_qa_scope
 scope=require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1): raise RuntimeError('core limit differs')
 O.mkdir(exist_ok=False); report={'passed':False,'nativeAcceptance':False,'requirementAccepted':False,'protectedScope':scope,'commands':[],'driverSHA256':sha(__file__)}
 env={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','SOURCE_DATE_EPOCH':'0','PYTHONDONTWRITEBYTECODE':'1'}
 def run(name,argv,cwd=R):
  argv=list(map(str,argv)); p=subprocess.run(argv,cwd=cwd,env=env,capture_output=True,timeout=240); out=O/(name+'.stdout'); err=O/(name+'.stderr'); out.write_bytes(p.stdout); err.write_bytes(p.stderr); report['commands'].append({'name':name,'argv':argv,'cwd':str(cwd),'exit':p.returncode,'stdoutSHA256':sha(out),'stderrSHA256':sha(err)})
  if p.returncode: raise RuntimeError(name+' failed')
  return p.stdout.decode()
 try:
  fixed={AR:'69d5b85ad1137c3e851127c2cf5b4d9dcfe16f16e46568cbf106d2f165c77955',HR:'13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a',T:'bc225242e30baf4a5b8b1182cef6fdc716cc9c67de90dc35674f90c5fa87830b',M:'fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa'}; checks(fixed)
  a=json.loads(AR.read_text()); h=json.loads(HR.read_text()); t=json.loads(T.read_text()); m=json.loads(M.read_text())
  if not a['passed'] or not h['passed']: raise RuntimeError('old receipt incomplete')
  oldassets={item['path']:item['sha256'] for item in a['assets'].values()}; checks(oldassets); checks(h['outputs'])
  sources=dict(a['sourceAfter']); sources[str(P/'src/Shell.elm')]=args.shell_sha256; checks(sources)
  if {str(p) for p in (P/'src').rglob('*.elm')}!={s for s in sources if s.startswith(str(P/'src')+'/') and s.endswith('.elm')}: raise RuntimeError('Elm inventory drift')
  oldstatic=a['staticAfter']; static={str(p.relative_to(P/'assets')):sha(p) for p in (P/'assets').rglob('*') if p.is_file() and str(p.relative_to(P/'assets')) not in {'elm.js','bar.js','popup.js'}}
  if static!=oldstatic: raise RuntimeError('static asset drift')
  native=dict(h['nativeSourcesAfter']); native[str(P/'native/host.c')]=args.host_sha256
  current={str(p):sha(p) for p in (P/'native').rglob('*') if p.is_file()}
  if native!=current: raise RuntimeError('native inventory drift')
  deps=dict(h['freshDependenciesAfterCompile']); deps[str(P/'native/host.c')]=args.host_sha256; checks(deps)
  for key in ('toolHashes','compilerSupportTools','linkedProviders'): checks(h[key])
  for name,d in {'core':'b1c58200342f3cb8f5442bc34b92563ca21801194a0d63afc6e74280ca3abd0e','authority':'9ae1626ab46a3993f30890689425ab7a92354b0c9ed604e4283f6d507c5d170c','aquamarine':'667a22d535aade4e4a26134e39028a87fb3f963c28b7bf7ff79da684bb014ecd'}.items():
   slot=t['slots'][name]
   if slot['sha256']!=d or sha(slot['path'])!=d: raise RuntimeError('tuple drift '+name)
  aq=t['slots']['aquamarine']; alias=Path(aq['sonameAlias'])
  if not alias.is_symlink() or os.readlink(alias)!=aq['aliasTarget'] or alias.resolve()!=Path(aq['path']).resolve(): raise RuntimeError('AQ alias drift')
  for name,item in m['heldFiles'].items():
   if sha(H/name)!=item['sha256']: raise RuntimeError('held Elm cache drift '+name)
  compiler=H/m['compiler']
  if sha(compiler)!='c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948': raise RuntimeError('compiler drift')
  objects=[Path(x) for x in h['outputs'] if x.endswith('.cpp.o')]; objects.sort(key=lambda x:next(i for i,c in enumerate(h['commands']) if c['name']=='compile-'+x.name[:-2]))
  if len(objects)!=10: raise RuntimeError('ten retained objects required')
  checks({str(x):h['outputs'][str(x)] for x in objects}); checks({str(x):v for x,v in h['outputs'].items() if x.endswith('.d')})
  flags=shlex.split(run('pkg-config',['/usr/bin/pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']))
  if flags!=h['pkgConfigFlags']: raise RuntimeError('pkg-config drift')
  w=O/'workspace'; w.mkdir(); (w/'src').symlink_to(P/'src',target_is_directory=True); shutil.copyfile(P/'elm.json',w/'elm.json'); assets=O/'assets'; assets.mkdir()
  for name in static:
   dest=assets/name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(P/'assets'/name,dest)
  home=O/'elm-home'; shutil.copytree(H/m['elmHome'],home); env['ELM_HOME']=str(home)
  for module,target in [('Main','elm.js'),('Bar','bar.js'),('Popup','popup.js')]: run('elm-'+module,[compiler,'make','src/'+module+'.elm','--optimize','--output='+str(assets/target)],w)
  obj=O/'shared-host.c.o'; dep=O/'shared-host.c.d'
  run('compile-shared-host',['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',dep,'-c',P/'native/shared-host.c','-o',obj,*flags])
  run('link-host',['/usr/bin/g++',obj,*objects,'-o',O/'elm-host',*flags])
  fresh={}; body=dep.read_text().replace('\\\n',' '); _,sep,body=body.partition(':')
  if not sep: raise RuntimeError('depfile malformed')
  for name in shlex.split(body):
   p=Path(name); p=p if p.is_absolute() else R/p; fresh[str(p)]=sha(p)
  ldd=run('host-ldd',['/usr/bin/ldd',O/'elm-host']); providers={}
  if 'not found' in ldd: raise RuntimeError('missing provider')
  for line in ldd.splitlines():
   x=re.search(r'(?:=>\s*)?(/[^\s]+)\s+\(0x[0-9a-f]+\)',line)
   if x:
    p=str(Path(x.group(1)).resolve()); providers[p]=sha(p)
  if providers!=h['linkedProviders']: raise RuntimeError('host linked providers drift')
  checks(sources); checks(native); checks(deps); checks(fresh); checks(fixed); checks(oldassets); checks(h['outputs']); checks(providers)
  for name,item in m['heldFiles'].items():
   if sha(H/name)!=item['sha256']: raise RuntimeError('held cache changed during build')
  for key in ('toolHashes','compilerSupportTools'): checks(h[key])
  for name in ('core','authority','aquamarine'):
   if sha(t['slots'][name]['path'])!=t['slots'][name]['sha256']: raise RuntimeError('tuple changed during build')
  if not alias.is_symlink() or os.readlink(alias)!=aq['aliasTarget'] or alias.resolve()!=Path(aq['path']).resolve(): raise RuntimeError('AQ alias changed during build')
  if {str(p.relative_to(P/'assets')):sha(p) for p in (P/'assets').rglob('*') if p.is_file() and str(p.relative_to(P/'assets')) not in {'elm.js','bar.js','popup.js'}}!=static: raise RuntimeError('static changed during build')
  report.update({'sources':sources,'static':static,'nativeSources':native,'retainedObjects':{str(x):sha(x) for x in objects},'freshHostDeps':fresh,'freshDependencyLimit':'newly introduced dependencies observed after compilation','linkedProviders':providers,'outputs':{str(p):sha(p) for p in [obj,dep,O/'elm-host',*sorted(assets.rglob('*'))] if p.is_file()},'receiptPins':{str(p):x for p,x in fixed.items()},'elmCompiler':{'path':str(compiler),'sha256':sha(compiler)},'passed':True})
 except Exception as e: report['error']=repr(e); report['traceback']=traceback.format_exc()
 (O/'report.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps({'passed':report['passed'],'report':str(O/'report.json'),'error':report.get('error')})); return 0 if report['passed'] else 1
if __name__=='__main__': sys.exit(main())
