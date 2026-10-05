"""Actual archive method: exact bytes/hash/identity, no reread or attribution."""
import hashlib,json,pathlib,sys,time,resource,copy,ast
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
import map_failure
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('map-failure-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False,'checks':[]}
def check(name,fn):assert fn(),name;r['checks'].append({'name':name,'passed':True})
class Failure:
 def __init__(self,evidence):self.evidence=evidence;self.reads=0
 @property
 def map_evidence(self):
  self.reads+=1
  if self.reads!=1:raise AssertionError('exception evidence reread')
  return self.evidence
try:
 raw=b'1-2 r--p 00000000 00:01 10 /same-name\n3-4 r--p 00000000 00:01 11 /same-name\n'
 evidence={'pid':100,'start':20,'raw':raw,'mapsSHA256':hashlib.sha256(raw).hexdigest()};error=Failure(evidence)
 # Forbid the API that an attempted later proc reread would use.
 original=pathlib.Path.read_bytes;pathlib.Path.read_bytes=lambda self:(_ for _ in ()).throw(AssertionError('no reread'))
 try:result=map_failure.archive(error,OUT/'actual',pid=100,start='20')
 finally:pathlib.Path.read_bytes=original
 check('exact-original-byte-artifact',lambda:(OUT/'actual/maps.raw').read_bytes()==raw)
 check('one-exception-read-no-proc-reread',lambda:error.reads==1)
 check('metadata-hash-and-owner-exact',lambda:result['mapsSHA256']==hashlib.sha256(raw).hexdigest() and result['pid']==100 and result['start']==20 and result['sameRead'] is True)
 check('no-native-or-causal-claim',lambda:result['nativeAcceptance'] is False and 'no causal attribution' in result['interpretation'])
 check('failure-before-map-read-no-artifact',lambda:map_failure.archive(Failure(None),OUT/'none',pid=None,start=None) is None and not (OUT/'none').exists())
 def refuse(change):
  value=copy.deepcopy(evidence);change(value);error=Failure(value);path=OUT/('negative-'+str(time.time_ns()))
  try:map_failure.archive(error,path,pid=100,start=20)
  except ValueError:return not path.exists()
  return False
 for name,change in [('other-pid',lambda e:e.update(pid=101)),('other-start',lambda e:e.update(start=21)),('bool-pid',lambda e:e.update(pid=True)),('bool-start',lambda e:e.update(start=True)),('text-raw',lambda e:e.update(raw=raw.decode())),('altered-hash',lambda e:e.update(mapsSHA256='0'*64)),('unknown-field',lambda e:e.update(extra=1)),('oversized-raw',lambda e:e.update(raw=b'x'*(4*1024*1024+2)))]:check(name+'-refused-before-write',lambda change=change:refuse(change))
 for name,data in [('empty',b''),('bound-detection-prefix',b'x'*(4*1024*1024+1))]:
  e={'pid':100,'start':20,'raw':data,'mapsSHA256':hashlib.sha256(data).hexdigest()}
  result=map_failure.archive(Failure(e),OUT/name,pid=100,start='20')
  check(name+'-exact-inspected-bytes-preserved',lambda name=name,data=data:(OUT/name/'maps.raw').read_bytes()==data)
  check(name+'-not-full-file-proof',lambda result=result:result['completeMapsProven'] is False)
 # Execute the real nested native exception wrapper with the ACTUAL recorded owner shape.
 from preflight import checked_guard
 guard,_=checked_guard();failure=guard.Refused('controlled maps refusal')
 original_report=ROOT.parent/'elm-own-popup-native-diagnostic-selector-v332/qa/native-1791158834072814524/report.json'
 owner=json.loads(original_report.read_text())['nativeOwner'];assert type(owner['start']) is str
 payload={'pid':owner['pid'],'start':int(owner['start']),'raw':raw,'mapsSHA256':hashlib.sha256(raw).hexdigest()};failure.map_evidence=payload
 fn=next(n for n in ast.walk(ast.parse((ROOT/'qa/native.py').read_text())) if isinstance(n,ast.FunctionDef) and n.name=='process_guard')
 class Stub:
  def __init__(self,error=None):self.error=error;self.calls=[];self.result={'same-return':True}
  def verify_process(self,**kwargs):
   self.calls.append(kwargs)
   if self.error is not None:raise self.error
   return self.result
 def wrapper(stub,directory):
  state={};namespace={'guard':stub,'owned':owner,'tuple_evidence':{'tuple':'same'},'r':state,'out':directory,'map_failure':map_failure}
  exec(compile(ast.Module(body=[fn],type_ignores=[]),str(ROOT/'qa/native.py'),'exec'),namespace);return namespace['process_guard'],state
 stub=Stub();function,state=wrapper(stub,OUT/'positive-wrapper');returned=function(100.0)
 check('actual-wrapper-positive-same-return-and-original-deadline',lambda:returned is stub.result and stub.calls==[{'pid':owner['pid'],'start':int(owner['start']),'tuple_evidence':{'tuple':'same'},'deadline':100.0}] and state=={})
 directory=OUT/'actual-owner-wrapper';directory.mkdir();function,state=wrapper(Stub(failure),directory)
 try:function(100.0)
 except BaseException as observed:check('actual-wrapper-preserves-original-refusal-object',lambda:observed is failure)
 else:raise AssertionError('wrapper did not rethrow')
 check('actual-recorded-string-owner-archives-exact-maps',lambda:(directory/'map-failure/maps.raw').read_bytes()==raw and state['sameReadMapFailure']['start']==int(owner['start']))
 real_archive=map_failure.archive
 try:
  map_failure.archive=lambda *a,**k:(_ for _ in ()).throw(OSError('controlled archive failure'))
  function,state=wrapper(Stub(failure),OUT/'IO-wrapper')
  try:function(100.0)
  except BaseException as observed:check('actual-wrapper-archive-IO-preserves-original-refusal',lambda:observed is failure and 'controlled archive failure' in state['mapFailureArchiveError'])
  else:raise AssertionError('wrapper swallowed original failure')
 finally:map_failure.archive=real_archive
 r['sourceSHA256']=hashlib.sha256((ROOT/'qa/map_failure.py').read_bytes()).hexdigest();r['passed']=True
except BaseException as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
