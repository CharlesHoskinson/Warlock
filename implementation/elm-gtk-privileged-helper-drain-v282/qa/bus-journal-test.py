"""Actual activation snapshot decoder hostile boundaries; no GUI/bus effects."""
import copy,hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from private_bus import Activations,Refused
ROOT=Path(__file__).resolve().parent;OUT=ROOT/('bus-journal-'+str(time.time_ns()));OUT.mkdir();proof=json.loads((ROOT/'private-bus-1791147578802060564/activation-inventory.json').read_text());record=proof['services'][0];source=next(Path(record['journalDirectory']).glob('*.jsonl'));original=source.read_bytes();rows=[json.loads(x) for x in original.split(b'\n') if x];path=OUT/'journal.jsonl';record=copy.deepcopy(record);record['journalDirectory']=str(OUT);manager=object.__new__(Activations);manager.records=[record];checks=[];report={'passed':False,'nativeAcceptance':False,'checks':checks}
try:
 cases=[('valid',original,True)]
 for name,mutation in [('boolseq',lambda r:r[0].update(sequence=True)),('boolpid',lambda r:r[0]['identity'].update(pid=True)),('extra',lambda r:r[0].update(extra=0)),('badstatus',lambda r:next(x for x in r if x['kind']=='child-exit').update(waitStatus=12345)),('numericcancel',lambda r:r[-1].update(cancelled=1)),('nonfiniteerror',lambda r:r[-1].update(error=1e400)),('boolchildexit',lambda r:r[-1].update(childExitCode=True)),('boolruid',lambda r:r[0]['identity'].update(realUid=True)),('wrongrealuid',lambda r:r[0]['identity'].update(realUid=0)),('negativeeuid',lambda r:r[0]['identity'].update(effectiveUid=-1)),('numericprivilege',lambda r:r[0]['identity'].update(privilegedCredentials=1)),('wrongprivilegeclass',lambda r:r[0]['identity'].update(privilegedCredentials=True)),('missingcredentials',lambda r:r[0]['identity'].pop('savedUid')),('exitobservedwrongstart',lambda r:next(x for x in r if x['kind']=='child-exit')['observedIdentity'].update(start='1'))]:
  changed=copy.deepcopy(rows);mutation(changed);cases.append((name,('\n'.join(json.dumps(r) for r in changed)+'\n').encode(),False))
 cases += [('duplicateseq',original.replace(b'"sequence": 1',b'"sequence": 1,"sequence": 1',1),False),('partialterminal',original[:-1],False),('laterrecord',original+json.dumps(rows[0]).encode()+b'\n',False)]
 for name,raw,expected in cases:
  path.write_bytes(raw);accepted=True
  try:result=manager.snapshots()
  except Refused:accepted=False
  assert accepted is expected,name;checks.append({'name':name,'passed':True,'accepted':accepted})
 report['passed']=True
finally:
 path.write_bytes(original);report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'private_bus.py',source,ROOT/'activation-supervisor.py']};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
