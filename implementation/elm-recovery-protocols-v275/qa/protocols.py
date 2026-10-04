"""Actual durable records, protocol partition and legacy migration compatibility."""
import copy,hashlib,json,resource,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from recovery_journal import Journal,validate,effect_protocol
from endpoint import Refused
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('protocols-'+str(time.time_ns()));OUT.mkdir()
report={'passed':False,'checks':[],'scope':'CPU durable journal only; geometry host/broker/Elm integration and native acceptance remain open','inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'adapter/recovery_journal.py',ROOT/'adapter/endpoint.py']}}
def check(name,value):
 report['checks'].append({'name':name,'passed':bool(value)});assert value,name
def refused(fn):
 try:fn()
 except (ValueError,Refused):return True
 return False
bound={'lifetime':'71','session':'2','frontend':'3'}
intent={'request':'1','generation':'2','incarnation':'4','operation':'minimize','context':{'lifetime':'71','epoch':'3','output':'5','revision':'6'}}
def record(op='minimize',schema=2,protocol=1,status='Pending'):
 r={'schema':schema,'binding':copy.deepcopy(bound),'intent':dict(copy.deepcopy(intent),operation=op),'status':status}
 if schema==2:r['effectProtocol']=protocol
 return r
def put(path,r):path.write_text(json.dumps(r));path.chmod(0o600)
try:
 with tempfile.TemporaryDirectory(prefix='elm-protocols-') as tmp:
  runtime=Path(tmp);runtime.chmod(0o700)
  with Journal(runtime,'alpha','71') as j:
   for op,p in [('minimize',1),('restore',1),('activate',1),('maximize',2),('restore-geometry',2)]:
    r=record(op,protocol=p);j.begin(bound,r['intent'],p)
    check('durableTypedPending:'+op,j.read()==r)
    frame=j.uncertain(dict(bound,session='9'));expected={'protocolVersion':3,'kind':'host-uncertain','binding':dict(bound,session='9'),'intent':r['intent']}
    if p==2:expected['effectProtocol']=2
    check('informationalUnknownExactWire:'+op,frame==expected)
    saved=(j.path/'intent.json').read_bytes()
    check('oppositeProtocolReceiptRefused:'+op,refused(lambda:j.settle({'binding':bound,'intent':r['intent'],'status':'Committed','effectProtocol':3-p})))
    check('wrongReceiptPreservesDurablePending:'+op,(j.path/'intent.json').read_bytes()==saved)
    if p==2:check('missingProtocolCannotSettleGeometry:'+op,refused(lambda:j.settle({'binding':bound,'intent':r['intent'],'status':'Committed'})))
    j.settle({'binding':bound,'intent':r['intent'],'status':'Committed','effectProtocol':p})
    check('matchedCommitSuppressesUnknown:'+op,j.uncertain(bound) is None)
   for p in [True,False,1.0,2.0,'2',0,3,None]:
    check('invalidProtocolRefused:'+repr(p),refused(lambda:validate(record('maximize',protocol=p))))
   for op,p in [('maximize',1),('restore-geometry',1),('minimize',2),('restore',2),('activate',2),('close',2)]:
    check('operationProtocolMismatchRefused:'+op+str(p),refused(lambda:validate(record(op,protocol=p))))
   for schema in [True,2.0,0,3,'2',None]:
    r=record();r['schema']=schema;check('invalidSchemaRefused:'+repr(schema),refused(lambda:validate(r)))
   legacy=record(schema=1);check('legacySchemaNormalizesToOne',effect_protocol(legacy)==1)
   j.write(legacy);check('legacyRecordRoundTripsUnchanged',j.read()==legacy)
   # A legacy host admission and new-format broker commit correlate by protocol.
   put(j.path/'host-intent.json',legacy);j.begin(bound,intent)
   j.settle({'binding':bound,'intent':intent,'status':'Committed'})
   check('legacyHostNewBrokerSettlementSuppressesUnknown',j.uncertain(bound) is None)
   geo=record('maximize',protocol=2);geo['intent']['request']='10'
   put(j.path/'host-intent.json',geo)
   check('olderLegacyCommitCannotClearGeometryAdmission',j.uncertain(bound)['intent']==geo['intent'])
   j.begin(bound,geo['intent'],2);j.settle({'binding':bound,'intent':geo['intent'],'status':'Unknown','effectProtocol':2})
   check('settledUnknownRemainsInformational',j.uncertain(bound)['effectProtocol']==2)
   # Even an invalid terminal status cannot corrupt the durable pending record.
   j.begin(bound,geo['intent'],2);before=(j.path/'intent.json').read_bytes()
   check('invalidStatusRefused',refused(lambda:j.settle({'binding':bound,'intent':geo['intent'],'status':'Success','effectProtocol':2})))
   check('invalidStatusPreservesPending',(j.path/'intent.json').read_bytes()==before)
   for field,value in [('request','0'),('generation','18446744073709551616'),('incarnation','04')]:
    bad=copy.deepcopy(geo);bad['intent'][field]=value;check('noncanonicalIntentRefused:'+field,refused(lambda:validate(bad)))
   for field in ['lifetime','epoch']:
    bad=copy.deepcopy(geo);bad['intent']['context'][field]='9';check('foreignContextRefused:'+field,refused(lambda:validate(bad)))
  with Journal(runtime,'alpha','71') as j:
   check('geometryUnknownSurvivesNewWriter',j.uncertain(dict(bound,session='10'))['effectProtocol']==2)
 report['passed']=True
except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
