import copy,hashlib,json,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('tests-'+str(time.time_ns()));OUT.mkdir()
checks=[];commands=[]
try:
 CAP=REPO/'implementation/elm-recovery-context-feedback-v592/qa/replay-1791146043447506188/captured-frames.json'
 captured=json.loads(CAP.read_text());shutil.copy2(CAP,OUT/'captured573-frames.json')
 frames={item['frame']['kind']:copy.deepcopy(item['frame']) for item in captured}
 old=copy.deepcopy(frames['attached']['binding']);current={**old,'frontend':'2'};frames['attached']['binding']=current
 record={'schema':2,'effectProtocol':1,'binding':old,'intent':frames['host-uncertain']['intent'],'status':'Unknown'}
 proof={'protocolVersion':3,'kind':'binding-retirement','retirementProtocol':1,'operation':'retire','binding':current,'queriedBinding':old,'requestId':'31','sequence':'777','grantState':'Retired'}
 native=lambda frame:{'kind':'native','frame':copy.deepcopy(frame)}
 def read(kind,request,bound=current,revision=None):
  f=copy.deepcopy(frames[kind]);f['requestId']=str(request);f['binding']=copy.deepcopy(bound)
  if kind=='action-projection':
   f['context']['lifetime']=bound['lifetime'];f['context']['epoch']=bound['frontend']
   if revision is not None:f['context']['revision']=str(revision);f['scene']['revision']=str(revision)
  elif kind=='geometry-facts':
   if revision is not None:f['revision']=str(revision)
   f['sequence']=str(int(f['sequence'])+request)
  return f
 prefix=[native(frames['attached']),native(read('action-projection',1)),native(frames['host-geometry-negotiate']),native(read('geometry-attached',2)),native(read('geometry-facts',3))]
 unknown={'protocolVersion':3,'kind':'host-reservation-unknown','binding':current,'record':record}
 act=read('action-projection',4);geo=read('geometry-facts',5,revision=int(frames['geometry-facts']['revision'])+10)
 observation={'actionRequestId':'4','geometryRequestId':'5','actionContext':act['context'],'geometryContext':{'lifetime':current['lifetime'],'epoch':current['frontend'],'output':geo['outputGeneration'],'revision':geo['revision']}}
 release={'protocolVersion':3,'kind':'host-reservation-released','binding':current,'record':record,'release':{'id':'0123456789abcdef'*4,'proof':proof,'observation':observation}}
 base=prefix+[native(unknown),native(proof),native(act),native(geo)]
 inputs=OUT/'inputs';shutil.copytree(ROOT/'src',inputs/'src');shutil.copy2(ROOT/'elm.json',inputs/'elm.json');shutil.copy2(ROOT/'qa/Probe.elm',inputs/'src/Probe.elm')
 commands=[];checks=[]
 def command(name,cmd,cwd):
  p=subprocess.run(cmd,cwd=cwd,capture_output=True,timeout=180);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);commands.append({'name':name,'command':cmd,'cwd':str(cwd),'exitCode':p.returncode});assert p.returncode==0,p.stderr.decode();return p
 command('compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Probe.elm','--optimize','--output='+str(OUT/'worker.js')],inputs)
 def run(name,events):
  (OUT/(name+'-events.json')).write_text(json.dumps(events,indent=2)+'\n');command(name,['node',str(ROOT/'qa/probe.cjs'),str(OUT/'worker.js'),str(OUT/(name+'-events.json')),str(OUT/(name+'-rows.json'))],ROOT);return json.loads((OUT/(name+'-rows.json')).read_text())
 def check(name,value):
  checks.append({'name':name,'passed':bool(value)});assert value,name
 rows=run('valid',base+[native(release),{'kind':'checkpoint'},{'kind':'act2'}]);before=rows[-4];after=rows[-3]
 check('full-origin-Unknown-blocks-before-release',rows[5]['blocked'] and rows[5]['unresolved']==1)
 check('ready-ack-precedes-both-frontend-read-requests',[w['kind'] for w in rows[6]['wires']]==['reconciliation-ready','projection-request','geometry-facts-request'])
 check('proof-and-current-reads-do-not-release',before['blocked'])
 check('full-correlated-release-removes-live-reservation',not after['blocked'] and after['unresolved']==0)
 check('historical-Unknown-transaction-kept',after['transaction']['transaction']==before['transaction']['transaction'] and after['transaction']['transaction']['status']=='Unknown')
 check('release-does-not-consume-any-counter',after['effectRequest']==before['effectRequest'] and after['effectGeneration']==before['effectGeneration'] and after['shellRequest']==before['shellRequest'])
 check('release-emits-no-effect-or-refresh',after['wires']==[])
 check('only-new-explicit-intent-can-send',len(rows[-1]['wires'])==1 and rows[-1]['wires'][0]['kind']=='window-effect' and rows[-1]['effectRequest']=='13')
 for name,path,bad in [
  ('foreign-current',['binding','session'],'999'),('foreign-old',['record','binding','session'],'999'),('stale-proof',['release','proof','requestId'],'30'),('changed-proof-sequence',['release','proof','sequence'],'778'),('stale-action-id',['release','observation','actionRequestId'],'1'),('stale-geometry-id',['release','observation','geometryRequestId'],'3'),('stale-own-geometry-revision',['release','observation','geometryContext','revision'],'1'),('foreign-action-output',['release','observation','actionContext','output'],'999'),('bool-id',['release','observation','actionRequestId'],True),('overflow-id',['release','proof','sequence'],'18446744073709551616'),('invented-committed',['record','status'],'Committed')]:
  f=json.loads(json.dumps(release));o=f
  for part in path[:-1]:o=o[part]
  o[path[-1]]=bad
  result=run(name,base+[native(f)]);check(name+'-keeps-live-reservation-and-counters',result[-1]['blocked'] and result[-1]['unresolved']==1 and result[-1]['effectRequest']=='12' and not result[-1]['wires'])
 for name,events in [('no-proof',prefix+[native(unknown),native(release)]),('no-geometry',base[:-1]+[native(release)]),('pre-proof-reads',prefix+[native(unknown),native(proof),native(release)]),('legacy-origin',prefix[:1]+[native({**frames['host-uncertain'],'binding':current})]+prefix[1:]+[native(unknown),native(proof),native(act),native(geo),native(release)])]:
  result=run(name,events);check(name+'-cannot-release',result[-1]['blocked'] and not result[-1]['wires'])
 # A retry invalidates accepted domains before the new matching replies arrive.
 result=run('retry-pending',base+[{'kind':'refresh'},native(release)]);check('retry-pending-invalidates-prior-read-qualification',result[-1]['blocked'])
 retryAct=read('action-projection',6);retryGeo=read('geometry-facts',7,revision=int(geo['revision'])+1)
 retryRelease=json.loads(json.dumps(release));retryRelease['release']['observation']={'actionRequestId':'6','geometryRequestId':'7','actionContext':retryAct['context'],'geometryContext':{'lifetime':current['lifetime'],'epoch':current['frontend'],'output':retryGeo['outputGeneration'],'revision':retryGeo['revision']}}
 result=run('retry-complete',base+[{'kind':'refresh'},native(retryAct),native(retryGeo),native(retryRelease)]);check('latest-both-accepted-retries-can-release',not result[-1]['blocked'])
 # Exact duplicate proof cannot issue another acknowledgement or refresh.
 result=run('duplicate-proof',base+[native(proof)]);check('duplicate-proof-has-no-automatic-read-replay',not result[-1]['wires'] and result[-1]['blocked'])
 (OUT/'report.json').write_text(json.dumps({'passed':True,'checks':checks,'commands':commands,'nativeAcceptance':False,'fixture':'Synthetic post-proof trajectory derived from preserved573 observation payloads; no claimed captured durable release','sourceSHA256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'src').glob('*.elm')}},indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks),'report':str(OUT/'report.json')}))
except BaseException as error:
 (OUT/'failure.json').write_text(json.dumps({'passed':False,'error':repr(error),'checks':checks,'commands':commands},indent=2)+'\n')
 raise
finally:
 shutil.copy2(ROOT/'qa/run.py',OUT/'run-source.py');shutil.copy2(ROOT/'qa/Probe.elm',OUT/'Probe-source.elm');shutil.copy2(ROOT/'qa/probe.cjs',OUT/'probe-source.cjs')
