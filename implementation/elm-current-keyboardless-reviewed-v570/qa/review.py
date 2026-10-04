import hashlib,json,os,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(path,base):
 j=json.loads(path.read_text())
 rows=j['files'];rows=[{'path':p,**r} for p,r in rows.items()] if isinstance(rows,dict) else rows
 for row in rows:
  p=base/row['path'];target=row.get('symlink',row.get('target'))
  if target is not None:assert p.is_symlink() and str(p.readlink())==target
  else:assert sha(p)==row['sha256'],str(p)
 links=j.get('symlinks',[]);links=[{'path':k,'target':v} for k,v in links.items()] if isinstance(links,dict) else links
 for row in links:assert str((base/row['path']).readlink())==row['target']
 return j
p=REPO/'implementation/elm-keyboardless-current-acceptance-v222/acceptance-manifest.json';assert sha(p)=='bbb42789486071600535cf66d4ba869722530c6fe590cc7f1af72a203fc80fe4';accepted=verify(p,REPO);assert accepted['boundedNativeAcceptance'] and not accepted['fullReleaseAccepted'] and not accepted['toolkitNativeAcceptance'];assert accepted['acceptedGuiNativeCheckCount']==473
reports=[]
for row in accepted['reports']:
 path=REPO/row['path'];assert sha(path)==row['sha256'];j=json.loads(path.read_text());assert j['passed'] and j['cleanupPassed'] and not j['mainDesktopActions'];assert j['pair']==accepted['nativePair'];assert all(c['passed'] for c in j['checks']) and len(j['checks'])==row['checks'];assert j['buildReport']==str(REPO/'implementation/elm-stable-surface-publication-v521/qa/build-1791138800386580258/report.json')
 for rel,digest in j['artifacts'].items():assert sha(path.parent/rel)==digest
 reports.append({'path':str(path.relative_to(REPO)),'sha256':sha(path),'checks':len(j['checks'])})
assert sum(r['checks'] for r in reports)==473
for row in accepted['nativePair'].values():assert sha(row['path'])==row['sha256']
core=REPO/'implementation/elm-core-keyboardless-focus-v205/component-manifest.json';assert sha(core)=='81dbdd89a0f650f075f96ec435e271d9b997458ce5bbc94d437e684c67ef6852';c=verify(core,core.parent);build=Path(c['buildReport']);assert sha(build)==c['buildReportSHA256'];b=json.loads(build.read_text());assert b['passed'] and b['unchangedArchiveMembers']==432 and set(b['rebuiltArchiveMembers'])=={'SeatManager.cpp.o'} and b['existingPublicHeadersUnchanged'] and b['geometryAndReloadArchivePayloadsPreserved'];assert len(b['owningHeaders'])==694 and b['exportClosure']['ancestorCount']==b['exportClosure']['candidateCount']==13412 and b['exportClosure']['missingSymbols']==[]
for section in ['dependencies','linkDependencies','linkedLibraries','tools']:
 for path,digest in b[section].items():assert sha(path)==digest
observer=Path(accepted['toolkitObserverCompiled']);assert sha(observer)==accepted['toolkitObserverCompiledSHA256'];o=verify(observer,observer.parent);assert o['compiled'] and not o['nativeAcceptance'];ob=Path(o['buildReport']);assert sha(ob)==o['buildReportSHA256'];oj=json.loads(ob.read_text());assert oj['core']['sha256']==accepted['nativePair']['core']['sha256'] and len(oj['owningHeaders'])==694 and not oj['missingSymbols']
for path,row in o['externalFiles'].items():assert sha(path)==row['sha256']
result={'passed':True,'scope':'Independent exact source/ABI and five actual native report review of current521 owning205 tuple; no new native campaign and no fullrelease','nativeAcceptance':False,'adoptedBoundedNativeEvidence':True,'reviewedNativeChecks':473,'source':'implementation/elm-stable-surface-publication-v521','nativePair':accepted['nativePair'],'reviewedManifest':str(p.relative_to(REPO)),'reviewedManifestSHA256':sha(p),'reviewedReports':reports,'toolkitObserver':str(observer),'toolkitObserverSHA256':sha(observer),'toolkitNativeAcceptance':False,'unchangedArchiveMembers':432,'rebuiltArchiveMembers':['SeatManager.cpp.o'],'fullReleaseAccepted':False,'completedRequirementIds':[]}
out=ROOT/'qa/report.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'reviewedNativeChecks':473,'report':str(out)}))
