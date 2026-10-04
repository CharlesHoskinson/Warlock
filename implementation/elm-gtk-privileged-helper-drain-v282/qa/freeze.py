import hashlib,json,os,resource,stat,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from preflight import verify,sha
root=Path(__file__).resolve().parents[1];manifest=root/'component-manifest.json';assert not manifest.exists()
host,core,fixture,observer,probe,external=verify()
for p in root.rglob('*'):
 if p.is_file() and p.name=='report.json':
  data=json.loads(p.read_text())
  if data.get('passed') is True and 'inputs' in data:
   for path,digest in data['inputs'].items():
    # Historical reports bind their retained predecessor snapshots, not current source.
    if not str(path).startswith(str(root)):assert sha(path)==digest,path
files={}
for p in sorted(root.rglob('*')):
 if p.is_file():files[str(p.relative_to(root))]={'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullCampaignPassed':False,'diagnosticBootstrapOnly':True,'scope':'Reviewed actual GTK bootstrap source/CPU closure only; no GUI by source owner, GTK01-08 mandatory open','files':files,'externalFiles':external,'selectedNativeTuple':{'core':core['binary'],'coreSHA256':core['sha256'],'authority':core['plugin'],'observer':{'path':observer['binary'],'sha256':observer['binarySHA256']},'gtk':fixture['artifact'],'parentInput':probe},'remainingScenarios':['GTK01','GTK02','GTK03','GTK04','GTK05','GTK06','GTK07','GTK08'],'defaultRefusalReport':str(root/'qa/native-1791140937813514436/report.json'),'invocation':'python3 -B implementation/elm-build-loop-v1/loop.py native --runner '+str(root/'qa/native.py')+' -- --diagnostic-bootstrap'}
for name,row in files.items():assert sha(root/name)==row['sha256'],name
for path,digest in external.items():assert sha(path)==digest,path
manifest.write_text(json.dumps(packet,indent=2)+'\n');print(json.dumps({'passed':True,'manifest':str(manifest),'sha256':sha(manifest),'ownedFiles':len(files),'externalFiles':len(external),'nativeAcceptance':False}))
