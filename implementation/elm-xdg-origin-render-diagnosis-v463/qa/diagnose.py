import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
held=REPO/'implementation/elm-nonzero-origin-presentation-failure-v462/qa/slice-manifest.json';assert sha(held)=='ea3657b7a15b5f7083a9cc0e4f67a989e404193a8f23f1112c251dc4f14f9290'
for e in json.loads(held.read_text())['files']:assert sha(REPO/e['path'])==e['sha256']
p=REPO/'implementation/elm-seat-focus-presented-landmarks-v461/qa/native-1791132996553890921/report.json';j=json.loads(p.read_text());capture=j['pixelCaptures'][3];args=capture['oracleArguments'];width,height=capture['dimensions'];rgbpath=p.parent/'native-evidence/origin-scale1-pixels-12/capture.rgb';rgb=rgbpath.read_bytes();assert len(rgb)==width*height*3
rx,ry,rw,rh=args['real'];gx,gy,gw,gh=args['geometry'];assert args['monitor_scale']==1 and args['monitor_origin']==[0,0]
checks=[]
def check(name,value,**data):checks.append({'name':name,'passed':bool(value),**data});assert value,name
def pixel(x,y):return list(rgb[(y*width+x)*3:(y*width+x)*3+3])
check('actualFailureAndNormalCleanup',not j['passed'] and j['cleanupPassed'] and j['error']=="AssertionError('origin-scale1:actualPresentedLandmarks')")
check('selectedOriginAndNativeBox',args['geometry']==[16,24,800,600] and args['real']==[-1,-1,800,600])
check('originalPredictionFailsFirstThreeCorners',all(s['measured'][4]['rgb']==[32,32,32] for s in capture['samples'][:3]))
red=[]
for y in range(0,80):
 for x in range(0,80):
  if pixel(x,y)==[255,48,48]:red.append((x,y))
box=[min(x for x,y in red),min(y for x,y in red),max(x for x,y in red),max(y for x,y in red)]
check('observedTopLeftRedExtent',box==[15,23,22,30],extent=box)
check('naiveSurfaceAnchorMatchesRedCenter',pixel(rx+gx+4,ry+gy+4)==[255,48,48],pixel=[rx+gx+4,ry+gy+4])
check('geometryRelativeAnchorBackground',pixel(rx+4,ry+4)==[32,32,32],pixel=[rx+4,ry+4])
# This is a frozen-image observation, never a replacement oracle or accepted transform.
check('measuredTranslationEqualsGeometryOrigin',[box[0]-rx,box[1]-ry]==[gx,gy])
owner=REPO/'implementation/maximized-stack-v1/native-core-v2/src';element=owner/'render/ElementRenderer.cpp';renderer=owner/'render/Renderer.cpp';surface=owner/'render/pass/SurfacePassElement.cpp';text=element.read_text()
check('owningSourceGeometryUVBlockDisabled','// // Adjust UV based on the xdg_surface geometry' in text and '// CBox geom = pWindow->m_xdgSurface->m_current.geometry;' in text)
check('owningRootTexBoxUsesUnshiftedRenderPosition','sc<int>(outputX) + m_data.pos.x + m_data.localPos.x' in surface.read_text())
out=ROOT/'qa'/('diagnosis-'+str(time.time_ns()));out.mkdir();inputs={str(q):sha(q) for q in [Path(__file__),held,p,rgbpath,element,renderer,surface]};report={'passed':True,'scope':'Frozen actual image landmarks and owning-source coordinate-path diagnosis; no new native run or causal patch acceptance','checks':checks,'inputs':inputs,'redExtent':box,'geometryOrigin':[gx,gy],'nativeOrigin':[rx,ry],'conclusion':'Captured red extent begins at native origin plus geometry origin. Owning root texture placement and disabled geometry UV block are candidate cause, not independently proven loaded callback causality. Preserve original oracle; evaluate geometry-aware full-surface placement and UV with shadows/subsurfaces/hit regions.','nativeAcceptance':False,'replacementOracleAccepted':False,'fullReleaseAccepted':False};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks),'redExtent':box,'report':str(out/'report.json')}))
