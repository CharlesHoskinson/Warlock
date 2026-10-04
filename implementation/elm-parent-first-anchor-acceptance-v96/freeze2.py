import hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;IMPL=ROOT.parent;REPO=IMPL.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def packet(p):
 d=json.loads(p.read_text());assert d['passed'],p
 for rel,h in d.get('artifacts',{}).items():assert sha(p.parent/rel)==h,rel
 for name in ['inputs','sourceInputs']:
  for path,h in d.get(name,{}).items():
   if Path(path).is_absolute():assert sha(path)==h,path
 return d
core_root=IMPL/'elm-core-parent-first-anchor-v89';core_path=core_root/'build-1791107301396755104/report.json';core=packet(core_path)
assert core['unchangedArchiveMembers']==432 and len(core['rebuiltArchiveMembers'])==1 and len(core['owningHeaders'])==694 and not core['exportClosure']['missingSymbols']
assert sha(core['binary'])==core['binarySHA256']=='3e02556699f1e1667a88ace26f656ee380fce8a39b20d405a3f0d2757c65cd73'
for rel,h in core['inputs'].items():assert sha(core_root/rel)==sha(core_path.parent/'inputs'/rel)==h
for rel,h in core['owningHeaders'].items():assert sha(core_path.parent/'owning-headers'/rel)==h
pair_root=IMPL/'elm-parent-first-anchor-pair-v90';pair_path=pair_root/'qa/build-1791107369559431070/report.json';pair=packet(pair_path)
assert pair['core']['sha256']==core['binarySHA256'] and len(pair['owningHeaders'])==694 and pair['strongUndefinedCount']==152 and not pair['missingSymbols']
assert sha(pair['binary'])==pair['binarySHA256']=='c0bf07547a943e48d5493bc2df490a27c91c2e8def6060150fb59237ade5e20c'
for rel,h in pair['inputs'].items():assert sha(pair_root/rel)==h
pm=packet(pair_root/'qa/build-pair-manifest.json')
for rel,h in pm['files'].items():assert sha(pair_root/rel)==h
for rel,target in pm['symlinks'].items():assert os.readlink(pair_root/rel)==target
warp_path=core_root/'qa/warp-1791107173327274874/report.json';warp=packet(warp_path);assert warp['checks']==24 and warp['mutantsRejected']==5 and warp['originalStationaryFailureReproduced']
model_path=sorted((IMPL/'elm-parent-first-anchor-model-v97/qa').glob('model-*/report.json'))[-1];model=packet(model_path);assert len(model['namedScenarios'])==10 and model['mutantsRejected']==6 and model['invariantSamples']==1000 and model['maxSteps']==40
assert model['sourceSHA256']==sha(core_root/'spec/anchor.qnt')
schedule_path=core_root/'qa/test-1791107173327125155/report.json';schedule=packet(schedule_path);assert schedule['checks']==29 and schedule['mutantsRejected']==5
campaigns=[
 ('burst',IMPL/'elm-parent-first-anchor-native-v91/qa/native-1791107465967616268/report.json',35,None),
 ('input',IMPL/'elm-parent-first-anchor-input-v92/qa/native-1791107557243965804/report.json',159,IMPL/'elm-seat-original-input-v85/qa/native-1791106661802588805/report.json'),
 ('menu',IMPL/'elm-parent-first-anchor-menu-v93/qa/menu-1791107602252087183/report.json',68,IMPL/'elm-parent-cursor-hit-test-v77/qa/menu-1791104785113020088/report.json'),
 ('cursor',IMPL/'elm-parent-first-anchor-menu-v93/qa/native-1791107791934827159/report.json',195,IMPL/'elm-parent-cursor-hit-test-v77/qa/native-1791105014801003538/report.json'),
 ('multi',IMPL/'elm-parent-first-anchor-multi-v94/qa/native-1791107746219146262/report.json',51,IMPL/'elm-parent-multioutput-fixed-v75/qa/native-1791104851222699838/report.json'),
 ('geometry',IMPL/'elm-parent-first-anchor-geometry-v95/qa/native-1791107701330561760/report.json',96,IMPL/'elm-geometry-effect-native-v55/qa/native-1791102357953536490/report.json')]
AQ=core['aqLibrary'];AQSHA=core['aqLibrarySHA256'];evidence=[]
for name,path,count,oldpath in campaigns:
 d=packet(path);assert len(d['checks'])==count and all(v['passed'] for v in d['checks']) and d['cleanupPassed']
 if oldpath is not None:assert [v['name'] for v in d['checks']]==[v['name'] for v in json.loads(oldpath.read_text())['checks']],name
 h=d['privateHost'];assert h['hyprlandMaps']['files'].get(core['binary'])==core['binarySHA256'],name
 assert h['privateAquamarine']['mappedVerified'] and h['privateAquamarine']['mappedFiles']=={AQ:AQSHA},name
 if name in ['menu','geometry']:assert d['pluginMapsAfterLoad']['files'].get(pair['binary'])==pair['binarySHA256'],name
 if name=='burst':assert [(b['cycles'],b['final'],b['publications']) for b in d['capabilityBursts']]==[(3,0,0),(4,1,1),(16,1,1)]
 if name=='geometry':assert len(d['pixelAttempts'])==7
 evidence.append({'campaign':name,'path':str(path.relative_to(REPO)),'sha256':sha(path),'checkExecutions':count,'originalReport':str(oldpath.relative_to(REPO)) if oldpath else None})
failed=core_root/'qa/warp-1791107145765290844/report.json';assert json.loads(failed.read_text())['passed'] is False
v87=IMPL/'elm-seat-burst-qualified-v87/qa/native-1791106488291216547/report.json';d=json.loads(v87.read_text());assert not d['passed'] and d['cleanupPassed'] and 'six-second' in d['error']
doc=REPO/'docs/elm-roadmap/delivery/PARENT-FIRST-ANCHOR-V96-ACCEPTANCE.md';assert doc.is_file()
roots=['elm-core-parent-first-anchor-v89','elm-parent-first-anchor-pair-v90','elm-parent-first-anchor-native-v91','elm-parent-first-anchor-input-v92','elm-parent-first-anchor-menu-v93','elm-parent-first-anchor-multi-v94','elm-parent-first-anchor-geometry-v95','elm-parent-first-anchor-acceptance-v96','elm-parent-first-anchor-model-v97'];files=[]
for name in roots:
 for p in sorted((IMPL/name).rglob('*')):
  if p==ROOT/'acceptance-manifest.json':continue
  if p.is_symlink():files.append({'path':str(p.relative_to(REPO)),'symlink':os.readlink(p)})
  elif p.is_file():files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
files.append({'path':str(doc.relative_to(REPO)),'sha256':sha(doc),'size':doc.stat().st_size})
r={'schema':1,'passed':True,'releaseAcceptance':False,'scope':'Bounded first parent anchor fix on coherent merged core/authority/AQ tuple; six native campaigns, not full shared-host/recovery/hardware/roadmap acceptance','nativeCheckExecutions':sum(v['checkExecutions'] for v in evidence),'nativeReports':evidence,'cpuChecks':24+29,'cpuMutantsRejected':5+5,'acceptedModelReport':{'path':str(model_path.relative_to(REPO)),'sha256':sha(model_path)},'namedModelScenarios':10,'modelSamples':1000,'modelMaxSteps':40,'modelMutantsRejected':6,'tuple':{'core':{'path':core['binary'],'sha256':core['binarySHA256']},'plugin':{'path':pair['binary'],'sha256':pair['binarySHA256']},'aquamarine':{'path':AQ,'sha256':AQSHA}},'failedReportsRetained':[{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for p in [failed,v87]],'ownedRoots':['implementation/'+name for name in roots],'files':files}
out=ROOT/'acceptance-manifest.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'manifest':str(out),'sha256':sha(out),'files':len(files),'nativeCheckExecutions':r['nativeCheckExecutions']}))
