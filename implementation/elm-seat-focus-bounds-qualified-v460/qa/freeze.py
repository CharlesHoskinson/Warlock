import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];source=REPO/'implementation/elm-seat-focus-feasible-bounds-v459'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(p,d):assert sha(p)==d,str(p)
parent=REPO/'implementation/elm-seat-focus-bounded-acceptance-v458/qa/slice-manifest.json';verify(parent,'b76584ceca2a713776f231c1ffc1ea6afa0eed94eb8d1c04bed49bd0adc32191');held=json.loads(parent.read_text())
for e in held['files']:verify(REPO/e['path'],e['sha256'])
for e in held['symlinks']:assert str((REPO/e['path']).readlink())==e['target']
ancestor=REPO/'implementation/elm-geometry-feasible-bounds-acceptance-v209/acceptance-manifest.json';a=json.loads(ancestor.read_text());assert a['passed'] and a['nativeChecks']==604
for p,e in a['externalFiles'].items():verify(p,e['sha256'])
for p,e in a['files'].items():verify(ancestor.parent/p,e['sha256'])
old=REPO/'implementation/elm-geometry-feasible-bounds-native-v204';oldbytes=(old/'qa/native.py').read_text();expected=oldbytes.replace('elm-shared-keyboard-runtime-v435','elm-seat-focus-restored-runtime-v453').replace("REPO/'implementation/elm-geometry-coordinate-authority-v409'/path","REPO/'implementation/elm-seat-focus-geometry-pair-v451'/path").replace('freshly pinned435 core89/plugin409/AQ155 tuple','corrected453 core450/plugin451/AQ155 tuple');assert (source/'qa/native.py').read_text()==expected
assert (source/'profiles.json').read_bytes()==(old/'profiles.json').read_bytes()
for n in ['plan-test.py','error-test.py','snapshot-test.py']:assert (source/'qa'/n).read_bytes()==(old/'qa'/n).read_bytes()
plan=json.loads((source/'profiles.json').read_text())['profiles'];files=[];links=[];reports=[];native=[];synthetic=[]
for p in sorted(source.rglob('*')):
 if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
 if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
 if not p.is_file():continue
 files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
 if p.name!='report.json' or 'inputs' in p.relative_to(source).parts or 'native-evidence' in p.relative_to(source).parts:continue
 d=json.loads(p.read_text())
 for path,digest in d.get('inputs',{}).items():verify(path,digest)
 for name,digest in d.get('artifacts',{}).items():verify(p.parent/name,digest)
 row={'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':d['passed']}
 if p.parent.name.startswith('native-'):
  if not d['passed']:
   assert d['pluginMaps']['files']=={'/synthetic/plugin':'plugin'}
   assert 'buffer-byte-bound' in d['primaryError'];row['classification']='Synthetic actual-runner error-path fixture; no GUI launched';synthetic.append(row)
  else:native.append((p,d));row['classification']='Actual protected native campaign'
 else:assert d['passed'];row['classification']='CPU preflight/preservation/helper/error-path'
 reports.append(row)
assert len(native)==3 and len(synthetic)==1
seen=set();native_evidence=[];pair=held['nativePair'];expected_parts=[(372,[800,600],1,14),(186,[1600,1200],2,6),(46,[800,600],2,2)]
for (p,d),(count,mode,scale,n) in zip(native,expected_parts):
 assert d['passed'] and d['cleanupPassed'] and len(d['checks'])==count and all(c['passed'] for c in d['checks'])
 assert not d['mainDesktopActions'] and not d['profileCleanupErrors'] and not d['finalCleanupErrors']
 assert d['requestedOutput']=={'physicalMode':mode,'monitorScale':scale}
 expected={x['id'] for x in plan if x['physicalMode']==mode and x['monitorScale']==scale};actual={x['name'] for x in d['profiles']};assert actual==expected and len(actual)==n and not seen&actual;seen|=actual
 host=d['cleanup'];assert host['runtimeGone'] and not host['cleanupErrors'] and not host['remainingDescendants'] and not host['xwaylandEnabled']
 assert host['hyprlandMaps']['files'][str(Path(pair['core']['path']).resolve())]==pair['core']['sha256']
 assert d['pluginMaps']['files'][str(Path(pair['plugin']['path']).resolve())]==pair['plugin']['sha256']
 aq=host['privateAquamarine'];assert aq['mappedVerified'] and aq['mappedFiles']=={pair['aquamarine']['path']:pair['aquamarine']['sha256']}
 gates=[c for c in d['checks'] if c['name'].endswith(':actualOutputScaleAndWorkareaBeforeIntent')];assert {c['name'].split(':')[0] for c in gates}==expected
 native_evidence.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'checks':count,'profiles':sorted(actual),'physicalMode':mode,'monitorScale':scale})
assert len(seen)==22 and seen=={x['id'] for x in plan}
for p in [ROOT/'HANDOFF.md',Path(__file__).resolve()]:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
output=ROOT/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Actual corrected owning450/451/AQ155 controlled XDG geometry constraints/feasible bounds/refusal/display-scale profiles','parentManifest':str(parent),'parentManifestSHA256':sha(parent),'ancestorAcceptance':str(ancestor),'ancestorAcceptanceSHA256':sha(ancestor),'files':files,'symlinks':links,'reports':reports,'nativeEvidence':native_evidence,'nativePair':pair,'nativeAcceptance':True,'nativeCheckCount':604,'profileCount':22,'sameTupleSharedRegressionChecks':307,'nativePixelsAccepted':False,'physicalPointerAccepted':False,'gtkConstrainedConformanceAccepted':False,'fullGeometryAccepted':False,'fullReleaseAccepted':False,'completedRequirementIds':[]},indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'nativeChecks':604,'profiles':22,'manifestSHA256':sha(output)}))
