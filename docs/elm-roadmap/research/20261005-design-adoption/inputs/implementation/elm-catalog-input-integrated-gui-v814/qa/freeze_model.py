import hashlib,json,pathlib,shutil,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
root=pathlib.Path(__file__).resolve().parents[1];base=root.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p):return {'sha256':sha(p),'size':p.stat().st_size}
out=root/'qa'/('model-freeze-'+str(time.time_ns()));out.mkdir()
try:
 parent=base/'elm-batch-cache-ownership-v730';manifest=parent/'component-manifest.json';assert sha(manifest)=='896fef834db35af5137d4e0b676635b04407be894fdd0d44da7309cc2a65daae'
 inventory=json.loads(manifest.read_text())['files']
 for name,wanted in inventory.items():assert sha(parent/name)==(wanted['sha256'] if isinstance(wanted,dict) else wanted),name
 store=base/'elm-recovery-delivery-integrated-gui-v640';store_manifest=store/'component-manifest.json';assert sha(store_manifest)=='f09652e1b61b5850d9efead5ac624c4d3097a69d68470b986fd94655d52765df'
 store_inventory=json.loads(store_manifest.read_text())['files'];store_checked=0
 for name,wanted in store_inventory.items():
  if name.startswith('adapter/'):
   assert sha(store/name)==(wanted['sha256'] if isinstance(wanted,dict) else wanted),name;store_checked+=1
 producer=root/'qa/producer-1791171061378661166';assert json.loads((producer/'report.json').read_text())['passed']
 for name,entry in json.loads((producer/'held-source.json').read_text()).items():
  source=pathlib.Path(entry['source']);assert sha(source)==entry['sha256']
  if name.startswith('adapter/'):assert sha(producer/name)==entry['sha256']
 passed=[p for p in (root/'qa').glob('model-*/report.json') if json.loads(p.read_text()).get('passed')];assert passed
 selected=sorted(passed,key=lambda p:p.parent.name)[-1];assert (selected.parent/'catalog.qnt').read_bytes()==(root/'spec/catalog.qnt').read_bytes()
 model=root/'model';assert not model.exists();model.mkdir()
 shutil.copy2(root/'CONTRACT.md',model/'CONTRACT.md');shutil.copytree(root/'spec',model/'spec');shutil.copytree(producer,model/'producer');shutil.copytree(selected.parent,model/'model-evidence')
 shutil.copy2(root/'qa/model.py',model/'model-runner.py');shutil.copy2(root/'qa/producer.py',model/'producer-runner.py');shutil.copy2(root/'qa/admission-probe.c',model/'admission-probe.c')
 shutil.copy2(manifest,model/'730-component-manifest.json');shutil.copy2(store_manifest,model/'640-component-manifest.json')
 report={'passed':True,'730RowsVerified':len(inventory),'640AdapterRowsVerified':store_checked,'producerChecks':len(json.loads((producer/'report.json').read_text())['checks']),'nativeAcceptance':False,'productionLogicApproved':False,'modelReport':str(selected)}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(out/'report.json',model/'freeze-report.json')
 files={str(p.relative_to(model)):row(p) for p in sorted(model.rglob('*')) if p.is_file()}
 packet={'component':'778-model-precondition','files':files,'nativeAcceptance':False,'productionLogicApproved':False}
 target=model/'component-manifest.json';target.write_text(json.dumps(packet,indent=2)+'\n');print(json.dumps({'manifest':str(target),'sha256':sha(target),'files':len(files),'report':str(out/'report.json')}))
except Exception as error:
 (out/'report.json').write_text(json.dumps({'passed':False,'error':repr(error)})+'\n');raise
