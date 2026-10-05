import hashlib,json,pathlib,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
r=pathlib.Path(__file__).resolve().parents[1];out=r/'qa'/('freeze-'+str(time.time_ns()));out.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def differences(p):
 result=[]
 for base in ['src','native','adapter','assets']:
  ours={str(x.relative_to(r)) for x in (r/base).rglob('*') if x.is_file()}; theirs={str(x.relative_to(p)) for x in (p/base).rglob('*') if x.is_file()}
  for rel in sorted(ours|theirs):
   if rel not in ours or rel not in theirs or sha(r/rel)!=sha(p/rel):result.append(rel)
 return sorted(result)
try:
 a=json.loads((r/'ANCESTRY.json').read_bytes());verified={};deltas={}
 for key in ['778','786']:
  p=pathlib.Path(a[key]['path']);assert sha(p/'component-manifest.json')==a[key]['manifestSHA256']
  inventory=json.loads((p/'component-manifest.json').read_bytes())['files']
  for rel,row in inventory.items():
   assert not (p/rel).is_symlink();assert sha(p/rel)==row['sha256'];assert (p/rel).stat().st_size==row['size']
  verified[key]=len(inventory);deltas[key]=differences(p)
 assert deltas['786']==['native/host.c','native/shared-host.c','src/Desktop.elm','src/OutputController.elm','src/Surface.elm'],deltas
 assert deltas['778']==sorted(['src/Bar.elm','src/CapturedAction.elm','src/Popup.elm','src/Presentation.elm','src/SurfaceRenderer.elm','native/host.c','assets/activation.js','assets/bar-adapter.js','assets/bar.html','assets/popup-adapter.js','assets/popup.html']),deltas
 for name in ['src/Desktop.elm','src/OutputController.elm','src/Surface.elm','native/shared-host.c']:assert sha(r/name)==sha(pathlib.Path(a['778']['path'])/name)
 for name in ['src/Bar.elm','src/CapturedAction.elm','src/Popup.elm','src/Presentation.elm','src/SurfaceRenderer.elm','assets/activation.js','assets/bar-adapter.js','assets/bar.html','assets/popup-adapter.js','assets/popup.html']:assert sha(r/name)==sha(pathlib.Path(a['786']['path'])/name)
 reports={}
 for prefix in ['catalog-controls','catalog-mutations','producer-candidate','negative','tests','ownership','decoder','callback','resource','activation','build']:
  good=[p for p in sorted((r/'qa').glob(prefix+'-*/report.json')) if json.loads(p.read_bytes()).get('passed',json.loads(p.read_bytes()).get('cpuHarnessPassed',False))];assert good,prefix;reports[prefix]=good[-1]
 build=json.loads(reports['build'].read_bytes())
 for rel,wanted in build['inputs'].items():assert sha(r/rel)==wanted,rel
 for rel,wanted in build['artifacts'].items():assert sha(reports['build'].parent/rel)==wanted,rel
 assert sha(reports['build'].parent/'elm-host')==build['binarySHA256']
 for name in ['compilerDependencies','tools','linkedLibraries']:
  for path,wanted in build[name].items():assert sha(pathlib.Path(path))==wanted['sha256'],path
 for prefix in ['catalog-controls','negative']:
  for rel,wanted in json.loads(reports[prefix].read_bytes())['heldSource'].items():assert sha(r/rel)==(wanted['sha256'] if isinstance(wanted,dict) else wanted),rel
 assert len(json.loads((reports['catalog-controls'].parent/'controls.json').read_bytes())['checks'])==19
 assert len(json.loads(reports['producer-candidate'].read_bytes())['checks'])==76
 (r/'qa/current-build.json').write_text(json.dumps({'report':str(reports['build']),'reportSHA256':sha(reports['build']),'nativeAcceptance':False,'FIFOTransportGate':'OPEN'},indent=2)+'\n')
 report={'passed':True,'verifiedInventories':verified,'productionDifferencesByParent':deltas,'reports':{k:str(v) for k,v in reports.items()},'nativeAcceptance':False,'wholeGUIAcceptance':False,'packetBudgetRecoveryGate':'OPEN','FIFOTransportGate':'OPEN'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 files={}
 for p in sorted(r.rglob('*')):
  if p.is_file() and p!=r/'component-manifest.json':
   assert not p.is_symlink();files[str(p.relative_to(r))]={'sha256':sha(p),'size':p.stat().st_size}
 result=dict(report,component='814',experiment=True,files=files)
 target=r/'component-manifest.json';target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'manifest':str(target),'sha256':sha(target),'files':len(files),'report':str(out/'report.json')}))
except Exception as error:
 (out/'report.json').write_text(json.dumps({'passed':False,'error':repr(error)})+'\n');raise
