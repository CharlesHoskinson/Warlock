"""Actual219 send parser plus synthetic peer/subprocess, no socket/process/GUI."""
import hashlib,importlib.util,json,resource,time,types
from pathlib import Path
from unittest.mock import patch
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1];parent=s.parent/'elm-xdg-pointer-alignment-native-v219';p=parent/'qa/pointer.py'
spec=importlib.util.spec_from_file_location('actual219pointer',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert hashlib.sha256((parent/'component-manifest.json').read_bytes()).hexdigest()=='bec46ee86dd120a919197148436d6c7ab2f517d0c7dff5494e6214d737aada3f'
canonical='{"ready":true,"scope":"parent-notify-only"}\n{"sequence":1,"accepted":true,"scope":"parent-notify-only"}\n'
cases={
 'valid control':canonical,
 'ready integer masquerades bool':canonical.replace('"ready":true','"ready":1'),
 'accepted integer masquerades bool':canonical.replace('"accepted":true','"accepted":1'),
 'sequence float masquerades int':canonical.replace('"sequence":1','"sequence":1.0'),
 'sequence bool masquerades int':canonical.replace('"sequence":1','"sequence":true'),
 'duplicate ready key accepted':canonical.replace('"ready":true','"ready":false,"ready":true'),
 'duplicate sequence key accepted':canonical.replace('"sequence":1','"sequence":8,"sequence":1')}
session=types.SimpleNamespace(host=types.SimpleNamespace(env={},runtime=Path('/synthetic')),guard=lambda:None)
records=[]
with patch.object(m,'verify_peer',lambda *args:{'synthetic':True}):
 for name,stdout in cases.items():
  with patch.object(m.subprocess,'run',lambda *args,stdout=stdout,**kwargs:types.SimpleNamespace(stdout=stdout,stderr='',returncode=0)):
   result=m.send(session,None,{}, {},Path('/synthetic/helper'),['motion 20 30'],time.monotonic()+6)
  assert result['exitCode']==0 and result['receipts']
  records.append({'case':name,'actualParserAccepted':True,'rawStdout':stdout,'parsedReceipts':result['receipts']})
out=s/'qa'/('witness-'+str(time.time_ns()));out.mkdir();report={'diagnosisConfirmed':True,'scope':'Actual219 parser with mocked peer/subprocess and synthetic raw JSON; no socket/process/GUI/recipient acceptance','nativeAcceptance':False,'sourceSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'scriptSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'records':records};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'diagnosisConfirmed':True,'report':str(out/'report.json'),'acceptedCases':len(records)}))
