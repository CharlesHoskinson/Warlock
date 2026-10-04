"""Freeze actual integrated CPU build and exact held inputs, no GUI/acceptance."""
import argparse,hashlib,json,os,resource,stat,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--build',required=True);args=parser.parse_args()
BUILD=Path(args.build).resolve(strict=True)
assert BUILD.parent.parent==ROOT/'qa' and BUILD.name=='report.json' and BUILD.parent.name.startswith('build-'),'Exact local build packet required'
TARGET=ROOT/'component-manifest.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def artifacts(d,p):
 for rel,w in d['artifacts'].items():assert sha(Path(p).parent/rel)==w,(p,rel)
def held(root,expected):
 p=root/'qa/held-source-manifest.json';assert sha(p)==expected,p
 d=read(p);assert d['sourceHeld'] is True and d['evidenceIntegrityPassed'] is True
 entries=d['files'].items() if isinstance(d['files'],dict) else ((row['path'],row) for row in d['files'])
 for rel,e in entries:
  q=root/rel;assert q.is_file() and not q.is_symlink() and sha(q)==e['sha256'],q
  if 'size' in e:assert q.stat().st_size==e['size'],q
  if 'mode' in e:assert stat.S_IMODE(q.stat().st_mode)==(int(e['mode'],8) if isinstance(e['mode'],str) else e['mode']),q
 return p,d
def component(p,expected):
 assert sha(p)==expected,p
 d=read(p);assert d.get('passed',d.get('sourceHeld')) is True;root=Path(d.get('inventoryBase',p.parent.parent if p.name=='build-pair-manifest.json' else p.parent))
 entries=d['files']
 if isinstance(entries,dict):
  for rel,w in entries.items():assert sha(root/rel)==(w['sha256'] if isinstance(w,dict) else w),(p,rel)
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
b=read(BUILD);assert b['passed'] is True and not b.get('error')
assert all(x['exitCode']==0 for x in b['commands'] if not x.get('diagnosticOnly'))
d=b['postCloseChecks'];assert d['passed'] and d['checks']==len(d['cases'])==59 and all(x['passed'] for x in d['cases'])
for suite,count,passed in [('menu',78,64),('refresh',21,18)]:
 diagnostic=b['originalSuites'][suite]
 assert diagnostic['accepted'] is False and diagnostic['exitCode']!=0
 result=diagnostic['result'];assert not result['passed'] and result['checks']==len(result['cases'])==count
 assert sum(c['passed'] for c in result['cases'])==passed
assert b['originalSuites']['geometry']['accepted'] is False and b['originalSuites']['geometry']['exitCode']!=0 and not b['originalSuites']['geometry']['result']['passed']
artifacts(b,BUILD)
# Original capture hashes and generated final artifact hashes have separate roles.
for rel,w in b['inputs'].items():
 origin=Path(b['origins'][rel]);assert sha(origin)==w,origin
 generated=rel in ('assets/elm.js','assets/popup.js')
 if not generated:assert sha(BUILD.parent/'inputs'/rel)==w,rel
for rel,origin in b['origins'].items():assert rel in b['inputs'] and sha(origin)==b['inputs'][rel],rel
contract=read(ROOT/'qa/native-contract.json')
ancestor=Path(contract['sourceLineageParent'])/'component-manifest.json'
previous=component(ancestor,contract['sourceLineageParentManifestSHA256'])
assert sha(BUILD.parent/'inputs/lineage/previous-build-held.json')==sha(ancestor)
# Retain the failed V65 list-manifest preflight packet and exact captured script.
failure_root=REPO/'implementation/elm-geometry-integrated-menu-v65'
failures=[]
for p in sorted(failure_root.glob('qa/build-*/report.json')):
 d=read(p);assert d['passed'] is False
 artifacts(d,p)
 assert 'AttributeError' in d.get('error','') and 'items' in d['error'],p
 failures.append({'report':str(p),'sha256':sha(p)})
assert failures,'Original failed preflight packet missing'
failed_files={str(p):sha(p) for p in sorted(failure_root.rglob('*')) if p.is_file() and not p.is_symlink()}
sources=contract['sourceLanes']
elm,broker,host=[REPO/sources[x] for x in ('elm','broker','host')]
elm_hold,_=held(elm,'c3172da2ef407113e440e27ed419ccc8e62c909ce08943c53fed16a56c4681ca')
broker_hold,_=held(broker,'3aa379a0c7c694455d32f08c69d047b4ac0dd9200015d30b40e68593938b2161')
host_hold,h=held(host,'60e40d823ffcaa2bf1e3d5250d41a57ad5e41630fa62e1bb3a97939bd36e3d7c')
postclose_hold,qa_packet=held(REPO/contract['qaLane'],'c3172da2ef407113e440e27ed419ccc8e62c909ce08943c53fed16a56c4681ca')
for label,p in [('elm',elm_hold),('broker',broker_hold),('host',host_hold),('post-close-qa',postclose_hold)]:assert sha(BUILD.parent/'inputs/lineage'/ (label+'-held.json'))==sha(p)
qa_root=REPO/contract['qaLane']
for name in ['menu.cjs','geometry.cjs','refresh.cjs','fixtures.json','geometry-fixtures.json']:
 assert sha(BUILD.parent/'inputs/qa/original'/name)==sha(qa_root/'semantic/qa/original'/name)==sha(REPO/'implementation/elm-geometry-observation-refresh-v58/qa'/name)
assert sha(BUILD.parent/'inputs/src/MenuSurfaceReplay.elm')==sha(qa_root/'semantic/src/MenuSurfaceReplay.elm')=='84b25332a2d437e813100dcbbc32738c0216eedcea9ba94251423aa3c25ff9dd'
assert sha(BUILD.parent/'inputs/source-worker/MenuSurfaceReplay.elm')==sha(elm/'src/MenuSurfaceReplay.elm')
assert sha(BUILD.parent/'inputs/qa/post-close.cjs')==sha(qa_root/'post-close/qa/post-close.cjs')=='f07b575c5a3396c683e7e800b4748edbc079fba258b0f3ba99c2f5bb53d6ea59'

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
core_path=REPO/'implementation/elm-geometry-monitor-core-v73/component-manifest.json'
component(core_path,'ea95dbdcac7b61ca0c43338338ea73cf135d4b9b806fe1effb72cc9debad84bf')
pair_root=REPO/'implementation/elm-geometry-monitor-pair-review-v76'
pair_path,pair=held(pair_root,'7119b6b63fbb60a39b9eae19d67b87746c00b75096f063dee0d5bf82c124a5a0')
plugin_root=Path(pair['pairRoot'])
for relative,row in pair['pairFiles'].items():assert sha(plugin_root/relative)==row['sha256'] and (plugin_root/relative).stat().st_size==row['size'],relative
review=read(pair['report']);assert review['passed'] and sha(pair['report'])==pair['reportSHA256']
for path,wanted in review['verified'].items():assert sha(path)==wanted,path
pair_descriptor_path=plugin_root/'native-build-report.json'
assert sha(pair_descriptor_path)=='30b119a1552935d68cfe303cd2373ad49048c9a5b41d6b106af3d7347a4c5663'
pair_descriptor=read(pair_descriptor_path);plug_report=Path(pair_descriptor['pluginBuildReport'])
assert sha(plug_report)==pair_descriptor['pluginBuildReportSHA256'];pb=read(plug_report)
assert pb['passed'] and pb['missingSymbols']==[] and pb['strongUndefinedCount']==152
for section in ('dependencies','linkedLibraries','tools'):
 for p,w in pb[section].items():assert sha(p)==w,p
artifacts(pb,plug_report)
assert pair_descriptor['binary']==pb['core']['path'] and pair_descriptor['sha256']==pb['core']['sha256']
assert sha(pair_descriptor['binary'])==pair_descriptor['sha256']
assert pair_descriptor['coreComponentManifestSHA256']==sha(core_path)
# Separate native qualification remains bounded to V79's original 96/7 campaign.
native_acceptance_path=REPO/'implementation/elm-geometry-monitor-native-acceptance-v84/component-manifest.json'
assert sha(native_acceptance_path)=='3ddb05c9de1a1ec74cf4642ef7dac8767a3fa22cfc81537306a919a48ef51a4a'
na=read(native_acceptance_path);assert na['boundedGeometryNativeAccepted'] and not na['fullMenuNativeAccepted']
for relative,row in na['files'].items():assert sha(Path(na['inventoryBase'])/relative)==row['sha256'],relative
native_pass=next(row for row in na['reports'] if row['passed']);assert sha(native_pass['path'])==native_pass['sha256']
nr=read(native_pass['path']);assert nr['passed'] and nr['cleanupPassed'] and len(nr['checks'])==96 and all(x['passed'] for x in nr['checks'])
assert sum(x['name'].endswith(':actualInteriorPixelsMatchSelectedConfigure') for x in nr['checks'])==7
# Separately compiled family fixtures/mutants have exact production source hashes.
for label,row in b['separateCpuEvidence'].items():
 assert sha(row['path'])==row['sha256'];e=read(row['path']);assert e['passed']
 for relative,wanted in e['sourceInputs'].items():assert sha(elm/relative)==wanted,relative
 for relative,wanted in e['artifacts'].items():assert sha(Path(row['path']).parent/relative)==wanted,relative
 assert sha(BUILD.parent/'inputs/lineage'/(label+'.json'))==row['sha256']
family=read(b['separateCpuEvidence']['family6']['path']);assert family['profiles']['actual']['checks']==6 and family['profiles']['actual']['exitCode']==0
assert all(family['profiles'][name]['compiled'] and family['profiles'][name]['exitCode']==1 for name in ['root-only','missing-native-guard'])
mutants=read(b['separateCpuEvidence']['postCloseFiveMutants']['path']);assert len(mutants['mutants'])==5 and all(x['compiled'] and x['failedCases'] for x in mutants['mutants'])
assert all(b['semanticSuites'][name]['passed'] and b['semanticSuites'][name]['checks']==count for name,count in [('menu',78),('geometry',53),('refresh',21)])
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
packet={'schema':1,'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'qaScope':scope,'frozenNs':time.time_ns(),'scope':'Actual V87 optimized Main/Popup with all152 staged semantic equivalents and59 post-close CPU checks; separate exact family6 and7 compiled mutants; original diagnostics retained. Native96/7 upstream qualification remains separate; no integrated native/menu/release acceptance','nativeAcceptance':False,'geometryMenuNativeAccepted':False,'releaseAccepted':False,'deploymentAccepted':False,'fullRoadmapAccepted':False,'buildReport':str(BUILD),'buildReportSHA256':sha(BUILD),'buildRoot':str(BUILD.parent),'binary':str(binary),'binarySHA256':sha(binary),'cpuChecks':{'stagedMenu':78,'stagedGeometry':53,'stagedRefresh':21,'postClose':59,'separateFamily':6,'separateCompiledMutantsRejected':7},'separateCpuEvidence':b['separateCpuEvidence'],'semanticSuites':b['semanticSuites'],'originalSuites':b['originalSuites'],'guiAssets':assets,'sourceInputs':b['inputs'],'sourceOrigins':b['origins'],'artifacts':b['artifacts'],'ancestorComponentManifest':str(ancestor),'ancestorComponentManifestSHA256':sha(ancestor),'retainedFailedPreflights':failures,'retainedFailedPreflightFiles':failed_files,'completedRequirementIds':[],'unsupportedNativeFallbackImplemented':False,'heldContributors':{str(p):sha(p) for p in (elm_hold,broker_hold,host_hold,postclose_hold)},'hostDependencyClosure':{'buildReport':str(host_report),'buildReportSHA256':sha(host_report),'compilerDependencies':999,'flags':hb['flags'],'binarySHA256':hb['binarySHA256'],'linkedLibraries':library_maps[0],'lddTool':str(ldd),'lddToolSHA256':sha(ldd)},'nativeCoreManifest':str(core_path),'nativeCoreManifestSHA256':sha(core_path),'nativePairManifest':str(pair_path),'nativePairManifestSHA256':sha(pair_path),'nativePairDescriptor':str(pair_descriptor_path),'nativePairDescriptorSHA256':sha(pair_descriptor_path),'separateBoundedNativeAcceptance':{'manifest':str(native_acceptance_path),'sha256':sha(native_acceptance_path),'scope':'Original V79 native96 andpixel7 only; not integrated menu acceptance'},'files':files}
with TARGET.open('x') as f:f.write(json.dumps(packet,indent=2)+'\n')
TARGET.chmod(0o444)
print(json.dumps({'passed':True,'manifest':str(TARGET),'manifestSHA256':sha(TARGET),'files':len(files),'binarySHA256':sha(binary),'guiAssets':assets,'hostLinkedLibraries':len(library_maps[0])}),flush=True)
