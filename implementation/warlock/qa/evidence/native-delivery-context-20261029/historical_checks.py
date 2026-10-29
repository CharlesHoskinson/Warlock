"""Immutable historical receipt assertions; current deltas are owned by caller."""
import hashlib,json,os,re,shlex
from pathlib import Path
R=Path('/home/charles/Warlock');P=R/'implementation/warlock';B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild');H=R/'implementation/warlock-preview-provider-v143'
OLDHOST='cde6230199756dfaa193d5e8af5a41470f8b65de3cdd1942e0e0224ab458ccbf'; HOST13='f78d1ba337dff920e50e79e7324d5467cfbfe240a3b4d03c7d4239f52b17850a'; SHELL='93fdf86ac11ff9c190978fb46557623045a6c697d468a42fc9ba16a4bfa4df48'; SHARED='6e7f43b92c08f19ac82f5c93d67ca69d0a11a6c73f01a763a018f2beba282a7a'
def read(path,expected):
 path=Path(path); raw=path.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected:raise RuntimeError('Historical input changed: '+str(path))
 return raw
def load(path,expected):return json.loads(read(path,expected))
def check_map(rows,changed=None):
 changed=changed or {}
 for path,digest in rows.items():
  if path in changed:
   if digest!=changed[path]:raise RuntimeError('Historical changed-source digest differs: '+path)
  else:read(path,digest)
def inventory(root):
 entries=list(root.rglob('*'))
 if any(p.is_symlink() for p in entries):raise RuntimeError('Historical asset symlink')
 return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in entries if p.is_file()}
def verify_historical():
 tuple_hash='bc225242e30baf4a5b8b1182cef6fdc716cc9c67de90dc35674f90c5fa87830b'; t=load(B/'fresh-pair/tuple.json',tuple_hash)
 prev=load(B/'host/host-build-report.json','691806471ff599503a20067aa0b90bf914b93a1ee5985198cdc79fb92ff975bf')
 ap=B/'launcher-pending-visibility-fix/assets-build-v1/report.json';a=load(ap,'d31ddf1174986d902e8c2cecfcbc25bc5e0d9e743c465afadb6d159208eec606')
 cp=B/'context-keyup-assets-v1/output/report.json';c=load(cp,'69d5b85ad1137c3e851127c2cf5b4d9dcfe16f16e46568cbf106d2f165c77955')
 hp=B/'taskbar-host-rebuild-v1/output/report.json';h=load(hp,'13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a')
 if not prev['complete'] or a['schema']!=1 or not a['passed'] or not c['passed'] or not h['passed'] or c['nativeAcceptance'] or h['nativeAcceptance']:raise RuntimeError('Historical report disposition')
 if a['protectedScope']['coreLimit']!=1 or a['protectedScope']['cgroup']!='0::/user.slice/user-1000.slice/user@1000.service/qa.slice/qa-harness.slice/qa-harness-2ee9b9455c8c44d39b249c8be93bd467.scope':raise RuntimeError('Historical asset scope')
 if h['coreLimit']!=[1,1] or h['cgroup']!='0::/user.slice/user-1000.slice/user@1000.service/qa.slice/qa-harness.slice/qa-harness-bfed7884e7c444c4b75f4f36b63f2d26.scope':raise RuntimeError('Historical native scope')
 if c['coreLimit']!=[1,1] or c['protectedScope']['coreLimit']!=1 or c['protectedScope']['cgroup']!='0::/user.slice/user-1000.slice/user@1000.service/qa.slice/qa-harness.slice/qa-harness-f0f7b25724ba4191a47940b1ae89e7f7.scope':raise RuntimeError('Historical context scope')
 for row in t['reports'].values():read(row['path'],row['sha256'])
 for name in ('core','aquamarine','authority','host'):
  row=t['slots'][name];read(row['path'],row['sha256'])
  if name in ('core','aquamarine','authority'):
   expected={'core':'b1c58200342f3cb8f5442bc34b92563ca21801194a0d63afc6e74280ca3abd0e','authority':'9ae1626ab46a3993f30890689425ab7a92354b0c9ed604e4283f6d507c5d170c','aquamarine':'667a22d535aade4e4a26134e39028a87fb3f963c28b7bf7ff79da684bb014ecd'}[name]
   if row['sha256']!=expected:raise RuntimeError('Historical native tuple changed')
 aq=t['slots']['aquamarine'];alias=Path(aq['sonameAlias'])
 if not alias.is_symlink() or os.readlink(alias)!=aq['aliasTarget'] or alias.resolve()!=Path(aq['path']).resolve():raise RuntimeError('Historical AQ alias')
 for row in t['slots']['host']['assets'].values():read(row['path'],row['sha256'])
 native=a['nativeReuse']
 for name in ('host','core','authority','aquamarine'):
  if native[name]!={k:t['slots'][name][k] for k in ('path','sha256')}:raise RuntimeError('Historical slot mismatch')
 if native['hostReport']!=t['slots']['host']['report'] or native['compiledDependencyHashes']!=prev['compiledDependencyHashes'] or len(native['compiledDependencyHashes'])!=1317 or native['aquamarineAlias']!={'path':aq['sonameAlias'],'target':aq['aliasTarget']}:raise RuntimeError('Historical native reuse mismatch')
 changed={str(P/'native/host.c'):OLDHOST,str(P/'native/shared-host.c'):SHARED}
 check_map(native['compiledDependencyHashes'],changed)
 providers=native['linkedProviders']
 if not providers:raise RuntimeError('Historical providers empty')
 for row in providers.values():read(row['path'],row['sha256'])
 if a['sourceBefore']!=a['sourceAfter'] or len(a['sourceAfter'])!=100:raise RuntimeError('Historical source inventory')
 check_map(a['sourceAfter'],{str(P/'src/Shell.elm'):SHELL})
 if a['staticBefore']!=a['staticAfter'] or len(a['staticAfter'])!=16:raise RuntimeError('Historical static inventory')
 oldout=ap.parent/'assets';oldassets=inventory(oldout);generated={'elm.js','bar.js','popup.js'}
 if set(oldassets)!=set(a['staticAfter'])|generated or any(oldassets[k]!=v for k,v in a['staticAfter'].items()):raise RuntimeError('Historical built assets mismatch')
 if a['assets']!={'assets/'+k:{'path':str(oldout/k),'sha256':v} for k,v in oldassets.items()}:raise RuntimeError('Historical asset receipt mismatch')
 manifest_sha='fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa';compiler_sha='c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948';m=load(H/'qa/toolchain.json',manifest_sha)
 if a['toolchainManifestSHA256']!=manifest_sha or a['compilerSHA256']!=compiler_sha or m['compilerSHA256']!=compiler_sha or len(m['heldFiles'])!=111:raise RuntimeError('Historical Elm toolchain')
 for name,row in m['heldFiles'].items():
  path=H/name;raw=read(path,row['sha256'])
  if len(raw)!=row['size']:raise RuntimeError('Held file size')
 compiler=H/m['compiler'];read(compiler,compiler_sha)
 if a['driver']['sha256']!='1a4394fceb89e49b1be5a13cf744a0df910678b086995bec75fbc72ea68fcb49' or a['driver']['path']!=str(ap.parent.parent/'build-assets.py'):raise RuntimeError('Historical asset builder')
 read(a['driver']['path'],a['driver']['sha256']);read(a['node']['path'],a['node']['sha256'])
 ac=a['commands'];names=['host-ldd','compile-Main','compile-Bar','compile-Popup','compile-NewInstanceReplay','typed-NewInstanceReplay','host-ldd-after']
 if [r['name'] for r in ac]!=names:raise RuntimeError('Historical asset command sequence')
 for row in ac:
  if row['exit']!=0:raise RuntimeError('Historical asset command failed')
  read(row['stdout'],row['stdoutSHA256']);read(row['stderr'],row['stderrSHA256'])
  if row['name'] in ('host-ldd','host-ldd-after') and (row['argv']!=['/usr/bin/ldd',t['slots']['host']['path']] or row['cwd']!=str(R)):raise RuntimeError('Historical asset host ldd command')
 for mod,target in [('Main','elm.js'),('Bar','bar.js'),('Popup','popup.js')]:
  row=next(r for r in ac if r['name']=='compile-'+mod)
  if row['argv']!=[str(compiler),'make','src/'+mod+'.elm','--optimize','--output='+str(oldout/target)] or row['cwd']!=str(ap.parent/'workspace'):raise RuntimeError('Historical asset compile recipe')
 if len(a['newInstanceChecks'])!=19 or set(a['newInstanceChecks'])!=set(prev['reducerChecks']) or not all(v is True for v in a['newInstanceChecks'].values()):raise RuntimeError('Historical replay result')
 check_map(a['replayArtifacts'])
 if h['reviewedHostSHA256']!=HOST13 or h['assetReportSHA256']!='d31ddf1174986d902e8c2cecfcbc25bc5e0d9e743c465afadb6d159208eec606' or h['tupleSHA256']!=tuple_hash or h['historicalReportSHA256']!='691806471ff599503a20067aa0b90bf914b93a1ee5985198cdc79fb92ff975bf' or h['driverSHA256']!='3e393072d4e7c1468884fa2fd1ae345be363df5e86a821107eb3d554f104eac4':raise RuntimeError('Historical native receipt binding')
 read(hp.parent.parent/'build-host.py',h['driverSHA256'])
 expected_prior=dict(prev['compiledDependencyHashes']);expected_prior[str(P/'native/host.c')]=HOST13
 if h['historicalDependenciesAdjusted']!=expected_prior:raise RuntimeError('Historical dependency lineage')
 check_map(expected_prior,{str(P/'native/host.c'):HOST13,str(P/'native/shared-host.c'):SHARED})
 fresh=h['freshDependenciesAfterCompile'];check_map(fresh,{str(P/'native/host.c'):HOST13,str(P/'native/shared-host.c'):SHARED})
 for group in ('toolHashes','compilerSupportTools','linkedProviders','outputs'):check_map(h[group])
 host=hp.parent/'elm-host';hostsha='e0a2f0464b090f77c744c7fe7fc8e356a9d0f1ce2ad8a648040379dd2f7c0558';read(host,hostsha)
 if h['outputs'].get(str(host))!=hostsha or h['assetSources']!=a['sourceAfter'] or h['assets']!={v['path']:v['sha256'] for v in a['assets'].values()} or h['heldManifestSHA256']!=manifest_sha or h['elmCompilerSHA256']!=compiler_sha or h['pkgConfigFlags']!=prev['pkgConfigFlags']:raise RuntimeError('Historical native inputs')
 if h['linkedProviders']!={v['path']:v['sha256'] for v in providers.values()}:raise RuntimeError('Historical host providers')
 units=['shared-host.c','preview_uri.cpp','preview_icons.cpp','preview-uri-webkit.cpp','preview-provider-bootstrap.cpp','client-producer.cpp','imported-clients.cpp','preview-uri-router.cpp','elm-preview-policy.cpp','preview-visual-channel.cpp','preview-policy-driver.cpp']
 required=['cc-version','cxx-version','pkg-version','pkg-modversions','pkg-config','tool-cc1','tool-cc1plus','tool-as','tool-ld','tool-collect2']+['compile-'+x for x in units]+['link-host','host-ldd'];cmd=h['commands'];env={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','SOURCE_DATE_EPOCH':'0','PYTHONDONTWRITEBYTECODE':'1'}
 if [x['name'] for x in cmd]!=required:raise RuntimeError('Historical host command order')
 for row in cmd:
  if row['exit']!=0 or row['cwd']!=str(R) or row['env']!=env:raise RuntimeError('Historical host command context')
  read(hp.parent/(row['name']+'.stdout'),row['stdoutSHA256']);read(hp.parent/(row['name']+'.stderr'),row['stderrSHA256'])
 flags=h['pkgConfigFlags'];objects=[];dep_paths=set()
 for i,name in enumerate(units):
  obj=hp.parent/(name+'.o');dep=hp.parent/(name+'.d');objects.append(str(obj))
  argv=['/usr/bin/cc' if i==0 else '/usr/bin/g++','-std=c11' if i==0 else '-std=c++20','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(dep),'-c',str(P/'native'/name),'-o',str(obj),*flags]
  if next(x for x in cmd if x['name']=='compile-'+name)['argv']!=argv:raise RuntimeError('Historical host compile recipe '+name)
  body=read(dep,h['outputs'][str(dep)]).decode().replace('\\\n',' ');_,sep,body=body.partition(':')
  if not sep:raise RuntimeError('Historical depfile malformed')
  for q in shlex.split(body):
   p=Path(q);dep_paths.add(str(p if p.is_absolute() else R/p))
 if set(h['outputs'])!={str(host)}|{str(hp.parent/(name+ext)) for name in units for ext in ('.o','.d')} or dep_paths!=set(fresh):raise RuntimeError('Historical native output/dependency coverage')
 if next(x for x in cmd if x['name']=='link-host')['argv']!=['/usr/bin/g++',*objects,'-o',str(host),*flags] or next(x for x in cmd if x['name']=='host-ldd')['argv']!=['/usr/bin/ldd',str(host)]:raise RuntimeError('Historical link or ldd command')
 if c['driverSHA256']!='2b3ffe36d4a0709d66370c8a7ae7bd1fa8ffad2e81b244780415c6180b2e15a8' or c['tupleSHA256']!=tuple_hash or c['previousAssetReport']!={'path':str(ap),'sha256':'d31ddf1174986d902e8c2cecfcbc25bc5e0d9e743c465afadb6d159208eec606'} or c['hostReport']!={'path':str(hp),'sha256':'13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a'} or c['host']!={'path':str(host),'sha256':hostsha,'hostSourceSHA256':HOST13}:raise RuntimeError('Historical context receipt binding')
 read(cp.parent.parent/'build-assets.py',c['driverSHA256'])
 if c['sourcesBefore']!=a['sourceAfter'] or c['sourceAfter']!=a['sourceAfter'] or c['nativeSourcesBefore']!=h['nativeSourcesBefore'] or c['nativeSourcesAfter']!=h['nativeSourcesAfter'] or c['nativeSourcesBefore']!=c['nativeSourcesAfter']:raise RuntimeError('Historical context source provenance')
 historical_static=dict(a['staticAfter']);historical_static['context.js']='e843e72479a6e499a99f4369f145530e8e097c576e7d08926a6a912dbd50bc8d'
 if c['staticBefore']!=historical_static or c['staticAfter']!=historical_static or c['historicalAssetHashes']!={v['path']:v['sha256'] for v in a['assets'].values()} or c['linkedProviders']!=h['linkedProviders'] or c['heldManifestSHA256']!=manifest_sha or c['compilerSHA256']!=compiler_sha:raise RuntimeError('Historical context asset inputs')
 if c['historicalNewInstanceEvidence']!={'assetReportSHA256':'d31ddf1174986d902e8c2cecfcbc25bc5e0d9e743c465afadb6d159208eec606','sourceInputsUnchanged':True,'checks':a['newInstanceChecks'],'newExecution':False}:raise RuntimeError('Historical replay binding')
 contextout=cp.parent/'assets';actual=inventory(contextout)
 if set(actual)!=set(historical_static)|generated or any(actual[k]!=v for k,v in historical_static.items()) or any(actual[k]!=oldassets[k] for k in generated):raise RuntimeError('Historical context assets')
 if c['assets']!={k:{'path':str(contextout/k),'sha256':v} for k,v in actual.items()}:raise RuntimeError('Historical context output receipt')
 cc=c['commands']
 if [r['name'] for r in cc]!=['host-ldd-before','compile-Main','compile-Bar','compile-Popup','host-ldd-after']:raise RuntimeError('Historical context command order')
 for row in cc:
  if row['exit']!=0:raise RuntimeError('Historical context command failed')
  read(cp.parent/(row['name']+'.stdout'),row['stdoutSHA256']);read(cp.parent/(row['name']+'.stderr'),row['stderrSHA256'])
  if row['name'].startswith('host-ldd-') and (row['argv']!=['/usr/bin/ldd',str(host)] or row['cwd']!=str(R)):raise RuntimeError('Historical context ldd recipe')
 for mod,target in [('Main','elm.js'),('Bar','bar.js'),('Popup','popup.js')]:
  row=next(x for x in cc if x['name']=='compile-'+mod)
  env={'ELM_HOME':str(cp.parent/'elm-home'),'SOURCE_DATE_EPOCH':'0','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1'}
  if row['argv']!=[str(compiler),'make','src/'+mod+'.elm','--optimize','--output='+str(contextout/target)] or row['cwd']!=str(cp.parent/'workspace') or row['environment']!=env:raise RuntimeError('Historical context compile recipe')
 def provider_paths(raw):
  found={}
  for line in raw.decode().splitlines():
   if 'not found' in line:raise RuntimeError('Historical missing provider')
   pair=re.search(r'^\s*(\S+)\s+=>\s+(/\S+)\s+\(',line);direct=re.search(r'^\s*(/\S+)\s+\(',line)
   if pair:found[pair.group(1)]=str(Path(pair.group(2)).resolve(strict=True))
   elif direct:found['loader']=str(Path(direct.group(1)).resolve(strict=True))
  if not found:raise RuntimeError('Historical empty provider map')
  return found
 expected_paths={name:row['path'] for name,row in providers.items()}
 prior_ldd=read(B/'host/host-ldd.stdout','c0a0bc7fd8063760c81e6421b220c3a11546c00d2af778f3c7412462c466064b')
 if provider_paths(prior_ldd)!=expected_paths:raise RuntimeError('Historical original host mapping')
 for row in ac:
  if row['name'] in ('host-ldd','host-ldd-after') and provider_paths(read(row['stdout'],row['stdoutSHA256']))!=expected_paths:raise RuntimeError('Historical asset host mapping')
 for row in cc:
  if row['name'].startswith('host-ldd-') and set(provider_paths(read(cp.parent/(row['name']+'.stdout'),row['stdoutSHA256'])).values())!=set(h['linkedProviders']):raise RuntimeError('Historical context host mapping')
 return {'historicalChecks':'passed','historicalReports':['d31ddf1174986d902e8c2cecfcbc25bc5e0d9e743c465afadb6d159208eec606','69d5b85ad1137c3e851127c2cf5b4d9dcfe16f16e46568cbf106d2f165c77955','13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a'],'changedSourceLimit':'historical hashes asserted against pinned receipts; live changed bytes must be verified by current seven/four delta owner','nativeAcceptance':False}
