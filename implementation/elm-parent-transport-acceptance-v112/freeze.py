import hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  while chunk:=f.read(1024*1024):h.update(chunk)
 return h.hexdigest()
names=['elm-parent-transport-fixture-v98','elm-parent-transport-fixture-fixed-v99','elm-parent-transport-native-v100',
 'elm-parent-transport-retirement-v101','elm-parent-transport-retirement-v102','elm-parent-transport-retirement-v103',
 'elm-parent-transport-native-v104','elm-parent-transport-retirement-v105','elm-parent-transport-input-v106',
 'elm-parent-transport-multi-v107','elm-parent-transport-geometry-v108','elm-parent-transport-menu-v109',
 'elm-parent-transport-burst-v110','elm-parent-transport-native-v111','elm-parent-transport-acceptance-v112']
def report(path,passed=True):
 p=Path(path);x=json.loads(p.read_text());assert x['passed'] is passed,p
 for rel,digest in x.get('artifacts',{}).items():assert sha(p.parent/rel)==digest,(p,rel)
 for source,digest in x.get('inputs',{}).items():
  # Native input maps have absolute keys; fixture compile uses relative keys.
  if Path(source).is_absolute():assert sha(source)==digest,source
 return {'path':str(p),'sha256':sha(p),'checks':len(x.get('checks',[]))},x
def latest(root,pattern):return sorted((REPO/'implementation'/root).glob(pattern))[-1]
component=REPO/'implementation/elm-parent-transport-retirement-v105/component-manifest.json'
c=json.loads(component.read_text());assert c['passed'] and not c['nativeAcceptance'] and not c['releaseAcceptance']
for f in c['files']:
 p=component.parent/f['path']
 if 'symlink' in f:assert p.is_symlink() and os.readlink(p)==f['symlink']
 else:assert sha(p)==f['sha256'],p
build=json.loads(Path(c['buildReport']).read_text());assert build['passed'] and build['publicHeadersUnchanged'] and not build['missingParentSymbols']
assert sha(build['library'])==build['librarySHA256']
native=[]
campaigns=[('elm-parent-transport-native-v111','native-*',26),('elm-parent-transport-input-v106','native-*',159),
 ('elm-parent-transport-multi-v107','native-*',51),('elm-parent-transport-geometry-v108','native-*',96),
 ('elm-parent-transport-menu-v109','menu-*',68),('elm-parent-transport-menu-v109','native-*',195),
 ('elm-parent-transport-burst-v110','native-*',35)]
for root,pattern,count in campaigns:
 entry,x=report(latest(root,'qa/'+pattern+'/report.json'));assert x['cleanupPassed'] and len(x['checks'])==count
 assert all(v['passed'] for v in x['checks'])
 mapped=x['privateHost']['hyprlandMaps']['files'];assert mapped[str(Path(build['library']).resolve())]==build['librarySHA256']
 native.append(entry)
baseline,b=report(latest('elm-parent-transport-native-v100','qa/native-*/report.json'),False)
assert b['cleanupPassed'] and b['lastDevicesAfterLoss']['mice'] and b['lastDevicesAfterLoss']['keyboards']
failedFixture,_=report(latest('elm-parent-transport-fixture-v98','build-*/report.json'),False)
failedNative,n=report(latest('elm-parent-transport-native-v104','qa/native-*/report.json'),False);assert n['cleanupPassed'] and n['error'].startswith('FileNotFoundError')
for version in [102,103]:
 _,f=report(latest('elm-parent-transport-retirement-v'+str(version),'build-*/report.json'),False)
 assert f['publicHeadersUnchanged'] and len(f['missingParentSymbols'])==1 and '_M_emplace_uniq' in f['missingParentSymbols'][0]
cpu,x=report(latest('elm-parent-transport-retirement-v105','qa/replay-*/report.json'));assert x['candidateChecks']==63 and x['mutantsRejected']==7
model,x=report(latest('elm-parent-transport-retirement-v105','qa/model-*/report.json'));assert len(x['namedScenarios'])==10 and x['mutantsRejected']==8 and x['invariantSamples']==1000 and x['maxSteps']==40
# Regressions change only the declared library tuple and explanatory scope text;
# retain every original assertion, deadline, identity and pixel/input oracle.
priorPairs=[('elm-parent-first-anchor-input-v92','elm-parent-transport-input-v106'),
 ('elm-parent-first-anchor-multi-v94','elm-parent-transport-multi-v107'),
 ('elm-parent-first-anchor-geometry-v95','elm-parent-transport-geometry-v108'),
 ('elm-parent-first-anchor-menu-v93','elm-parent-transport-menu-v109'),
 ('elm-parent-first-anchor-native-v91','elm-parent-transport-burst-v110')]
for old,new in priorPairs:
 source=REPO/'implementation'/old;target=REPO/'implementation'/new
 for p in source.iterdir():
  if p.is_file() and p.name!='aq-tuple.json':assert sha(p)==sha(target/p.name),p
 for p in (source/'qa').glob('*.py'):
  expected=p.read_text().replace('guarded V79 AQ','transport-retiring V105 AQ').replace('guarded79 AQ','transport105 AQ').replace('guarded V79 AQ','transport105 AQ').replace('guarded V79','transport-retiring V105')
  assert (target/'qa'/p.name).read_text()==expected,p
files={};links={}
for name in names:
 base=REPO/'implementation'/name
 for p in sorted(base.rglob('*')):
  if p==ROOT/'acceptance-manifest.json':continue
  if p.is_symlink():links[str(p.relative_to(REPO))]=os.readlink(p)
  elif p.is_file():files[str(p.relative_to(REPO))]={'sha256':sha(p),'size':p.stat().st_size}
doc=REPO/'docs/elm-roadmap/delivery/PARENT-TRANSPORT-V112-ACCEPTANCE.md';files[str(doc.relative_to(REPO))]={'sha256':sha(doc),'size':doc.stat().st_size}
result={'schema':1,'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'releaseAcceptance':False,
 'scope':'Exact private focused-child unheld transport loss plus six original normal campaigns on core89/plugin90/AQ105. No full transport recovery/held-loss/physical/GPU/AT/IME/S01-S16/release acceptance.',
 'componentManifest':str(component),'componentManifestSHA256':sha(component),'nativeReports':native,
 'nativeCheckExecutions':sum(v['checks'] for v in native),'cpuReport':cpu,'modelReport':model,
 'preservedFailures':[baseline,failedFixture,failedNative],'files':files,'symlinks':links}
p=ROOT/'acceptance-manifest.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'manifest':str(p),'sha256':sha(p),'files':len(files),'nativeCheckExecutions':result['nativeCheckExecutions']}))
