import hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from protocol import Trace
from journal import parse
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];old=REPO/'implementation/elm-gtk-role-native-v238';failure=old/'qa/native-1791141503469881852';logs=failure/'native-evidence/gtk-role-client';out=ROOT/'qa'/('wire-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'checks':[]}
try:
 raw=(logs/'wayland.log').read_bytes();journal=(logs/'journal.jsonl').read_bytes();record=json.loads((logs/'actor.json').read_text());pid=record['process']['pid'];rows=parse(journal,pid=pid,started=record['actualStart'])
 spec=importlib.util.spec_from_file_location('unsafe238protocol',old/'qa/protocol.py');unsafe=importlib.util.module_from_spec(spec);spec.loader.exec_module(unsafe)
 assert unsafe.Trace(raw).calls==[];report['checks'].append({'name':'actual held238 trace matched zero real calls','passed':True})
 trace=Trace(raw);assert len(trace.calls)>0
 for name,sid in [('A',42),('C',71)]:
  live=next(r for r in reversed(rows) if r.get('role')==name and r.get('mapped') is True);assert live['surfaceId']==sid
  joined=trace.role(role=name,pid=pid,surface_id=sid);assert joined['bufferId']>0 and joined['ack']['index']<joined['lastCommitIndex']
  report['checks'].append({'name':name+':whole real transcript resource/configure/ACK/buffer join','passed':True,'joined':joined,'lastGtkState':live})
 report['actualCalls']=len(trace.calls);report['rawBytes']=len(raw);report['passed']=True
finally:
 paths=[Path(__file__),ROOT/'qa/protocol.py',ROOT/'qa/journal.py',old/'qa/protocol.py',logs/'wayland.log',logs/'journal.jsonl',logs/'actor.json',failure/'report.json']
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
