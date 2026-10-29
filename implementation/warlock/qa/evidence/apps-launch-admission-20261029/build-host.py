#!/usr/bin/python3
"""Root-review candidate: rebuild all host units against one reviewed host.c hash."""
import argparse, hashlib, json, os, re, resource, shlex, shutil, subprocess, sys, traceback
from pathlib import Path
R=Path('/home/charles/Warlock'); P=R/'implementation/warlock'; H=R/'implementation/warlock-preview-provider-v143'; B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild'); OLD=B/'host'; O=B/'taskbar-host-rebuild-v1/output'; A=B/'launcher-pending-visibility-fix/assets-build-v1/report.json'; T=B/'fresh-pair/tuple.json'
sys.path.insert(0,str(R/'window-integration-qa'))
from qa_launch import require_qa_scope
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
UNITS=['shared-host.c','preview_uri.cpp','preview_icons.cpp','preview-uri-webkit.cpp','preview-provider-bootstrap.cpp','client-producer.cpp','imported-clients.cpp','preview-uri-router.cpp','elm-preview-policy.cpp','preview-visual-channel.cpp','preview-policy-driver.cpp']
PACKAGES=['gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']
REPORT='691806471ff599503a20067aa0b90bf914b93a1ee5985198cdc79fb92ff975bf'; ASSETS='d31ddf1174986d902e8c2cecfcbc25bc5e0d9e743c465afadb6d159208eec606'; TUPLE='bc225242e30baf4a5b8b1182cef6fdc716cc9c67de90dc35674f90c5fa87830b'; MANIFEST='fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa'; ELM='c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948'; DESKTOP='a503d926599b5aa194956a1208fdc0004fb829442cd523c5372d41fd1fab0404'; OLDHOST='cde6230199756dfaa193d5e8af5a41470f8b65de3cdd1942e0e0224ab458ccbf'
SLOTS={'core':'b1c58200342f3cb8f5442bc34b92563ca21801194a0d63afc6e74280ca3abd0e','authority':'9ae1626ab46a3993f30890689425ab7a92354b0c9ed604e4283f6d507c5d170c','aquamarine':'667a22d535aade4e4a26134e39028a87fb3f963c28b7bf7ff79da684bb014ecd'}
def snapshot(root): return {str(p):sha(p) for p in sorted(root.rglob('*')) if p.is_file()}
def check_map(m):
 for p,h in m.items():
  if sha(p)!=h: raise RuntimeError('changed input: '+p)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--host-sha256',required=True); expected=ap.parse_args().host_sha256
 if not re.fullmatch('[0-9a-f]{64}',expected) or expected==OLDHOST: raise ValueError('supply reviewed changed host.c SHA256')
 require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1): raise RuntimeError('wrong core limit')
 O.mkdir(exist_ok=False)
 result={'passed':False,'nativeAcceptance':False,'commands':[],'reviewedHostSHA256':expected,'driverSHA256':sha(__file__),'coreLimit':list(resource.getrlimit(resource.RLIMIT_CORE)),'cgroup':Path('/proc/self/cgroup').read_text().strip()}
 env={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','SOURCE_DATE_EPOCH':'0','PYTHONDONTWRITEBYTECODE':'1'}
 def run(name,args):
  cmd=[str(x) for x in args]; p=subprocess.run(cmd,cwd=R,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=240)
  so=O/(name+'.stdout'); se=O/(name+'.stderr'); so.write_bytes(p.stdout); se.write_bytes(p.stderr)
  result['commands'].append({'name':name,'argv':cmd,'cwd':str(R),'env':env,'exit':p.returncode,'stdoutSHA256':sha(so),'stderrSHA256':sha(se)})
  if p.returncode: raise RuntimeError(name+' exited '+str(p.returncode))
  return p.stdout.decode()
 try:
  assert sha(OLD/'host-build-report.json')==REPORT and sha(A)==ASSETS and sha(T)==TUPLE
  old=json.loads((OLD/'host-build-report.json').read_text()); assets=json.loads(A.read_text()); tup=json.loads(T.read_text()); assert old['complete'] and assets['passed']
  assert sha(P/'native/host.c')==expected and sha(P/'src/Desktop.elm')==DESKTOP
  prior=dict(old['compiledDependencyHashes']); assert len(prior)==1317 and prior[str(P/'native/host.c')]==OLDHOST
  prior[str(P/'native/host.c')]=expected; check_map(prior)
  tools=dict(old['toolHashes']); tools={k:v for k,v in tools.items() if k in ['/usr/bin/gcc','/usr/bin/g++','/usr/bin/pkgconf']}; assert len(tools)==3; check_map(tools)
  for n,h in SLOTS.items(): assert tup['slots'][n]['sha256']==h and sha(tup['slots'][n]['path'])==h
  aq=B/'prefix/lib/libaquamarine.so.0.15.0'; alias=B/'prefix/lib/libaquamarine.so.14'; assert alias.is_symlink() and alias.resolve()==aq.resolve() and sha(aq)==SLOTS['aquamarine']
  def held():
   assert sha(H/'qa/toolchain.json')==MANIFEST
   t=json.loads((H/'qa/toolchain.json').read_text()); assert len(t['heldFiles'])==111 and t['compilerSHA256']==ELM and sha(H/t['compiler'])==ELM
   for name,row in t['heldFiles'].items():
    p=H/name; assert p.is_file() and p.stat().st_size==row['size'] and sha(p)==row['sha256']
  held()
  check_map(assets['sourceAfter']); assetmap={row['path']:row['sha256'] for row in assets['assets'].values()}; check_map(assetmap)
  native=snapshot(P/'native'); historical_native={str(R/k):v for k,v in old['sourceHashes'].items() if k.startswith('implementation/warlock/native/')}; assert historical_native[str(P/'native/host.c')]==OLDHOST; historical_native[str(P/'native/host.c')]=expected; assert native==historical_native
  result.update({'historicalReportSHA256':REPORT,'assetReportSHA256':ASSETS,'tupleSHA256':TUPLE,'nativeSourcesBefore':native,'historicalDependenciesAdjusted':prior,'toolHashes':tools,'assets':assetmap,'assetSources':assets['sourceAfter'],'heldManifestSHA256':MANIFEST,'elmCompilerSHA256':ELM})
  for n,cmd in [('cc-version',['/usr/bin/cc','--version']),('cxx-version',['/usr/bin/g++','--version']),('pkg-version',['/usr/bin/pkg-config','--version']),('pkg-modversions',['/usr/bin/pkg-config','--modversion',*PACKAGES])]: run(n,cmd)
  flags=shlex.split(run('pkg-config',['/usr/bin/pkg-config','--cflags','--libs',*PACKAGES])); assert flags==old['pkgConfigFlags']; result['pkgConfigFlags']=flags
  support={}
  for compiler, name in [('/usr/bin/cc','cc1'),('/usr/bin/g++','cc1plus'),('/usr/bin/g++','as'),('/usr/bin/g++','ld'),('/usr/bin/g++','collect2')]:
   value=run('tool-'+name,[compiler,'-print-prog-name='+name]).strip(); path=Path(value) if '/' in value else Path(shutil.which(value, path=env['PATH']) or '/nonexistent'); assert path.is_file(),value; support[str(path.resolve())]=sha(path.resolve())
  result['compilerSupportTools']=support
  objs=[]
  for i,n in enumerate(UNITS):
   obj=O/(n+'.o'); dep=O/(n+'.d'); objs.append(obj)
   run('compile-'+n,[('/usr/bin/cc' if i==0 else '/usr/bin/g++'),('-std=c11' if i==0 else '-std=c++20'),'-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',dep,'-c',P/'native'/n,'-o',obj,*flags])
  run('link-host',['/usr/bin/g++',*objs,'-o',O/'elm-host',*flags]); ldd=run('host-ldd',['/usr/bin/ldd',O/'elm-host'])
  if 'not found' in ldd: raise RuntimeError('missing linked provider')
  providers={}
  for line in ldd.splitlines():
   match=re.search(r'(?:=>\s*)?(/[^\s]+)\s+\(0x[0-9a-f]+\)',line)
   if match:
    path=str(Path(match.group(1)).resolve()); providers[path]=sha(path)
  result['linkedProviders']=providers
  dependencies={}
  for n in UNITS:
   dep=(O/(n+'.d')).read_text().replace('\\\n',' '); _,sep,body=dep.partition(':'); assert sep
   for name in shlex.split(body):
    path=Path(name); path=path if path.is_absolute() else R/path
    dependencies[str(path)]=sha(path)
  result['freshDependenciesAfterCompile']=dependencies; result['dependencyLimit']='Newly introduced dependencies have first-observed hashes after compilation, not historical pre-build hashes.'
  result['outputs']={str(p):sha(p) for p in [O/'elm-host',*[O/(n+'.o') for n in UNITS],*[O/(n+'.d') for n in UNITS]]}
  check_map(prior); check_map(tools); check_map(support); check_map(assetmap); check_map(assets['sourceAfter']); check_map(dependencies); check_map(providers); assert snapshot(P/'native')==native
  for n,h in SLOTS.items(): assert sha(tup['slots'][n]['path'])==h
  assert alias.is_symlink() and alias.resolve()==aq.resolve(); held(); assert sha(A)==ASSETS and sha(T)==TUPLE and sha(OLD/'host-build-report.json')==REPORT and sha(__file__)==result['driverSHA256']
  result['nativeSourcesAfter']=snapshot(P/'native'); result['passed']=True
 except Exception as e:
  result['error']=repr(e); (O/'failure.txt').write_text(traceback.format_exc())
 finally: (O/'report.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'passed':result['passed'],'report':str(O/'report.json'),'error':result.get('error')}))
 if not result['passed']: raise SystemExit(1)
if __name__=='__main__': main()
