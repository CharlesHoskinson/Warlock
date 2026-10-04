"""Freeze the owning event-loop reload fix and original native regressions."""
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
pair_path=IMPL/'elm-monitor-reload-pair-v49/qa/build-pair-manifest.json';pair=read(pair_path);assert pair['passed'];verify(pair_path.parent.parent,pair['files'])
core=pair['nativePair']['core'];plugin=pair['nativePair']['plugin'];assert sha(core['path'])==core['sha256'] and sha(plugin['path'])==plugin['sha256']
assert sha(core['componentManifest'])==core['componentManifestSHA256'];verify(Path(core['componentManifest']).parent,read(core['componentManifest'])['files'])
build=read(core['buildReport']);assert build['passed'] and build['unchangedArchiveMembers']==432
aq_path=IMPL/'elm-nested-input-status-v30/component-manifest.json';aq=read(aq_path);assert aq['passed'];verify(aq_path.parent,aq['files'])
aq_tuple=read(IMPL/'elm-parent-cursor-monitor-v51/aq-tuple.json');assert sha(aq_path)==aq_tuple['manifestSHA256'] and sha(aq_tuple['library'])==aq_tuple['librarySHA256']
model_path=IMPL/'elm-monitor-reload-model-v48/qa/model-1791101066590058691/report.json';model=read(model_path);assert model['passed'] and len(model['namedScenarios'])==6 and model['invariantSamples']==1000 and model['lateClearMutationRejected'];verify(model_path.parent,model['artifacts'])
cpu_path=IMPL/'elm-core-monitor-reload-v47/qa/test-1791101066587506241/report.json';cpu=read(cpu_path);assert cpu['passed'] and cpu['checks']==14 and cpu['lateClearMutationRejected'];verify(cpu_path.parent,cpu['artifacts']);verify(Path('/'),cpu['inputs'])
native_paths=[(IMPL/'elm-parent-focus-monitor-v50/qa/native-1791101305761063968/report.json',159),
              (IMPL/'elm-parent-cursor-monitor-v51/qa/native-1791101387874193409/report.json',195)]
menus=list((IMPL/'elm-parent-cursor-monitor-v51/qa').glob('menu-*/report.json'));assert len(menus)==1;native_paths.append((menus[0],68))
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
for relative in ['elm-parent-focus-v44/qa/native-1791100162878095039/report.json','elm-parent-focus-v46/qa/native-1791100365155458299/report.json']:
 p=IMPL/relative;assert read(p)['passed'] is False;failed.append({'path':str(p),'sha256':sha(p)})
files=[];target=ROOT/'acceptance-manifest.json';assert not target.exists()
for name in ['elm-core-monitor-reload-v47','elm-monitor-reload-model-v48','elm-monitor-reload-pair-v49','elm-parent-focus-monitor-v50','elm-parent-cursor-monitor-v51',ROOT.name]:
 for p in sorted((IMPL/name).rglob('*')):
  if p==target:continue
  if p.is_symlink():files.append({'path':str(p.relative_to(IMPL)),'symlink':os.readlink(p)})
  elif p.is_file():files.append({'path':str(p.relative_to(IMPL)),'sha256':sha(p),'size':p.stat().st_size})
target.write_text(json.dumps({'schema':1,'passed':True,'mainDesktopActions':False,'releaseAcceptance':False,
 'scope':'Owning core reload progress under full private parent cover plus original pointer/cursor/menu campaigns',
 'pairManifest':str(pair_path),'pairManifestSHA256':sha(pair_path),'aqTuple':aq_tuple,
 'modelReport':str(model_path),'modelReportSHA256':sha(model_path),'cpuReport':str(cpu_path),'cpuReportSHA256':sha(cpu_path),
 'nativeReports':reports,'retainedFailures':failed,
 'remaining':['Queued AQ publication/callback retirement and native parent configure-generation fences','Multiple outputs/rotation, physical devices and parent transport failure','Coherent geometry/shared-shell core integration, AT/IME, measured budgets and full roadmap/reversible release'],
 'files':files},indent=2)+'\n');print(json.dumps({'passed':True,'manifest':str(target),'files':len(files),'nativeChecks':422}))
