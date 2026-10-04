import datetime,hashlib,json,resource,re
from pathlib import Path
REPO=Path(__file__).resolve().parents[3];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
reports={}
for gui_name,qa_name in [('elm-native-popup-window-v63','elm-native-popup-qa-v64'),('elm-native-popup-lifetime-v65','elm-native-popup-lifetime-qa-v66')]:
 GUI=REPO/'implementation'/gui_name;ROOT=REPO/'implementation'/qa_name
 build=sorted((GUI/'qa').glob('build-*/report.json'))[-1];v=json.loads(build.read_text());assert v['passed']
 assert all(sha(GUI/name)==digest for name,digest in v['inputs'].items())
 reports[str(build)]={'passed':True,'sha256':sha(build),'scope':'Build/effect20/shell27 only'}
 p=sorted((ROOT/'qa').glob('native-*/report.json'))[-1];v=json.loads(p.read_text());assert v['cleanupPassed']
 assert v['passed']==(qa_name.endswith('v66'))
 assert sha(v['buildReport'])==v['buildReportSHA256']
 assert all(sha(name)==digest for name,digest in v['inputs'].items())
 for artifact in v['pair'].values():assert sha(artifact['path'])==artifact['sha256']
 log=(p.parent/'native-evidence/elm-webview.log').read_text()
 roles=re.findall(r'zwlr_layer_surface_v1[#@]([0-9]+)\.get_popup\(xdg_popup[#@]([0-9]+)\)',log);assert roles
 rectangles=[tuple(map(int,value)) for value in re.findall(r'xdg_popup[#@][0-9]+\.configure\(([0-9]+), ([0-9]+), ([0-9]+), ([0-9]+)\)',log)]
 assert rectangles and all(rect==(50,48,700,420) for rect in rectangles)
 geometry={'passed':True,'scope':'Readonly actual Wayland popup configure audit; only default unit-scale output/anchor','roles':roles,'rectangles':rectangles,'nativeReport':str(p),'nativeReportSHA256':sha(p),'logSHA256':sha(p.parent/'native-evidence/elm-webview.log')}
 (ROOT/'qa/protocol-geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
 reports[str(p)]={'passed':v['passed'],'sha256':sha(p),'checksReached':len(v['checks']),'error':v.get('error'),'cleanupPassed':True}
 for directory in [GUI,ROOT]:
  manifest={'passed':v['passed'],'inventoryVerified':True,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Native popup-window experiment; temporary native opener/raw Escape are not final Elm GUI/IME','wholeFeatureAccepted':False,'completedRequirementIds':[],'reports':dict(reports),'files':{str(p.relative_to(directory)):sha(p) for p in sorted(directory.rglob('*')) if p.is_file() and p.name!='slice-manifest.json'}}
  (directory/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(directory/'qa/slice-manifest.json')
