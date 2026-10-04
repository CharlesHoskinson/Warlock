"""Freeze source, owning ABI, native regressions and preserved failed evidence."""
import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify_rows(base,entries):
 if isinstance(entries,dict):entries=[{'path':k,**(v if isinstance(v,dict) else {'sha256':v})} for k,v in entries.items()]
 for r in entries:
  p=base/r['path'];target=r.get('symlink',r.get('target'))
  if target is not None:assert p.is_symlink() and os.readlink(p)==target,str(p)
  else:assert sha(p)==r['sha256'],str(p)
reports=[]
native=[('elm-keyboardless-menu-capability-v209',83),('elm-keyboardless-menu-focus-v210',83),('elm-keyboardless-geometry-regression-v211',161),('elm-keyboardless-reconnect-regression-v212',57),('elm-keyboardless-full-menu-regression-v214',89)]
for name,count in native:
 paths=list((REPO/'implementation'/name/'qa').glob('native-*/report.json'));assert len(paths)==1
 p=paths[0];m=json.loads(p.read_text());assert m['passed'] and m['cleanupPassed'] and len(m['checks'])==count and all(v['passed'] for v in m['checks']) and not m['mainDesktopActions']
 for rel,digest in m['artifacts'].items():assert sha(p.parent/rel)==digest
 reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'checks':count,'kind':'actual GUI507 regression','passed':True})
paths=sorted((REPO/'implementation/elm-keyboardless-bounds-regression-v215/qa').glob('native-*/report.json'));assert len(paths)==3
bounds=0
for p in paths:
 m=json.loads(p.read_text());assert m['passed'] and m['cleanupPassed'] and all(v['passed'] for v in m['checks']) and not m['mainDesktopActions']
 for rel,digest in m['artifacts'].items():assert sha(p.parent/rel)==digest
 bounds+=len(m['checks']);reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'checks':len(m['checks']),'kind':'controlled XDG bounds with standalone adapter183','passed':True})
assert bounds==604
source=REPO/'implementation/elm-keyboardless-focus-source-held-v204/qa/slice-manifest.json';s=json.loads(source.read_text());assert s['passed'] and s['modelNamed']==17 and s['modelTraces']==1000 and s['modelControls']==9 and s['actualMethodChecks']==22 and s['actualMethodControls']==7
verify_rows(REPO,s['files'])
core=REPO/'implementation/elm-core-keyboardless-focus-v205/component-manifest.json';c=json.loads(core.read_text());assert c['sourceHeld'] and c['evidenceIntegrityPassed'];verify_rows(core.parent,c['files']);assert sha(c['buildReport'])==c['buildReportSHA256'];b=json.loads(Path(c['buildReport']).read_text());assert b['passed']
for name in ['elm-keyboardless-focus-owning-pair-v206','elm-keyboardless-focus-owning-observer-v207']:
 p=next((REPO/'implementation'/name/'qa').glob('build-*/report.json'));m=json.loads(p.read_text());assert m['passed'] and not m['missingSymbols'] and len(m['owningHeaders'])==694
 for rel,digest in m['artifacts'].items():assert sha(p.parent/rel)==digest
 reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'kind':'owning ABI build','passed':True})
runtime=REPO/'implementation/elm-keyboardless-focus-runtime-v208/qa/build-pair-manifest.json';r=json.loads(runtime.read_text());assert r['passed'];verify_rows(runtime.parent.parent,r['files']);assert sha(r['owningCoreComponent'])==r['owningCoreComponentSHA256']
ancestor=REPO/'implementation/elm-native-escape-bounded-acceptance-v195/acceptance-manifest.json';assert sha(ancestor)=='66234d3c8bffaf9ee3043fc481da7332eee99f2e219e61282b9bffc7b8273232'
files=[]
names=['elm-keyboardless-popup-focus-v196','elm-keyboardless-focus-model-v199','elm-keyboardless-focus-source-v200','elm-keyboardless-focus-model-v201','elm-keyboardless-focus-compile-v202','elm-keyboardless-method-controls-v203','elm-keyboardless-focus-source-held-v204','elm-core-keyboardless-focus-v205','elm-keyboardless-focus-owning-pair-v206','elm-keyboardless-focus-owning-observer-v207','elm-keyboardless-focus-runtime-v208','elm-keyboardless-menu-capability-v209','elm-keyboardless-menu-focus-v210','elm-keyboardless-geometry-regression-v211','elm-keyboardless-reconnect-regression-v212','elm-keyboardless-focus-bounded-acceptance-v213','elm-keyboardless-full-menu-regression-v214','elm-keyboardless-bounds-regression-v215']
for name in names:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  if p==ROOT/'acceptance-manifest.json':continue
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if p.is_symlink():row['symlink']=os.readlink(p)
  elif p.is_file():row.update(sha256=sha(p),size=st.st_size)
  elif p.is_dir():continue
  else:raise RuntimeError('Unexpected special file '+str(p))
  files.append(row)
manifest={'schema':1,'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'boundedNativeAcceptance':True,'keyboardCapabilityLossAcceptance':True,'keyboardFocusLossAcceptance':True,'acceptedGuiNativeCheckCount':473,'acceptedControlledBoundsCheckCount':604,'acceptedNativeCheckCount':1077,'fullRoadmapAccepted':False,'fullReleaseAccepted':False,'nativePair':r['nativePair'],'observerBuild':reports[-1],'gui':'implementation/elm-projection-native-escape-combined-v507','fixture':'implementation/elm-projection-current-broker-fixture-v511','sourceGate':str(source),'sourceGateSHA256':sha(source),'ancestorAcceptance':str(ancestor),'ancestorAcceptanceSHA256':sha(ancestor),'reports':reports,'files':files,'scope':'Core205 focus correction/plugin206/AQ155/observer207/GUI507/fixture511 bounded actual menu473 plus standalone controlled XDG bounds604; every original deadline/oracle preserved. No full release, GTK, hardware, AT/IME or pointer-race acceptance inferred.'}
with (ROOT/'acceptance-manifest.json').open('x') as f:f.write(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'acceptedNativeChecks':1077,'actualGuiChecks':473,'manifestSHA256':sha(ROOT/'acceptance-manifest.json')}))
