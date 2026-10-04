"""Freeze actual integrated CPU build and exact held inputs, no GUI/acceptance."""
import hashlib,json,os,resource,stat,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
BUILD=ROOT/'qa/build-1791103452303629948/report.json'
TARGET=ROOT/'component-manifest.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def artifacts(d,p):
 for rel,w in d['artifacts'].items():assert sha(Path(p).parent/rel)==w,(p,rel)
def held(root,expected):
 p=root/'qa/held-source-manifest.json';assert sha(p)==expected,p
 d=read(p);assert d['sourceHeld'] is True and d['evidenceIntegrityPassed'] is True
 for rel,e in d['files'].items():
  q=root/rel;assert q.is_file() and not q.is_symlink() and sha(q)==e['sha256'],q
  if 'size' in e:assert q.stat().st_size==e['size'],q
  if 'mode' in e:assert stat.S_IMODE(q.stat().st_mode)==e['mode'],q
 return p,d
def component(p,expected):
 assert sha(p)==expected,p
 d=read(p);assert d['passed'] is True;root=Path(d.get('inventoryBase',p.parent.parent if p.name=='build-pair-manifest.json' else p.parent))
 entries=d['files']
 if isinstance(entries,dict):
  for rel,w in entries.items():assert sha(root/rel)==w,(p,rel)
 else:
  for e in entries:
   q=root/e['path']
   if 'symlink' in e:assert q.is_symlink() and os.readlink(q)==e['symlink'],q
   else:assert q.is_file() and not q.is_symlink() and sha(q)==e['sha256'] and q.stat().st_size==e['size'],q
 return d
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
assert not TARGET.exists(),'Never overwrite frozen component'
assert sha(BUILD)=='b0320e54bcd2f3b58dbb5702e07ae2d58b821473fd8cb1b3c5d90fd382da73b4'
b=read(BUILD);assert b['passed'] is True and all(x['exitCode']==0 for x in b['commands'])
for key,count in [('menuChecks',78),('geometryChecks',53),('refreshChecks',21)]:
 d=b[key];assert d['passed'] is True and d['checks']==len(d['cases'])==count and all(x['passed'] is True for x in d['cases']),key
artifacts(b,BUILD)
# Original capture hashes and generated final artifact hashes have separate roles.
for rel,w in b['inputs'].items():
 origin=Path(b['origins'][rel]);assert sha(origin)==w,origin
 generated=rel in ('assets/elm.js','assets/popup.js')
 if not generated:assert sha(BUILD.parent/'inputs'/rel)==w,rel
for rel,origin in b['origins'].items():assert rel in b['inputs'] and sha(origin)==b['inputs'][rel],rel
sources=read(ROOT/'qa/native-contract.json')['sourceLanes']
elm,broker,host=[REPO/sources[x] for x in ('elm','broker','host')]
elm_hold,_=held(elm,'27ed7148d101cafb220f3ed21e2d3e14a1df5880f4924d01ff510473dccce450')
broker_hold,_=held(broker,'42aa90628d689727fe0293a95a99ce87d8f2ea10fe68ed1640b8527146f42ef3')
host_hold,h=held(host,'60e40d823ffcaa2bf1e3d5250d41a57ad5e41630fa62e1bb3a97939bd36e3d7c')
for label,p in [('elm',elm_hold),('broker',broker_hold),('host',host_hold)]:assert sha(BUILD.parent/'inputs/lineage'/ (label+'-held.json'))==sha(p)
host_report=Path(h['buildReport']);assert sha(host_report)==h['buildReportSHA256'];hb=read(host_report)
assert hb['passed'] is True and hb['nativeAcceptance'] is False and len(hb['dependencies'])==999 and hb['carrierChecks']==34 and hb['originalHostTests']==9
assert len(hb['mutants'])==3 and all(m['rejected'] is True for m in hb['mutants'])
for rel,w in hb['inputs'].items():assert sha(host/rel)==sha(host_report.parent/'inputs'/rel)==w,rel
for section in ('dependencies','tools'):
 for p,w in hb[section].items():assert sha(p)==w,p
artifacts(hb,host_report)
binary=BUILD.parent/'elm-host'
assert sha(binary)==b['binarySHA256']==hb['binarySHA256']==sha(hb['binary'])=='ad155e8f2703b357251b7276fdfd2d92d86078482cf0a2d101d217272528b368'
compile_command=next(c['argv'] for c in b['commands'] if c['name']=='host-compile');assert compile_command[-len(hb['flags']):]==hb['flags']
assert sha(BUILD.parent/'inputs/native/host.c')==hb['inputs']['native/host.c']
# V57 header/dependency closure did not record libraries. Add a separate fresh
# read-only closure for both identical binaries without altering V57's evidence.
ldd=Path('/usr/bin/ldd').resolve();library_maps=[]
for executable in (binary,Path(hb['binary'])):
 result=subprocess.run([str(ldd),str(executable)],capture_output=True,text=True,timeout=30)
 assert result.returncode==0 and 'not found' not in result.stdout,result.stderr
 libs={}
 for line in result.stdout.splitlines():
  for token in line.split():
   if token.startswith('/') and Path(token).is_file():
    p=Path(token).resolve();libs[str(p)]=sha(p)
 assert libs,'No host linked library closure';library_maps.append(libs)
assert library_maps[0]==library_maps[1],'Identical host bytes resolved different libraries'
core_path=REPO/'implementation/elm-window-geometry-default-limits-v40/component-manifest.json'
component(core_path,'dd924d35c3568b4b0e0434bbc2eb841789e69c4451806a6a62659111180ca712')
pair_path=REPO/'implementation/elm-window-geometry-owning-pair-v49/qa/build-pair-manifest.json'
pair=component(pair_path,'bd2e92fafa05355a0fb1fb07fadc5ff83f1e42a446dc00aad3ea8c120afbd81b')
plug_report=REPO/'implementation/elm-window-geometry-owning-pair-v49'/pair['buildReport'];assert sha(plug_report)==pair['buildReportSHA256'];pb=read(plug_report)
assert pb['passed'] is True and not pb['missingSymbols']
for section in ('dependencies','coreDependencies','coreLinkDependencies','linkedLibraries','tools'):
 for p,w in pb[section].items():assert sha(p)==w,p
artifacts(pb,plug_report)
base=REPO/sources['assets']
for rel,origin in b['origins'].items():
 if str(origin).startswith(str(base)):
  assert sha(origin)==b['inputs'][rel] and sha(BUILD.parent/'inputs'/rel)==b['artifacts']['inputs/'+rel],rel
assets={}
for p in sorted((BUILD.parent/'inputs/assets').glob('*')):
 if p.is_file():
  key=str(p.relative_to(BUILD.parent));assert sha(p)==b['artifacts'][key]
  assets['assets/'+p.name]={'path':str(p),'sha256':b['artifacts'][key],'artifactKey':key,'compiled':p.name in ('elm.js','popup.js')}
assert assets['assets/elm.js']['compiled'] and assets['assets/popup.js']['compiled']
files=[]
for p in sorted(ROOT.rglob('*')):
 if p==TARGET:continue
 if p.is_symlink():files.append({'path':str(p.relative_to(ROOT)),'symlink':os.readlink(p)})
 elif p.is_file():files.append({'path':str(p.relative_to(ROOT)),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode),'sha256':sha(p)})
packet={'schema':1,'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'qaScope':scope,'frozenNs':time.time_ns(),'scope':'Actual combined Main/Popup optimized compilation, 78 original +53 geometry +21 refresh CPU cases, exact C host byte identity/dependencies/libraries; no GUI/native/menu/release acceptance','nativeAcceptance':False,'geometryMenuNativeAccepted':False,'releaseAccepted':False,'deploymentAccepted':False,'fullRoadmapAccepted':False,'buildReport':str(BUILD),'buildReportSHA256':sha(BUILD),'buildRoot':str(BUILD.parent),'binary':str(binary),'binarySHA256':sha(binary),'cpuChecks':{'originalMenu':78,'geometry':53,'refresh':21},'guiAssets':assets,'sourceInputs':b['inputs'],'sourceOrigins':b['origins'],'artifacts':b['artifacts'],'heldContributors':{str(p):sha(p) for p in (elm_hold,broker_hold,host_hold)},'hostDependencyClosure':{'buildReport':str(host_report),'buildReportSHA256':sha(host_report),'compilerDependencies':999,'flags':hb['flags'],'binarySHA256':hb['binarySHA256'],'linkedLibraries':library_maps[0],'lddTool':str(ldd),'lddToolSHA256':sha(ldd)},'nativeCoreManifest':str(core_path),'nativeCoreManifestSHA256':sha(core_path),'nativePairManifest':str(pair_path),'nativePairManifestSHA256':sha(pair_path),'files':files}
with TARGET.open('x') as f:f.write(json.dumps(packet,indent=2)+'\n')
TARGET.chmod(0o444)
print(json.dumps({'passed':True,'manifest':str(TARGET),'manifestSHA256':sha(TARGET),'files':len(files),'binarySHA256':sha(binary),'guiAssets':assets,'hostLinkedLibraries':len(library_maps[0])}),flush=True)
