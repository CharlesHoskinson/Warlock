import copy,hashlib,json,shutil,subprocess,time,os
from toolchain import verify,command as pin_command,checks as toolchain_checks
heldToolchain=verify()
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
  verify();cmd=pin_command(cmd);p=subprocess.run(cmd,cwd=cwd,capture_output=True,timeout=180,env=dict(os.environ,ELM_HOME=str(ROOT/heldToolchain['elmHome'])));verify();toolchain_checks.append({'name':name,'beforeAfterVerified':True});(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);commands.append({'name':name,'command':cmd,'cwd':str(cwd),'exitCode':p.returncode});assert p.returncode==0,p.stderr.decode();return p
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
 check('original-old-binding-and-Unknown-history-retained',after['history']==[{'binding':old,'status':'Unknown','released':True}])
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
 result=run('retry-pending',base+[{'kind':'refresh'},native(release)]);check('pending-retry-retains-completed-accepted-pair',not result[-1]['blocked'] and not result[-1]['wires'])
 check('fresh-retry-repeats-idempotent-ready-before-reads',[w['kind'] for w in result[-2]['wires']]==['reconciliation-ready','projection-request','geometry-facts-request'])
 retryAct=read('action-projection',6);retryGeo=read('geometry-facts',7,revision=int(geo['revision'])+1)
 retryRelease=json.loads(json.dumps(release));retryRelease['release']['observation']={'actionRequestId':'6','geometryRequestId':'7','actionContext':retryAct['context'],'geometryContext':{'lifetime':current['lifetime'],'epoch':current['frontend'],'output':retryGeo['outputGeneration'],'revision':retryGeo['revision']}}
 result=run('retry-complete',base+[{'kind':'refresh'},native(retryAct),native(retryGeo),native(retryRelease)]);check('latest-both-accepted-retries-can-release',not result[-1]['blocked'])
 # A queued dirty notification drains a next batch on the final accepted reply.
 dirty={'protocolVersion':3,'kind':'host-refresh'}
 dirtyBase=prefix+[native(unknown),native(proof),native(act),native(dirty),native(geo)]
 dirtyRows=run('dirty-final-geometry',dirtyBase+[native(release)])
 check('dirty-final-geometry-drains-new-batch-before-release',[w['kind'] for w in dirtyRows[-2]['wires']]==['reconciliation-ready','projection-request','geometry-facts-request'] and dirtyRows[-2]['shell']['phase']=='Reconciling')
 check('completed-pair-release-survives-pending-next-batch',not dirtyRows[-1]['blocked'] and dirtyRows[-1]['unresolved']==0 and dirtyRows[-1]['transaction']['transaction']['status']=='Unknown' and not dirtyRows[-1]['wires'] and dirtyRows[-1]['effectRequest']=='12')
 check('pending-next-read-still-blocks-new-explicit-intent',not dirtyRows[-1]['shell']['available'] and dirtyRows[-1]['expected']=='6' and dirtyRows[-1]['geometryExpected']=='7')
 dirtyActionBase=prefix+[native(unknown),native(proof),native(geo),native(dirty),native(act)]
 dirtyActionRows=run('dirty-final-action',dirtyActionBase+[native(release)])
 check('accepted-action-counts-even-if-immediate-drain-reconciling',dirtyActionRows[-2]['shell']['phase']=='Reconciling' and not dirtyActionRows[-1]['blocked'] and dirtyActionRows[-1]['transaction']['transaction']['status']=='Unknown')
 newAction=read('action-projection',6,revision=int(act['context']['revision'])+1)
 newActionRows=run('actual-new-action-obsoletes-pair',base+[{'kind':'refresh'},native(newAction),native(release)])
 check('actual-new-accepted-action-stamp-refuses-obsolete-release',newActionRows[-1]['blocked'] and newActionRows[-1]['unresolved']==1 and not newActionRows[-1]['wires'])
 newGeometryRows=run('actual-new-geometry-obsoletes-pair',base+[{'kind':'refresh'},native(retryGeo),native(release)])
 check('actual-new-accepted-geometry-stamp-refuses-obsolete-release',newGeometryRows[-1]['blocked'] and newGeometryRows[-1]['unresolved']==1 and not newGeometryRows[-1]['wires'])
 # Exact duplicate proof cannot issue another acknowledgement or refresh.
 result=run('duplicate-proof',base+[native(proof)]);check('duplicate-proof-has-no-automatic-read-replay',not result[-1]['wires'] and result[-1]['blocked'])
 # Independent historical keys share one qualified scope without releasing each other.
 independent=copy.deepcopy(unknown);independent['record']['intent'].update(request='13',generation='15',incarnation='1')
 independentRows=run('independent',prefix+[native(unknown),native(independent),native(proof),native(act),native(geo),native(release)])
 check('only-matched-target-reservation-removed',not independentRows[-1]['blocked'] and independentRows[-1]['blocked1'] and independentRows[-1]['unresolved']==1)
 check('independent-history-and-counters-kept',independentRows[-1]['transaction']['transaction']==independentRows[-2]['transaction']['transaction'] and independentRows[-1]['effectRequest']=='13' and independentRows[-1]['effectGeneration']=='15')
 # Historical old session is part of the full key even when Effects.Intent collides.
 collidingUnknown=copy.deepcopy(unknown);collidingUnknown['record']['binding']['session']='999'
 collisionBase=prefix+[native(unknown),native(collidingUnknown),native(proof),native(act),native(geo)]
 collisionRows=run('full-origin-collision',collisionBase+[native(release)])
 check('one-origin-release-cannot-free-shared-Intent-reservation',collisionRows[-1]['blocked'] and collisionRows[-1]['unresolved']==1 and sum(item['released'] for item in collisionRows[-1]['history'])==1)
 secondProof=copy.deepcopy(proof);secondProof.update(requestId='32',sequence='778');secondProof['queriedBinding']=collidingUnknown['record']['binding']
 secondRelease=copy.deepcopy(retryRelease);secondRelease['record']=collidingUnknown['record'];secondRelease['release']['proof']=secondProof
 collisionRows=run('full-origin-collision-complete',collisionBase+[native(release),native(secondProof),native(retryAct),native(retryGeo),native(secondRelease)])
 check('each-full-origin-requires-own-qualified-release',not collisionRows[-1]['blocked'] and collisionRows[-1]['unresolved']==0 and all(item['released'] and item['status']=='Unknown' for item in collisionRows[-1]['history']) and len(collisionRows[-1]['history'])==2)
 # Stale detached delivery must not import or advance reservations/counters.
 detachedRows=run('detached-unknown',prefix+[native({'protocolVersion':3,'kind':'host-disconnected'}),native(unknown)])
 check('detached-full-record-cannot-import-or-advance',detachedRows[-1]['unresolved']==0 and detachedRows[-1]['effectRequest']=='0' and detachedRows[-1]['history']==[])
 # Exhausted history refuses frontend transport, preserving all bounded slots.
 many=[]
 for n in range(1,66):
  f=copy.deepcopy(unknown);f['record']['intent'].update(request=str(n),generation=str(n+100),incarnation=str(n));many.append(native(f))
 capacityRows=run('history-capacity',prefix+many)
 check('history-capacity-fails-closed-without-eviction',len(capacityRows[-1]['history'])==64 and capacityRows[-1]['unresolved']==64 and capacityRows[-1]['shell']['transportRefused'] and capacityRows[-1]['effectRequest']=='64' and capacityRows[-1]['effectGeneration']=='164')
 # Actual menu dispatch uses the public post-close reducer path and emitted native key.
 owner={'kind':'owner','frame':{'surfaceProtocol':2,'kind':'surface-owner','outputId':'1','providerId':'1'}}
 menuPrefix=prefix+[owner,{'kind':'menu-open'},{'kind':'menu-minimize'}]
 menuRows=run('menu-prepare',menuPrefix)
 check('menu-selection-prepared-through-public-reducer',menuRows[-1]['prepared'] and menuRows[-1]['outstanding']==1)
 # Reconciliation retires a prepared local click before old read replies arrive.
 preparedRelease=copy.deepcopy(release);preparedRelease['release']['observation']={'actionRequestId':'6','geometryRequestId':'7','actionContext':retryAct['context'],'geometryContext':{'lifetime':current['lifetime'],'epoch':current['frontend'],'output':retryGeo['outputGeneration'],'revision':retryGeo['revision']}}
 preparedRows=run('prepared-reconciliation',menuPrefix+[native(unknown),native(proof),native(read('action-projection',4)),native(read('geometry-facts',5)),native(retryAct),native(retryGeo),native(preparedRelease)])
 check('reconciliation-retires-prepared-choice-without-native-outcome',not preparedRows[-1]['prepared'] and preparedRows[-1]['outstanding']==0 and not preparedRows[-1]['choice'])
 check('prepared-click-never-replayed-by-proofs-reads-or-release',not any(w['kind']=='window-effect' for row in preparedRows for w in row['wires']) and preparedRows[-1]['effectRequest']=='12' and not preparedRows[-1]['blocked'])
 menuDispatch=menuPrefix+[native(read('action-projection',4)),native(read('geometry-facts',5))]
 menuRows=run('menu-dispatch',menuDispatch)
 wire=next(w for w in menuRows[-1]['wires'] if w['kind']=='window-effect')
 menuRecord={'schema':2,'effectProtocol':wire['effectProtocol'],'binding':wire['binding'],'intent':wire['intent'],'status':'Unknown'}
 outcome={**wire,'kind':'effect-outcome','status':'Unknown','reason':'Synthetic transport uncertainty fixture','revision':wire['intent']['context']['revision'],'outputGeneration':wire['intent']['context']['output']}
 menuReceiptUncertain=menuDispatch+[native(outcome)]
 menuReceiptRows=run('menu-receipt-unknown',menuReceiptUncertain)
 check('public-receipt-router-retains-uncertain-native-mapping',menuReceiptRows[-1]['outstanding']==1 and menuReceiptRows[-1]['registry']==1 and menuReceiptRows[-1]['blocked'])
 menuUncertain=menuDispatch+[native({'protocolVersion':3,'kind':'host-reservation-unknown','binding':current,'record':menuRecord})]
 menuRows=run('menu-unknown',menuUncertain)
 check('actual-menu-native-key-becomes-Unknown',menuRows[-1]['blocked'] and menuRows[-1]['outstanding']==1 and menuRows[-1]['registry']==1 and menuRows[-1]['transaction']['transaction']['status']=='Unknown')
 nextRead=int(menuRows[-1]['shellRequest'])+1
 newer={**current,'frontend':'3'};attached={**frames['attached'],'binding':newer}
 restart=menuUncertain+[native({'protocolVersion':3,'kind':'host-disconnected'}),{'kind':'reconnect'},native(attached),native(read('action-projection',nextRead,newer)),native(frames['host-geometry-negotiate']),native(read('geometry-attached',nextRead+1,newer)),native(read('geometry-facts',nextRead+2,newer))]
 menuUnknown={'protocolVersion':3,'kind':'host-reservation-unknown','binding':newer,'record':menuRecord}
 menuProof={**proof,'binding':newer,'queriedBinding':current}
 menuAct=read('action-projection',nextRead+3,newer);menuGeo=read('geometry-facts',nextRead+4,newer,revision=int(geo['revision'])+1)
 menuRelease={'protocolVersion':3,'kind':'host-reservation-released','binding':newer,'record':menuRecord,'release':{'id':'abcdef0123456789'*4,'proof':menuProof,'observation':{'actionRequestId':str(nextRead+3),'geometryRequestId':str(nextRead+4),'actionContext':menuAct['context'],'geometryContext':{'lifetime':newer['lifetime'],'epoch':newer['frontend'],'output':menuGeo['outputGeneration'],'revision':menuGeo['revision']}}}}
 menuBase=restart+[native(menuUnknown),native(menuProof),native(menuAct),native(menuGeo)]
 menuRows=run('menu-release',menuBase+[native(menuRelease),{'kind':'act2'}]);afterMenu=menuRows[-2]
 check('menu-full-correlated-release-clears-live-local-and-native-mappings',not afterMenu['blocked'] and afterMenu['outstanding']==0 and afterMenu['registry']==0)
 check('menu-history-remains-Unknown-without-fake-receipt',afterMenu['historicalUnknownMenus']==1 and afterMenu['transaction']['transaction']['status']=='Unknown' and afterMenu['effectRequest']=='1' and not afterMenu['wires'])
 check('new-explicit-menu-target-intent-required',any(w['kind']=='window-effect' for w in menuRows[-1]['wires']) and menuRows[-1]['effectRequest']=='2')
 menuBad=copy.deepcopy(menuRelease);menuBad['release']['observation']['geometryRequestId']=str(nextRead+2)
 menuRows=run('menu-foreign-read',menuBase+[native(menuBad)])
 check('menu-mismatch-keeps-both-reservations',menuRows[-1]['blocked'] and menuRows[-1]['outstanding']==1 and menuRows[-1]['registry']==1)
 # Compiled differential: identical public input demonstrates original611 drain gap.
 original=REPO/'implementation/elm-reconciliation-frontend-v611'
 baseline=OUT/'original611-inputs';shutil.copytree(original/'src',baseline/'src');shutil.copy2(original/'elm.json',baseline/'elm.json');shutil.copy2(ROOT/'qa/Probe.elm',baseline/'src/Probe.elm')
 command('original611-compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Probe.elm','--optimize','--output='+str(OUT/'original611-worker.js')],baseline)
 for scenario in ['dirty-final-geometry','dirty-final-action']:
  command('original611-'+scenario,['node',str(ROOT/'qa/probe.cjs'),str(OUT/'original611-worker.js'),str(OUT/(scenario+'-events.json')),str(OUT/('original611-'+scenario+'-rows.json'))],ROOT)
  beforeRows=json.loads((OUT/('original611-'+scenario+'-rows.json')).read_text());fixedRows=json.loads((OUT/(scenario+'-rows.json')).read_text())
  check('compiled611-differential-'+scenario,beforeRows[-1]['blocked'] and beforeRows[-1]['unresolved']==1 and not fixedRows[-1]['blocked'] and fixedRows[-1]['unresolved']==0)
 (OUT/'report.json').write_text(json.dumps({'elmToolchainBeforeAfterChecks':toolchain_checks,'passed':True,'checks':checks,'commands':commands,'nativeAcceptance':False,'fixture':'Synthetic post-proof trajectory derived from preserved573 observation payloads; no claimed captured durable release','sourceSHA256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'src').glob('*.elm')}},indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks),'report':str(OUT/'report.json')}))
except BaseException as error:
 (OUT/'failure.json').write_text(json.dumps({'passed':False,'error':repr(error),'checks':checks,'commands':commands},indent=2)+'\n')
 raise
finally:
 shutil.copy2(ROOT/'qa/run.py',OUT/'run-source.py');shutil.copy2(ROOT/'qa/Probe.elm',OUT/'Probe-source.elm');shutil.copy2(ROOT/'qa/probe.cjs',OUT/'probe-source.cjs')
