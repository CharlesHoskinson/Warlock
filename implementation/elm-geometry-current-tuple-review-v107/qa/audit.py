"""Read-only actual archive/header/source/runtime descriptor adoption audit."""
import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];I=REPO/'implementation';OUT=ROOT/'qa'/('audit-'+str(time.time_ns()));OUT.mkdir();checks=[];pins={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):p=Path(p);v=sha(p);pins[str(p)]={'sha256':v,'size':p.stat().st_size};return v
def read(p):pin(p);return json.loads(Path(p).read_text())
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
report={'passed':False,'nativeAcceptance':False,'menu09CurrentTupleAccepted':False,'scope':'Read-only existing exact tuple/header/archive/runtime evidence audit; no builds, loading or GUI','checks':checks}
try:
 cdir=I/'elm-core-parent-first-anchor-v89';cm=read(cdir/'component-manifest.json');c=read(cm['buildReport']);prior=read(c['ancestor']['report']);pdir=I/'elm-parent-first-anchor-pair-v90';pair=read(pdir/'native-build-report.json');plugin=read(pair['pluginBuildReport']);adir=I/'elm-parent-transport-retirement-v105';am=read(adir/'component-manifest.json');aq=read(am['buildReport'])
 check('core89 owning ancestor exact geometry73 component',pin(c['ancestor']['componentManifest'])=='ea95dbdcac7b61ca0c43338338ea73cf135d4b9b806fe1effb72cc9debad84bf')
 check('current core89 binary and archive exact owning report',pin(c['binary'])==c['binarySHA256'] and pin(Path(cm['buildReport']).parent/'libhyprland_lib.a')==c['archiveSHA256'])
 check('ancestor core73 archive unchanged',pin(c['ancestor']['archive'])==c['ancestor']['archiveSHA256'])
 check('694 core and plugin owning headers same ancestor',len(c['owningHeaders'])==694 and c['owningHeaders']==prior['owningHeaders']==plugin['owningHeaders'])
 for rel,digest in c['owningHeaders'].items():
  checkvalue=sha(Path(cm['buildReport']).parent/'owning-headers'/rel)==digest and sha(Path(pair['pluginBuildReport']).parent/'owning-headers'/rel)==digest
  assert checkvalue,rel
 check('all 694 actual captured core/plugin header bytes verified',True)
 old=read(Path(cm['buildReport']).parent/'ancestor-archive-payloads.json');new=read(Path(cm['buildReport']).parent/'new-archive-payloads.json');changed=[a['name'] for a,b in zip(old,new) if a!=b]
 check('one Pointer replacement retains432 exact geometry73 payloads',len(old)==len(new)==433 and changed==['PointerManager.cpp.o'] and c['unchangedArchiveMembers']==432)
 critical=['Window.cpp.o','FullscreenController.cpp.o','XDGShell.cpp.o'];report['retainedGeometryPayloads']=[a for a in new if a['name'] in critical]
 check('MAX full screen and XDG payloads retained',len(report['retainedGeometryPayloads'])==3 and all(a in old for a in report['retainedGeometryPayloads']))
 check('plugin90 exact core89 owning descriptor',pair['binary']==c['binary'] and pair['sha256']==c['binarySHA256'] and plugin['core']['sha256']==c['binarySHA256'] and pin(pair['plugin']['path'])==pair['plugin']['sha256'])
 check('152 plugin strong imports resolved owning core',plugin['strongUndefinedCount']==152 and plugin['missingSymbols']==[])
 for rel,digest in plugin['sourceLineage']['sourceFiles'].items():assert sha(pdir/rel)==sha(I/'elm-geometry-monitor-owning-pair-v75'/rel)==digest,rel
 check('negotiated native geometry source unchanged from pair75',True)
 parent=read(I/'elm-seat-publication-v79/component-manifest.json');up=read(adir/'upstream.json');check('AQ105 exact AQ79 parent component',pin(up['parent']+'/component-manifest.json')==up['parentManifestSHA256'])
 public={k:v for k,v in up['sources'].items() if k.startswith('include/')}
 for rel,digest in public.items():assert sha(adir/'candidate'/rel)==digest,rel
 check('all AQ79 public headers unchanged in AQ105',bool(public) and aq['publicHeadersUnchanged'] and aq['missingParentSymbols']==[])
 check('current AQ105 exact library report',pin(aq['library'])==aq['librarySHA256'])
 acceptance=read(I/'elm-parent-first-anchor-acceptance-v96/acceptance-manifest.json');check('historical604 firstanchor tuple bound AQ79',acceptance['passed'] and acceptance['nativeCheckExecutions']==604 and acceptance['tuple']['core']['sha256']==c['binarySHA256'] and acceptance['tuple']['plugin']['sha256']==pair['plugin']['sha256'] and acceptance['tuple']['aquamarine']['sha256']==c['aqLibrarySHA256'] and c['aqLibrarySHA256']!=aq['librarySHA256'])
 nativepath=I/'elm-parent-transport-input-v106/qa/native-1791110169811044634/report.json';native=read(nativepath);mapped=native['privateHost']['hyprlandMaps']['files'];check('actual AQ105 input159 maps current core89 and AQ105',native['passed'] and native['cleanupPassed'] and len(native['checks'])==159 and mapped[c['binary']]==c['binarySHA256'] and mapped[aq['library']]==aq['librarySHA256'])
 check('input159 does not imply loaded authority plugin',not any('elm-window-geometry-authority.so' in p for p in mapped))
 for name in ['candidate_host.py','native-build-report.json','aq-tuple.json','parent-probe-build.json']:pin(I/'elm-parent-transport-input-v106'/name)
 pin(I/'elm-geometry-family-menu-receipt-cleanup-native-v100/candidate_host.py');pin(I/'elm-geometry-family-menu-receipt-cleanup-native-v100/qa/native.py');pin(I/'elm-geometry-staged-menu-native-v77/candidate_host.py');pin(REPO/'docs/elm-roadmap/delivery/loop-state.json')
 report.update(noCoreMergeNeeded=True,tuple={'core':{'path':c['binary'],'sha256':c['binarySHA256']},'plugin':pair['plugin'],'aquamarine':{'path':aq['library'],'sha256':aq['librarySHA256']}},owningHeaders=694,unchangedArchiveMembers=432,aqPublicHeaders=len(public),pins=pins,passed=True)
except Exception as error:report['error']=repr(error)
finally:
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
