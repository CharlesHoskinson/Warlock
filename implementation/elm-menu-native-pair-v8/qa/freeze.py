import ast,hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];BASE=REPO/'implementation/elm-menu-reflow-v6';V5=REPO/'implementation/elm-menu-output-v5'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
upstream=read(ROOT/'upstream.json');assert digest(upstream['baseBuildReport'])==upstream['baseBuildReportSHA256']
assert digest(upstream['failedNativeReport'])==upstream['failedNativeReportSHA256'] and not read(upstream['failedNativeReport'])['passed']
for rel,sha in upstream['baseInputs'].items():
 if rel.split('/')[0] in ('src','native','adapter','assets'):assert digest(ROOT/rel)==sha,rel
buildPath=sorted((ROOT/'qa').glob('build-*/report.json'))[-1];build=read(buildPath);assert build['passed']
for rel,sha in build['inputs'].items():assert digest(ROOT/rel)==sha,rel
assert digest(buildPath.parent/'elm-host')==build['binarySHA256']
replayPath=sorted((ROOT/'qa').glob('replay-*/report.json'))[-1];replay=read(replayPath);assert replay['passed'] and replay['checks']==78
pairRoot=REPO/'implementation/elm-buffer-authority-pair-v8';pairManifest=read(pairRoot/'qa/build-pair-manifest.json');assert pairManifest['passed']
for rel,sha in pairManifest['files'].items():assert digest(pairRoot/rel)==sha,rel
pair=pairManifest['nativePair']
for part in ('core','plugin'):assert digest(pair[part]['path'])==pair[part]['sha256']
aq=read(ROOT/'aq-tuple.json');assert digest(aq['manifest'])==aq['manifestSHA256'] and digest(aq['library'])==aq['librarySHA256']
aqManifest=read(aq['manifest']);assert aqManifest['passed']
for row in aqManifest['files']:
 path=Path(aq['manifest']).parent/row['path']
 if 'symlink' in row:assert path.is_symlink() and str(path.readlink())==row['symlink'],str(path)
 else:assert digest(path)==row['sha256'],str(path)
proofs={}
for script in ('native','regression','output-regression','menu-reflow'):
 matches=[]
 for reportPath in (ROOT/'qa').glob('native-*/report.json'):
  r=read(reportPath)
  if r.get('inputs',{}).get(str(ROOT/'qa'/(script+'.py')))==digest(ROOT/'qa'/(script+'.py')):matches.append((reportPath,r))
 assert matches,script
 reportPath,r=sorted(matches,key=lambda row:str(row[0]))[-1]
 assert r['passed'] and r['cleanupPassed'] and all(c['passed'] for c in r['checks']),script
 assert r['buildReportSHA256']==digest(buildPath),script
 assert r['pair']['core']['sha256']==pair['core']['sha256'] and r['pair']['plugin']['sha256']==pair['plugin']['sha256']
 host=r['privateHost'];assert host['privateAquamarine']['mappedVerified']
 assert host['privateAquamarine']['mappedFiles']=={str(Path(aq['library']).resolve()):aq['librarySHA256']}
 assert r['pluginMapsAfterLoad']['files'][str(Path(pair['plugin']['path']).resolve())]==pair['plugin']['sha256']
 assert host['hyprlandMaps']['files'][str(Path(pair['core']['path']).resolve())]==pair['core']['sha256']
 # Preserve every original behavioral check/wait and helper, despite new tuple assertions.
 before=ast.parse((BASE/'qa'/(script+'.py')).read_text());after=ast.parse((ROOT/'qa'/(script+'.py')).read_text())
 def calls(tree):return [ast.dump(n,include_attributes=False) for n in sorted(ast.walk(tree),key=lambda n:getattr(n,'lineno',0)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ('check','wait')]
 assert calls(before)==calls(after),script+' behavioral oracle changed'
 for node in ast.walk(before):
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
   candidates=[n for n in ast.walk(after) if isinstance(n,type(node)) and n.name==node.name]
   assert any(ast.dump(n,include_attributes=False)==ast.dump(node,include_attributes=False) for n in candidates),node.name
 expected={'native':47,'regression':92,'output-regression':114,'menu-reflow':66}[script]
 assert len(r['checks'])==expected,(script,len(r['checks']))
 proofs[script]={'path':str(reportPath),'sha256':digest(reportPath),'checks':expected}
entries=[]
for path in sorted(ROOT.rglob('*')):
 if path.name=='implementation-manifest.json':continue
 if path.is_symlink():entries.append({'path':str(path.relative_to(ROOT)),'symlink':os.readlink(path)})
 elif path.is_file():entries.append({'path':str(path.relative_to(ROOT)),'sha256':digest(path),'size':path.stat().st_size})
manifest={'schema':1,'passed':True,'scope':'Bounded V6 Elm menu integration on corrected exact core/plugin/private AQ tuple','fullFeatureQualified':False,'fullRoadmapQualified':False,'parentPointerInputQualified':False,'cursorFallbackQualified':False,'multiOutputInputQualified':False,'rotationParentPassed':False,'nativeWrapperSafetyQualified':False,'releaseAcceptance':False,'nativeProofs':proofs,'buildReportSHA256':digest(buildPath),'replayReportSHA256':digest(replayPath),'pairManifestSHA256':digest(pairRoot/'qa/build-pair-manifest.json'),'aqManifestSHA256':aq['manifestSHA256'],'failedParentRetained':True,'files':entries}
p=ROOT/'qa/implementation-manifest.json';assert not p.exists();p.write_text(json.dumps(manifest,indent=2)+'\n');print(p,flush=True)
