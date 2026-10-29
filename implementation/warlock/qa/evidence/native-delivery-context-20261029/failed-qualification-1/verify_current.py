"""Exact current receipt qualification; historical rows retain explicit deltas."""
import hashlib,json,os,shlex
from pathlib import Path
B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
R=Path('/home/charles/Warlock');P=R/'implementation/warlock';D=Path(__file__).resolve().parent
HOST='56f0952d61f3ce57e7c2cb1122c640dc7548495bfab9b02677961b98266aa022'
SHARED='5d0d43c61574f292842bc34b2e3363cd5e7a215239e609bcb9780d475a9a8bbc'
def checked(p,h):
 p=Path(p)
 body=p.read_bytes()
 if hashlib.sha256(body).hexdigest()!=h:raise RuntimeError('Pinned bytes changed '+str(p))
 return body
def load(p,h):
 return json.loads(checked(p,h))
def maps(m):
 for p,h in m.items():checked(p,h)
def inventory(root):
 entries=list(root.rglob('*'))
 if any(p.is_symlink() for p in entries):raise RuntimeError('Source/output symlink '+str(root))
 return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in entries if p.is_file()}
def verify_tuple():
 hp=B/'first-use-delivery-historical-terra2-v1/historical_checks.py'
 body=checked(hp,'0b3306903ace3396835950220dee0920f2199ee73983545c0b79daea9cece3e3')
 import importlib.util
 spec=importlib.util.spec_from_loader('delivery_historical_receipts',loader=None)
 history_module=importlib.util.module_from_spec(spec);history_module.__file__=str(hp)
 exec(compile(body,str(hp),'exec'),history_module.__dict__)
 historical_result=history_module.verify_historical()
 delta=load(D/'deltas.json','4554553d5cc6aebb87185836def0a5c490f287a9b03b067de6909617ca78196b')
 t=load(B/'fresh-pair/tuple.json','bc225242e30baf4a5b8b1182cef6fdc716cc9c67de90dc35674f90c5fa87830b')
 old=load(B/'fresh-pair/preflight-report.json','56e50f6a488b39fadf72064586422c33d0162d78aa36e9b88e7ca8dee0a83a3e')
 pre=load(B/'source-coherence-20261028/terra-2/preflight-v1.json','ae8d3fdb03bbbed5e4b42fd91225dfba1891142e1403389d74112d2b0f945b89')
 add=load(B/'source-coherence-20261028/terra-2/addendum-v1.json','051cb5c76896ce4db6edc0b94042181d4614fd163a8f36e3239634522f532e63')
 replacement=add['replacement'];before=old['checks'][3390]
 if replacement!={'index':3390,'label':'host sourceHashes','path':str(P/'adapter/release_builder.py'),'previousSHA256':'640b47a214286ca9ec3fcda74d98d895610202befd49e9b8bcce51706e9a9919','currentSHA256':'43dfc887228de8a755964a0aaa8b645d9fb8f4a4a288b7ff48d7b1844d630a'}:raise RuntimeError('Historical addendum differs')
 if before['expectedSHA256']!=replacement['previousSHA256'] or before['actualSHA256']!=replacement['previousSHA256'] or before['path']!=replacement['path'] or before['label']!=replacement['label']:raise RuntimeError('Unexpected old row')
 derived=json.loads(json.dumps(old));derived['checks'][3390].update(expectedSHA256=replacement['currentSHA256'],actualSHA256=replacement['currentSHA256'])
 if pre!=derived or len(pre['checks'])!=4721 or not pre['passed'] or pre['errors']:raise RuntimeError('Historical preflight differs')
 for e in add['evidence']:checked(e['path'],e['sha256'])
 changes={x['index']:x for x in delta['preflight']}
 if len(changes)!=7:raise RuntimeError('Expected seven explicit changed rows')
 seen=set()
 for i,row in enumerate(pre['checks']):
  if row.get('passed') is not True:raise RuntimeError('Historical failing row')
  if i in changes:
   c=changes[i]
   if row.get('path')!=c['path'] or row.get('label')!=c['label'] or row.get('expectedSHA256')!=c['old'] or row.get('actualSHA256')!=c['old']:raise RuntimeError('Changed row lineage mismatch')
   checked(c['path'],c['current']);seen.add(i)
  elif 'expectedSHA256' in row:checked(row['path'],row['expectedSHA256'])
  elif row.get('label')=='aquamarine soname alias':
   q=Path(row['path'])
   if not q.is_symlink() or os.readlink(q)!=row['target']:raise RuntimeError('Alias changed')
  else:raise RuntimeError('Unknown preflight row')
 if seen!=set(changes):raise RuntimeError('Missing delta')
 history=load(B/'context-keyup-qualified-terra-2-v1/native-new-instance-keyboard-1793299294154176471/report.json','69ab8850e0bf9f71cb90b6db76ded032fbc8ecc94b5eb3cc9a4a3fb1767cd48f')['sourceInputs']
 if len(history)!=367 or len(delta['sources'])!=4:raise RuntimeError('Historical source inventory differs')
 for name,h in history.items():
  q=Path(name)
  if q.is_absolute() or '..' in q.parts:raise RuntimeError('Bad relative path')
  if name in delta['sources']:
   c=delta['sources'][name]
   if h!=c['old']:raise RuntimeError('Changed source lineage mismatch')
   h=c['current']
  checked(P/q,h)
 review=load(B/'runtime-review/runtime-review.json','c73693f0aa11091b3788e30f5e699f491293f43c005fa4977f03b27e5ff61e6b')
 foundation=load(B/'parent-host/foundation-result.json','08b24bd93cbb63ec097900915379b32e90d9dcca7156d04fe8ee959efaff264f')
 if not review['passed'] or review['errors'] or not foundation['passed'] or foundation['productPluginLoaded'] or not t['readyForRootReview'] or t['nativeAcceptance'] or t['pluginLoaded']:raise RuntimeError('Historical pair readiness differs')
 for e in t['reports'].values():checked(e['path'],e['sha256'])
 for slot in t['slots'].values():
  checked(slot['path'],slot['sha256'])
  if 'report' in slot:checked(slot['report']['path'],slot['report']['sha256'])
 for e in t['slots']['host']['assets'].values():checked(e['path'],e['sha256'])
 aq=t['slots']['aquamarine'];alias=Path(aq['sonameAlias'])
 if not alias.is_symlink() or os.readlink(alias)!=aq['aliasTarget'] or alias.resolve()!=Path(aq['path']).resolve():raise RuntimeError('AQ alias differs')
 npath=B/'arc004-build-terra2-v1/output/report.json';n=load(npath,'1c35c3c24cbc2011176affe84191f111bbc96caa4ea32a17ff737dd32f658ef6')
 hpath=B/'first-use-delivery-context-root-v1/output/report.json';h=load(hpath,'65b7e0fe87f775b6489a2092f355856cd273ec4461114897ddfeed177b721987')
 if not n['passed'] or n['nativeAcceptance'] or not h['passed'] or h['nativeAcceptance'] or h['reviewedHostSHA256']!=HOST or h['reviewedSharedSHA256']!=SHARED:raise RuntimeError('Current build disposition differs')
 if h['scope']['coreLimit']!=1 or n['protectedScope']['coreLimit']!=1:raise RuntimeError('Protected core scope missing')
 checked(hpath.parent.parent/'build-host.py',h['driverSHA256']);checked(npath.parent.parent/'build.py',n['driverSHA256'])
 for receipt in (h,n):
  maps(receipt['receiptPins'])
  for row in receipt['commands']:
   if row['exit']!=0:raise RuntimeError('Build command failed')
  out=hpath.parent if receipt is h else npath.parent
  for row in receipt['commands']:
   checked(out/(row['name']+'.stdout'),row['stdoutSHA256']);checked(out/(row['name']+'.stderr'),row['stderrSHA256'])
  maps(receipt['outputs'])
 if h['sources']!=n['sources'] or len(h['sources'])!=100:raise RuntimeError('Elm/source receipt differs')
 maps(h['sources'])
 if {str(q) for q in (P/'src').rglob('*.elm')}!={q for q in h['sources'] if q.startswith(str(P/'src')+'/') and q.endswith('.elm')}:raise RuntimeError('Elm inventory differs')
 native=inventory(P/'native')
 expected=dict(n['nativeSources']);expected[str(P/'native/host.c')]=HOST;expected[str(P/'native/shared-host.c')]=SHARED
 if len(native)!=239 or native!=expected or native!=h['nativeSourcesBefore'] or native!=h['nativeSourcesAfter']:raise RuntimeError('Current native inventory differs')
 if len(h['retainedObjects'])!=10 or h['retainedObjects']!=n['retainedObjects'] or h['providers']!=n['linkedProviders']:raise RuntimeError('Retained object/provider mismatch')
 for group in ('retainedObjects','providers','freshDependencies','assets'):maps(h[group])
 for group in ('retainedObjects','linkedProviders'):maps(n[group])
 olddeps=dict(n['freshHostDeps']);olddeps[str(P/'native/host.c')]=HOST;olddeps[str(P/'native/shared-host.c')]=SHARED;maps(olddeps)
 if set(olddeps)!=set(h['freshDependencies']):raise RuntimeError('Fresh dependency coverage differs')
 for q in h['receiptPins']:
  r=json.loads(Path(q).read_text())
  for group in ('toolHashes','compilerSupportTools'):
   if group in r:maps(r[group])
 static={str(Path(q).relative_to(P/'assets')):v for q,v in inventory(P/'assets').items() if Path(q).name not in {'elm.js','bar.js','popup.js'}}
 if static!=n['static']:raise RuntimeError('Current static sources differ')
 assets=inventory(npath.parent/'assets')
 if len(assets)!=19 or assets!=h['assets'] or assets!={q:v for q,v in n['outputs'].items() if '/assets/' in q}:raise RuntimeError('Current compiled asset inventory differs')
 held=R/'implementation/warlock-preview-provider-v143';m=load(held/'qa/toolchain.json','fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa')
 if len(m['heldFiles'])!=111:raise RuntimeError('Held inventory differs')
 for name,e in m['heldFiles'].items():
  checked(held/name,e['sha256'])
  if (held/name).stat().st_size!=e['size']:raise RuntimeError('Held size differs')
 checked(held/m['compiler'],'c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948')
 verify_recipes(n,h,npath,hpath)
 binary=hpath.parent/'elm-host';checked(binary,'a6b0f0cdfaf9d1fbf35494501fe623c88e889497c14b6fc9f65a7cc6ac5cba97')
 if h['outputs'].get(str(binary))!='a6b0f0cdfaf9d1fbf35494501fe623c88e889497c14b6fc9f65a7cc6ac5cba97':raise RuntimeError('Output not bound')
 t['slots']['host']['historicalHostReport']=dict(t['slots']['host']['report']);t['slots']['host']['historicalHostBinary']={k:t['slots']['host'][k] for k in ('path','sha256')}
 t['slots']['host'].update(path=str(binary),sha256='a6b0f0cdfaf9d1fbf35494501fe623c88e889497c14b6fc9f65a7cc6ac5cba97',report={'path':str(hpath),'sha256':'65b7e0fe87f775b6489a2092f355856cd273ec4461114897ddfeed177b721987'},assets={'assets/'+name:{'path':str(npath.parent/'assets'/name),'sha256':assets[str(npath.parent/'assets'/name)]} for name in ('elm.js','bar.js','popup.js')})
 t['historicalQualification']=historical_result
 t['sourceQualification']={'kind':'Explicit current native/Elm receipt qualification with all historical preflight/source rows retained','historicalTupleSHA256':'bc225242e30baf4a5b8b1182cef6fdc716cc9c67de90dc35674f90c5fa87830b','sourceDeltas':delta,'hostReportSHA256':'65b7e0fe87f775b6489a2092f355856cd273ec4461114897ddfeed177b721987','assetReportSHA256':'1c35c3c24cbc2011176affe84191f111bbc96caa4ea32a17ff737dd32f658ef6','nativeAcceptance':False}
 return t

def verify_recipes(n,h,npath,hpath):
 prior=load(B/'taskbar-host-rebuild-v1/output/report.json','13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a')
 flags=prior['pkgConfigFlags'];pkg=['/usr/bin/pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']
 names=['preview_uri.cpp','preview_icons.cpp','preview-uri-webkit.cpp','preview-provider-bootstrap.cpp','client-producer.cpp','imported-clients.cpp','preview-uri-router.cpp','elm-preview-policy.cpp','preview-visual-channel.cpp','preview-policy-driver.cpp']
 objects=[str(B/'taskbar-host-rebuild-v1/output'/(name+'.o')) for name in names]
 if set(objects)!=set(h['retainedObjects']) or set(objects)!=set(n['retainedObjects']):raise RuntimeError('Retained object set/order provenance differs')
 compiler=n['elmCompiler'];checked(compiler['path'],compiler['sha256'])
 if compiler['sha256']!='c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948':raise RuntimeError('Compiler identity differs')
 for receipt,out,cn,ln,dn in [(n,npath.parent,'compile-shared-host','link-host','host-ldd'),(h,hpath.parent,'compile','link','ldd')]:
  expected_names=['pkg-config','elm-Main','elm-Bar','elm-Popup',cn,ln,dn] if receipt is n else ['pkg-config',cn,ln,dn]
  if [c['name'] for c in receipt['commands']]!=expected_names:raise RuntimeError('Unexpected current command order')
  cmds={c['name']:c for c in receipt['commands']}
  expected={'pkg-config':pkg,cn:['/usr/bin/cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(out/'shared-host.c.d'),'-c',str(P/'native/shared-host.c'),'-o',str(out/'shared-host.c.o'),*flags],ln:['/usr/bin/g++',str(out/'shared-host.c.o'),*objects,'-o',str(out/'elm-host'),*flags],dn:['/usr/bin/ldd',str(out/'elm-host')]}
  for name,argv in expected.items():
   if cmds[name]['argv']!=argv or cmds[name]['cwd']!=str(R):raise RuntimeError('Current native recipe differs '+name)
  if shlex.split((out/'pkg-config.stdout').read_text())!=flags:raise RuntimeError('Current flags differ')
  if receipt is n:
   for module,target in [('Main','elm.js'),('Bar','bar.js'),('Popup','popup.js')]:
    c=cmds['elm-'+module]
    if c['argv']!=[compiler['path'],'make','src/'+module+'.elm','--optimize','--output='+str(out/'assets'/target)] or c['cwd']!=str(out/'workspace'):raise RuntimeError('Current Elm recipe differs')
   source_link=out/'workspace/src'
   if not source_link.is_symlink() or source_link.resolve()!=(P/'src').resolve():raise RuntimeError('Reviewed compiler source link differs')
   checked(out/'workspace/elm.json',n['sources'][str(P/'elm.json')])
  dep=(out/'shared-host.c.d').read_text().replace('\\\n',' ');_,sep,body=dep.partition(':')
  if not sep:raise RuntimeError('Malformed current dependency file')
  paths={str(Path(q) if Path(q).is_absolute() else R/q) for q in shlex.split(body)}
  if paths!=set(receipt['freshHostDeps'] if receipt is n else receipt['freshDependencies']):raise RuntimeError('Current dependency file coverage differs')
  import re
  providers={}
  for line in (out/(dn+'.stdout')).read_text().splitlines():
   if 'not found' in line:raise RuntimeError('Missing current provider')
   m=re.search(r'(?:=>\s*)?(/[^\s]+)\s+\(0x[0-9a-f]+\)',line)
   if m:
    q=str(Path(m.group(1)).resolve());providers[q]=hashlib.sha256(Path(q).read_bytes()).hexdigest()
  if providers!=(receipt['linkedProviders'] if receipt is n else receipt['providers']):raise RuntimeError('Current provider mapping differs')
