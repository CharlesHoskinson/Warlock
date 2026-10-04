"""Freeze parent hit-test source/build and original native regressions."""
import hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;IMPL=ROOT.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def verify(base,entries):
 if isinstance(entries,dict):
  for path,digest in entries.items():assert sha(base/path)==digest,path
 else:
  for entry in entries:
   p=base/entry['path']
   if 'symlink' in entry:assert p.is_symlink() and os.readlink(p)==entry['symlink'],p
   else:assert sha(p)==entry['sha256'],p
pair_path=IMPL/'elm-parent-hit-test-pair-v64/qa/build-pair-manifest.json';pair=read(pair_path);assert pair['passed'];verify(pair_path.parent.parent,pair['files'])
core=pair['nativePair']['core'];plugin=pair['nativePair']['plugin'];assert sha(core['path'])==core['sha256'] and sha(plugin['path'])==plugin['sha256']
assert sha(core['componentManifest'])==core['componentManifestSHA256'];verify(Path(core['componentManifest']).parent,read(core['componentManifest'])['files'])
build=read(core['buildReport']);assert build['passed'] and build['unchangedArchiveMembers']==431
aq_path=IMPL/'elm-nested-input-status-v30/component-manifest.json';aq=read(aq_path);assert aq['passed'];verify(aq_path.parent,aq['files'])
aq_tuple=read(IMPL/'elm-parent-cursor-hit-test-v61/aq-tuple.json');assert sha(aq_path)==aq_tuple['manifestSHA256'] and sha(aq_tuple['library'])==aq_tuple['librarySHA256']
model_path=IMPL/'elm-parent-hit-test-model-v63/qa/model-1791103227852833622/report.json';model=read(model_path);assert model['passed'] and len(model['namedScenarios'])==10 and model['invariantSamples']==1000 and model['mutantsRejected']==5;verify(model_path.parent,model['artifacts'])
cpu_path=IMPL/'elm-core-parent-hit-test-v66/qa/test-1791103487114370575/report.json';cpu=read(cpu_path);assert cpu['passed'] and cpu['checks']==24 and cpu['mutantsRejected']==4;verify(cpu_path.parent,cpu['artifacts']);verify(Path('/'),cpu['inputs']);assert build['windowAncestor']['minimizedInputGuardPreserved']
native_paths=[(IMPL/'elm-parent-focus-hit-test-v60/qa/native-1791103880537946283/report.json',159),(IMPL/'elm-parent-multioutput-fixed-v70/qa/native-1791103839056216565/report.json',51)]
cursors=list((IMPL/'elm-parent-cursor-hit-test-v61/qa').glob('native-*/report.json'));assert len(cursors)==1;native_paths.append((cursors[0],195))
menus=list((IMPL/'elm-parent-cursor-hit-test-v61/qa').glob('menu-*/report.json'));assert len(menus)==1;native_paths.append((menus[0],68))
reports=[]
for path,count in native_paths:
 r=read(path);assert r['passed'] and r['cleanupPassed'] and not r['mainDesktopActions']
 assert len(r['checks'])==count and all(c['passed'] for c in r['checks']);verify(path.parent,r['artifacts'])
 for key in ['inputs','sourceInputs']:verify(Path('/'),r.get(key,{}))
 h=r['privateHost'];assert h['runtimeGone'] and not h['cleanupErrors'] and not h['remainingDescendants'] and not h['unexpectedInnerDescendants']
 assert h['hyprlandMaps']['files'][str(Path(core['path']).resolve())]==core['sha256']
 assert h['privateAquamarine']['mappedFiles'][str(Path(aq_tuple['library']).resolve())]==aq_tuple['librarySHA256']
 assert not h['xwaylandEnabled']
 if path.parent.name.startswith('menu-'):assert r['pluginMapsAfterLoad']['files'][str(Path(plugin['path']).resolve())]==plugin['sha256']
 if count==159:assert len(r['parentFocusCycles'])==2 and len(r['capabilityCycles'])==2
 reports.append({'path':str(path),'sha256':sha(path),'checks':count,'cleanupPassed':True,'scope':r['scope']})
failed=[]
for relative in ['elm-parent-multioutput-v53/qa/native-1791102327716067232/report.json',
 'elm-parent-multioutput-diagnostic-v54/qa/native-1791102579207540576/report.json',
 'elm-parent-multioutput-diagnostic-v56/qa/native-1791102725798943061/report.json',
 'elm-parent-multioutput-fixed-v59/qa/native-1791103068611529186/report.json',
 'elm-parent-multioutput-fixed-v65/qa/native-1791103659112745787/report.json',
 'elm-parent-multioutput-fixed-v69/qa/native-1791103771757407869/report.json',
 'elm-core-parent-hit-test-v62/qa/test-1791103315569439138/report.json',
 'elm-core-parent-hit-test-v62/build-1791103357066704160/report.json']:
 p=IMPL/relative;assert read(p)['passed'] is False;failed.append({'path':str(p),'sha256':sha(p)})
files=[];target=ROOT/'acceptance-manifest.json';assert not target.exists()
for name in ['elm-parent-multioutput-v53', 'elm-parent-multioutput-diagnostic-v54', 'elm-parent-hit-test-model-v55', 'elm-parent-multioutput-diagnostic-v56', 'elm-core-parent-hit-test-v57', 'elm-parent-hit-test-pair-v58', 'elm-parent-multioutput-fixed-v59', 'elm-parent-focus-hit-test-v60', 'elm-parent-cursor-hit-test-v61', 'elm-core-parent-hit-test-v62', 'elm-parent-hit-test-model-v63', 'elm-parent-hit-test-pair-v64', 'elm-parent-multioutput-fixed-v65', 'elm-core-parent-hit-test-v66', 'elm-parent-multioutput-fixed-v69', 'elm-parent-multioutput-fixed-v70',ROOT.name]:
 for p in sorted((IMPL/name).rglob('*')):
  if p==target:continue
  if p.is_symlink():files.append({'path':str(p.relative_to(IMPL)),'symlink':os.readlink(p)})
  elif p.is_file():files.append({'path':str(p.relative_to(IMPL)),'sha256':sha(p),'size':p.stat().st_size})
target.write_text(json.dumps({'schema':1,'passed':True,'mainDesktopActions':False,'releaseAcceptance':False,
 'scope':'Owning deferred and visible-surface-commit parent hit testing with two nested child outputs plus original focus/capability/cursor/menu campaigns',
 'pairManifest':str(pair_path),'pairManifestSHA256':sha(pair_path),'aqTuple':aq_tuple,
 'modelReport':str(model_path),'modelReportSHA256':sha(model_path),'cpuReport':str(cpu_path),'cpuReportSHA256':sha(cpu_path),
 'nativeReports':reports,'retainedFailures':failed,
 'remaining':['Queued AQ publication/callback retirement and native parent configure-generation fences','Physical multi-display/rotation, hidden GTK allocation progress and parent transport failure','Coherent geometry/shared-shell core integration, AT/IME, measured budgets and full roadmap/reversible release'],
 'files':files},indent=2)+'\n');print(json.dumps({'passed':True,'manifest':str(target),'files':len(files),'nativeChecks':473}))
