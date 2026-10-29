#!/usr/bin/python3
"""Root-only protected host unit rebuild, retaining the qualified 10 C++ objects."""
import argparse,hashlib,json,os,re,resource,shlex,subprocess,sys,traceback
from pathlib import Path
R=Path('/home/charles/Warlock');P=R/'implementation/warlock';H=R/'implementation/warlock-preview-provider-v143';B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild');D=Path(__file__).resolve().parent;O=D/'output';N=B/'arc004-build-terra2-v1/output/report.json';F=B/'taskbar-host-rebuild-v1/output/report.json';T=B/'fresh-pair/tuple.json';M=H/'qa/toolchain.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(m):
 for p,h in m.items():
  if sha(p)!=h:raise RuntimeError('input drift: '+str(p))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--shared-sha256',required=True);a=ap.parse_args()
 if not re.fullmatch('[0-9a-f]{64}',a.shared_sha256):raise RuntimeError('reviewed shared-host hash required')
 sys.path.insert(0,str(R/'window-integration-qa'));from qa_launch import require_qa_scope
 scope=require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('incorrect core limit')
 O.mkdir(exist_ok=False);result={'passed':False,'nativeAcceptance':False,'requirementAccepted':False,'scope':scope,'commands':[],'driverSHA256':sha(__file__)}
 env={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','SOURCE_DATE_EPOCH':'0','PYTHONDONTWRITEBYTECODE':'1'}
 def run(name,argv):
  argv=list(map(str,argv));p=subprocess.run(argv,cwd=R,env=env,capture_output=True,timeout=240);out=O/(name+'.stdout');err=O/(name+'.stderr');out.write_bytes(p.stdout);err.write_bytes(p.stderr)
  result['commands'].append({'name':name,'argv':argv,'cwd':str(R),'exit':p.returncode,'stdoutSHA256':sha(out),'stderrSHA256':sha(err)})
  if p.returncode:raise RuntimeError(name+' failed')
  return p.stdout.decode()
 try:
  pins={N:'1c35c3c24cbc2011176affe84191f111bbc96caa4ea32a17ff737dd32f658ef6',F:'13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a',T:'bc225242e30baf4a5b8b1182cef6fdc716cc9c67de90dc35674f90c5fa87830b',M:'fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa'};check(pins)
  n=json.loads(N.read_text());f=json.loads(F.read_text());t=json.loads(T.read_text());m=json.loads(M.read_text())
  if not n['passed'] or not f['passed']:raise RuntimeError('receipt not passed')
  shared=str(P/'native/shared-host.c'); native=dict(n['nativeSources']);native[shared]=a.shared_sha256
  sources=n['sources'];assets={p:h for p,h in n['outputs'].items() if '/assets/' in p};check(sources);check(assets)
  if len(assets)!=19 or len(native)!=239 or len(n['retainedObjects'])!=10:raise RuntimeError('receipt inventory differs')
  if {str(p):sha(p) for p in (P/'native').rglob('*') if p.is_file()}!=native:raise RuntimeError('native source inventory drift')
  if {str(p) for p in (P/'src').rglob('*.elm')}!={p for p in sources if p.startswith(str(P/'src')+'/') and p.endswith('.elm')}:raise RuntimeError('Elm inventory drift')
  def static():return {str(p.relative_to(P/'assets')):sha(p) for p in (P/'assets').rglob('*') if p.is_file() and str(p.relative_to(P/'assets')) not in {'elm.js','bar.js','popup.js'}}
  if static()!=n['static']:raise RuntimeError('static drift')
  maps=[n['retainedObjects'],n['linkedProviders'],f['toolHashes'],f['compilerSupportTools'],n['outputs'],f['outputs']]
  for key in ('freshHostDeps',):
   v=dict(n[key]);v[shared]=a.shared_sha256;maps.append(v)
  for key in ('historicalDependenciesAdjusted','freshDependenciesAfterCompile'):
   v=dict(f[key]);v[str(P/'native/host.c')]=native[str(P/'native/host.c')];v[shared]=a.shared_sha256;maps.append(v)
  def stable():
   check(pins);check(sources);check(assets);check(native)
   for row in maps:check(row)
   for name,item in m['heldFiles'].items():
    if sha(H/name)!=item['sha256']:raise RuntimeError('held cache drift '+name)
   if static()!=n['static']:raise RuntimeError('static changed')
   if {str(p):sha(p) for p in (P/'native').rglob('*') if p.is_file()}!=native:raise RuntimeError('native inventory changed')
   if {str(p) for p in (P/'src').rglob('*.elm')}!={p for p in sources if p.startswith(str(P/'src')+'/') and p.endswith('.elm')}:raise RuntimeError('Elm inventory changed')
   for name,expected in {'core':'b1c58200342f3cb8f5442bc34b92563ca21801194a0d63afc6e74280ca3abd0e','authority':'9ae1626ab46a3993f30890689425ab7a92354b0c9ed604e4283f6d507c5d170c','aquamarine':'667a22d535aade4e4a26134e39028a87fb3f963c28b7bf7ff79da684bb014ecd'}.items():
    slot=t['slots'][name]
    if slot['sha256']!=expected or sha(slot['path'])!=expected:raise RuntimeError('tuple changed '+name)
   aq=t['slots']['aquamarine'];alias=Path(aq['sonameAlias'])
   if not alias.is_symlink() or os.readlink(alias)!=aq['aliasTarget'] or alias.resolve()!=Path(aq['path']).resolve():raise RuntimeError('AQ alias changed')
  stable()
  flags=shlex.split(run('pkg-config',['/usr/bin/pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']))
  if flags!=f['pkgConfigFlags']:raise RuntimeError('pkg-config flags changed')
  compile_cmd=list(next(x['argv'] for x in n['commands'] if x['name']=='compile-shared-host'))
  compile_cmd[compile_cmd.index('-MF')+1]=str(O/'shared-host.c.d');compile_cmd[compile_cmd.index('-o')+1]=str(O/'shared-host.c.o');run('compile',compile_cmd)
  link=list(next(x['argv'] for x in n['commands'] if x['name']=='link-host'));link[1]=str(O/'shared-host.c.o');link[link.index('-o')+1]=str(O/'elm-host');run('link',link)
  dep=(O/'shared-host.c.d').read_text().replace('\\\n',' ');_,sep,body=dep.partition(':')
  if not sep:raise RuntimeError('bad depfile')
  fresh={}
  for s in shlex.split(body):
   p=Path(s);p=p if p.is_absolute() else R/p;fresh[str(p)]=sha(p)
  output=run('ldd',['/usr/bin/ldd',O/'elm-host']);providers={}
  if 'not found' in output:raise RuntimeError('missing provider')
  for line in output.splitlines():
   match=re.search(r'(?:=>\s*)?(/[^\s]+)\s+\(0x[0-9a-f]+\)',line)
   if match:
    p=str(Path(match.group(1)).resolve());providers[p]=sha(p)
  if providers!=n['linkedProviders']:raise RuntimeError('linked provider change')
  check(fresh);stable()
  result.update({'reviewedSharedSHA256':a.shared_sha256,'nativeSourcesBefore':native,'nativeSourcesAfter':{str(p):sha(p) for p in (P/'native').rglob('*') if p.is_file()},'sources':sources,'assets':assets,'retainedObjects':n['retainedObjects'],'providers':providers,'freshDependencies':fresh,'dependencyLimit':'New dependency bytes first observed after compile; no claim of historical attribution.','outputs':{str(p):sha(p) for p in [O/'shared-host.c.o',O/'shared-host.c.d',O/'elm-host']},'receiptPins':{str(p):h for p,h in pins.items()},'passed':True})
 except Exception as e:result['error']=repr(e);result['traceback']=traceback.format_exc()
 (O/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'report':str(O/'report.json')}));return 0 if result['passed'] else 1
if __name__=='__main__':sys.exit(main())
