import hashlib,json,re,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1];OUT=ROOT/('proof-'+str(time.time_ns()));OUT.mkdir()
NATIVE=REPO/'implementation/elm-geometry-carrier-shared-native-v424/qa/native-1791127869741674715/report.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'scope':'Post-run actual GTK protocol configure/ACK/window-geometry/commit evidence; no MAX RGB or original full geometry campaign acceptance','inputs':{str(NATIVE):sha(NATIVE),str(Path(__file__).resolve()):sha(Path(__file__).resolve())}}
def prove(text,expected,after=-1):
 lines=text.splitlines()
 ids=re.findall(r'xdg_toplevel([#@]\d+)\.set_title\("ELM-AUTHORITY-FIXTURE"\)',text);assert len(set(ids))==1
 top=ids[0];surface=re.findall(r'xdg_surface([#@]\d+)\.get_toplevel\(new id xdg_toplevel'+re.escape(top)+r'\)',text);assert len(surface)==1;surface=surface[0]
 wl=re.findall(r'get_xdg_surface\(new id xdg_surface'+re.escape(surface)+r', wl_surface([#@]\d+)\)',text);assert len(wl)==1;wl=wl[0]
 width,height=(int(x) for x in expected);assert [width,height]==expected
 candidates=[]
 for i,line in enumerate(lines):
  if i<=after or not re.search(r'xdg_toplevel'+re.escape(top)+rf'\.configure\({width}, {height}, array\[',line):continue
  next_top=next((n for n in range(i+1,len(lines)) if re.search(r'xdg_toplevel'+re.escape(top)+r'\.configure\(',lines[n])),len(lines))
  serials=[(n,re.search(r'xdg_surface'+re.escape(surface)+r'\.configure\((\d+)\)',lines[n]).group(1)) for n in range(i+1,next_top) if re.search(r'xdg_surface'+re.escape(surface)+r'\.configure\((\d+)\)',lines[n])]
  if not serials:continue
  assert len(serials)==1
  n,serial=serials[0]
  ack=next((k for k in range(n+1,next_top) if re.search(r'-> xdg_surface'+re.escape(surface)+r'\.ack_configure\('+serial+r'\)',lines[k])),None)
  if ack is None:continue
  geometry=next((k for k in range(ack+1,next_top) if re.search(r'-> xdg_surface'+re.escape(surface)+rf'\.set_window_geometry\(0, 0, {width}, {height}\)',lines[k])),None)
  if geometry is None:continue
  commit=next((k for k in range(geometry+1,next_top) if re.search(r'-> wl_surface'+re.escape(wl)+r'\.commit\(\)',lines[k])),None)
  if commit is not None:candidates.append({'toplevel':top,'xdgSurface':surface,'wlSurface':wl,'size':[width,height],'serial':serial,'configureLine':i,'surfaceConfigureLine':n,'ackLine':ack,'geometryLine':geometry,'commitLine':commit})
 assert len(candidates)==1,{'size':expected,'candidates':candidates}
 return candidates[0]
try:
 native=json.loads(NATIVE.read_text());assert native['passed'] and native['cleanupPassed']
 log=NATIVE.parent/'native-evidence/fixture.log';assert sha(log)==native['artifacts']['native-evidence/fixture.log'];report['inputs'][str(log)]=sha(log);text=log.read_text()
 def dimensions(name):
  check=next(c for c in native['checks'] if c['name']==name);assert check['passed'];return check['after']['geometry'][2:]
 maximize=prove(text,dimensions('floatingMaximizeChangesNativeGeometryPreservingOwnership'))
 restore=prove(text,dimensions('floatingGeometryRestoreReturnsOriginalPlacementAndOwnership'),maximize['commitLine'])
 report.update(maximize=maximize,restore=restore,controls=[])
 for name,token,replacement,expected,after in [('missing-max-ack','ack_configure('+maximize['serial']+')','ack_configure(999999999)',maximize['size'],-1),('missing-restore-ack','ack_configure('+restore['serial']+')','ack_configure(999999999)',restore['size'],maximize['commitLine'])]:
  assert text.count(token)==1
  try:prove(text.replace(token,replacement),expected,after);detected=False
  except AssertionError:detected=True
  report['controls'].append({'name':name,'detected':detected});assert detected
 for path,digest in report['inputs'].items():assert sha(Path(path))==digest
 report.update(passed=True,boundedNativeClientACKQualified=True,fullGeometryCampaignAccepted=False)
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'maximize':report.get('maximize'),'restore':report.get('restore'),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
