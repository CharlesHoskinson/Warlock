"""Bounded additive retained V15 evidence replay; no producer import/native command."""
from pathlib import Path
import hashlib,json,os,stat
B=Path(__file__).resolve().parent;STAGE=B.parent/'toolkit-held-matrix-v15';ATTEMPT=STAGE/'attempt-1';V=ATTEMPT/'qt-wayland'
def unique(pairs):
 r={}
 for k,v in pairs:
  if k in r:raise ValueError('duplicate JSON key')
  r[k]=v
 return r
def read(p):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  before=os.fstat(fd);raw=b''
  while True:
   part=os.read(fd,65536)
   if not part:break
   raw+=part
   if len(raw)>134217728:raise ValueError('bounded retained input exceeded')
  after=os.fstat(fd)
  identity=('st_dev','st_ino','st_mode','st_uid','st_gid','st_size','st_mtime_ns','st_ctime_ns')
  if not stat.S_ISREG(before.st_mode)or before.st_uid!=os.getuid()or any(getattr(before,k)!=getattr(after,k)for k in identity):raise ValueError('retained input changed')
  return raw
 finally:os.close(fd)
def js(p):return json.loads(read(p),object_pairs_hook=unique)
def sha(p):return hashlib.sha256(read(p)).hexdigest()
def need(p,m):
 if not p:raise ValueError(m)
def gone(i):
 need(type(i['pid'])is int and i['pid']>0 and str(i['start']).isdigit(),'exact PID/start required')
 try:raw=Path('/proc',str(i['pid']),'stat').read_text()
 except (FileNotFoundError,ProcessLookupError):return True
 return int(raw.rsplit(') ',1)[1].split()[19])!=int(i['start'])
def helpers(rows):
 starts=[r for r in rows if r['event']=='started'];ends=[r for r in rows if r['event']=='terminal']
 need(len(rows)==len(starts)+len(ends)and len(starts)==len(ends),'refused/missing actual terminal')
 need(len({r['operation']for r in starts})==len(starts)and len({r['operation']for r in ends})==len(ends),'duplicate helper operation')
 for s in starts:
  e=[r for r in ends if r['operation']==s['operation']];need(len(e)==1,'missing exact terminal');e=e[0]
  need(e['exitCode']==0 and all(e.get(k)==s.get(k)for k in ('wrapper','delegate','class','queryRoot','helper','serviceOperation')),'nonzero/replaced helper terminal')
  need(s['delegate']['parent']==s['wrapper']['pid']and gone(s['wrapper'])and gone(s['delegate']),'actual helper lifecycle unresolved')
  need(s['ipc']['completeServerEOF']is True,'helper IPC EOF missing')
 return starts
def process_receipts(answer,nonce,previous=None):
 need(set(answer)=={'version','nonce','ack','states'}and answer['version']==1 and answer['nonce']==nonce and answer['ack']is True,'terminal acknowledgment differs')
 names=[];all_closed=True;counts={}
 for s in answer['states']:
  name=s['screenName'];names.append(name);need(name=='WAYLAND-1'and s['currentMonitor']==0,'actual output differs')
  need(s['nonce']==nonce and s['quiesced']is True and s['error']=='','terminal widget error/nonce')
  need(all(s['timers'][k]is False for k in ('snapshot','capture','allCapture')),'future polling active')
  generation={k:0 for k in ('snapshot','action','capture','allCapture')};active={};quiesced=False;budget=0;post=0
  for r in s['records']:
   need(type(r['utcMs'])is int and r['utcMs']>0,'receipt time malformed')
   event=r['event']
   if event=='quiesced':need(not quiesced and r['nonce']==nonce and type(r['queuedActions'])is int and r['queuedActions']>=0,'terminal epoch duplicate');quiesced=True;budget=r['queuedActions'];continue
   k=r['kind'];g=r['generation'];need(k in generation and type(g)is int and g>0,'unknown Process generation')
   if event=='requested':
    need(g==generation[k]+1 and k not in active,'overlapping request');declaration=r['commandDeclaration'];need(isinstance(declaration,list)and declaration and all(isinstance(x,str)for x in declaration),'request declaration malformed')
    if quiesced:need(k=='action','fresh post-quiesce poll');post+=1;need(post<=budget,'new queued action authority')
    generation[k]=g;active[k]=(g,None)
   elif event=='started':
    need(active.get(k)==(g,None)and type(r['pid'])is int and r['pid']>0,'unmatched Process start');d=r['commandDeclarationAtStart'];need(isinstance(d,list)and d and all(isinstance(x,str)for x in d),'start declaration malformed');active[k]=(g,r['pid'])
   elif event=='exited':need(active.get(k)==(g,r['pid'])and r['code']==0 and r['status']==0,'missing/nonzero normal receipt');del active[k]
   else:raise ValueError('unknown Process event')
  need(quiesced and generation==s['generations']and budget-post==s['queuedBudget'],'generation/queue witness differs')
  expected=set(active);need(set(s['current'])==expected,'active generation missing')
  for k,p in s['processes'].items():
   if k in active:need(p['running']is True and(active[k][1]is None or p['pid']==active[k][1]),'active Process PID differs')
   else:need(p['running']is False and p['pid']in(None,0),'unrecorded live Process')
  if previous:
   old=[x for x in previous['states']if x['screenName']==name];need(len(old)==1 and old[0]['currentMonitor']==s['currentMonitor']and s['records'][:len(old[0]['records'])]==old[0]['records'],'receipt prefix/output reset')
  closed=not active and s['current']=={}and s['queuedActions']==s['queuedBudget']==0 and not any(s['timers'].values());all_closed=all_closed and closed;counts[name]=generation
 need(names==['WAYLAND-1'],'exact widget set required');return all_closed,counts
def main():
 checks={};errors={};details={}
 def check(name,fn):
  try:details[name]=fn();checks[name]=True
  except Exception as error:checks[name]=False;errors[name]=repr(error)
 report=js(ATTEMPT/'report.json');variant=js(V/'report.json');frozen=js(STAGE/'frozen-inputs.json');old=js(ATTEMPT/'agent-wheel-aware-terminal-replay-v3.json');retired=js(ATTEMPT/'agent-retirement-replay-v1.json');evaluation=js(ATTEMPT/'agent-evaluation-replay-v1.json');dr=js(V/'qs-terminal-drain.json');q=js(V/'qs-lifecycle.json');config=js(V/'terminal-helpers/helper-config.json');archive=js(V/'terminal-helpers/archive.json');raw=read(V/'terminal-helpers/helper-events.jsonl');events=[json.loads(x,object_pairs_hook=unique)for x in raw.splitlines()if x.strip()]
 def outcomes():
  need(report['result']==variant['result']=='fail'and len(report['variants'])==1 and len(variant['cases'])==4,'whole campaign failure missing')
  for c in variant['cases'][:3]:need(c['result']=='pass'and len(c['gates'])==9 and all(x['passed']is True for x in c['gates'])and old['checks']['qt-wayland:'+c['case']+':nativeReplay'],'first three strict cases changed')
  c=variant['cases'][3];need(c['case']=='move-minimize-preview'and c['result']=='fail'and 'One exact complete family native handover from actual presentation required'in c['error'],'case4 original presentation refusal missing')
  need(old['result']==retired['result']==evaluation['result']=='fail','original auditor failures erased')
  return dict(passedCases=3,reachedCases=4,expectedCases=52,unrun=48,failedCase=c['case'],strictAuditorChecks=old['checks'],causeOfPresentationFailure='unclassified')
 def closure():
  need(old['checks']['completeFrozenBytesModesLinks']and old['checks']['exactSourceManifest']and evaluation['checks']['wholeFrozenBytesModesLinks'],'complete frozen integrity absent')
  need(sha(STAGE/'frozen-inputs.json')==report['sourceManifestSHA256']==old['sourceManifestSHA256']==evaluation['sourceManifestSHA256'],'source manifest differs')
  need(old['checks']['all18MainPreservation']and len(report['mainPreservation'])==18 and all(report['mainPreservation'].values()),'main preservation incomplete')
  need(old['checks']['qt-wayland:hostRuntimeCleanup']and old['checks']['qt-wayland:allRecordedOriginalIdentitiesGone'],'private closure incomplete')
  return dict(inputs=len(frozen['inputs']),modes=len(frozen['inputModes']),links=len(frozen['symlinks']),mainGates=18,privateRuntimeGone=True,allRecordedOriginalLifetimesGone=True)
 def journal():
  need(hashlib.sha256(raw).hexdigest()==archive['logSHA256']and sha(V/'terminal-helpers/helper-config.json')==archive['configSHA256']and archive['completeEOF']is True and events==archive['events'],'full raw helper archive differs')
  starts=helpers(events);return dict(started=len(starts),terminal=len(starts),refusals=0,nonzero=0,completeWorkloadAccepted=False,missingWorkloadFailure=variant['helperAcceptanceError'])
 def arms():
  tickets=variant['evaluationTickets'];paths=variant['evaluationArmDiagnostics'];need(len(tickets)==len(paths)==6,'six actual arm decisions required');rows=[]
  for t,path in zip(tickets,paths):
   p=Path(path);need(p.parent==V,'arm evidence outside exact attempt');a=js(p);steps=a['attempts'];pub=[x for x in steps if x['stage']=='published'];need(a['accepted']is True and a['budgetSeconds']==8 and len(pub)==1 and pub[0]['ticket']==t and pub[0]['monotonic']<a['deadline']and a['finishedMonotonic']<a['deadline'],'arm publication/deadline differs')
   before=steps[steps.index(pub[0])-1];need(before['stage']=='publication-current'and before['configChanged']is False and before['terminalClosed']is True and before['exactPendingProcesses']==[],'publication lacks exact quiet recheck')
   need(all(x.get('configChanged')is not True and not x.get('terminalError')for x in steps),'authority/nonzero mutation accepted')
   for digest,snapshot in a['eventSnapshots'].items():need(hashlib.sha256(json.dumps(snapshot,sort_keys=True,separators=(',',':')).encode()).hexdigest()==digest,'arm raw rows changed')
   rows.append(dict(serial=t['serial'],kind=t['kind'],attemptRecords=len(steps),durationSeconds=a['finishedMonotonic']-(a['deadline']-8),ticketNonce=t['nonce'],publishedOnce=True,artifactSHA256=sha(p)))
  need(rows[3]['kind']=='native-load'and rows[3]['attemptRecords']==11 and any(x.get('exactPendingProcesses')for x in js(Path(paths[3]))['attempts']),'actual pending helper retry missing')
  need(variant['completedEvaluations']==[1,2,3,4,5],'completed evaluation inventory differs');return rows
 def drain():
  need(dr==variant['terminalQueryDrain']and dr['accepted']is True and dr['featureResult']in('pass','fail')and dr['budgetSeconds']==8,'drain erased failure/authority')
  need(dr['nonce']==variant['terminalDrainInstall']['nonce']and dr['qsIdentity']==q['identity']==config['queryRoots']['qs']['identity'],'exact nonce/QS registration differs')
  calls=dr['controlCalls'];records=[x for x in q['records']if x['role'].startswith('terminal-')];need(len(calls)==len(records)and [x['method']for x in calls]==['qaTerminalQuiesce']+['qaTerminalRead']*(len(calls)-1),'terminal control sequence differs')
  for c,r in zip(calls,records):
   need(r['command']==[str(STAGE/'payload/omarchy/bin/omarchy-shell'),'hoskinson.windows',c['method'],dr['nonce']]and r['role']=='terminal-'+c['method']and c['returncode']==r['returncode']==0 and c['stdout']==r['stdout']and c['stderr']==r['stderr']==''and r['qsIdentity']==q['identity']and r['originalProbeGone']is True and gone(r['processIdentity']),'exact control invocation/wait differs')
  previous=None;last=None;counts=None
  for s in dr['samples']:
   last,counts=process_receipts(s['answer'],dr['nonce'],previous);need(last==s['actualProcessReceiptsClosed'],'Process receipt closure claim differs');previous=s['answer']
  need(last and dr['samples'][-1]['helperNormalClosed']is True and dr['samples'][-1]['unloggedExactHelpers']==[],'final drain lacks closure');helpers(dr['lastRawHelperRows'])
  need(dr['servicePhaseProof']['identity']==config['queryRoots']['service']['identity']and dr['servicePhaseProof']['exitCode']==0 and dr['servicePhaseProof']['actualOriginalGone']is True and variant['cleanup']['service']['exitCode']==0 and variant['serviceEvidenceAcceptance']['allNormal']is True,'normal service proof missing')
  need(dr['servicePhaseProof']['resourceAcceptance']==variant['serviceEvidenceAcceptance'],'resource proof replaced')
  for w in dr['sourceWitnesses'].values():need(w['source']['sha256']==w['actual']['sha256']==sha(w['source']['path'])and w['source']['completeEOF']is True and w['actual']['completeEOF']is True,'QML witness differs')
  normal=[x for x in q['records']if x['role']=='normal-kill'];need(len(normal)==1 and dr['finishedUtcNs']<normal[0]['startedUtcNs']and variant['cleanup']['shell']['normalQuit']is True and variant['cleanup']['shell']['exitCode']==0 and variant['cleanup']['shell']['exitObservedUtcNs']>normal[0]['completedUtcNs']and gone(q['identity']),'normal QS quit preceded drain closure')
  return dict(processGenerations=counts,normalProcessCount=sum(sum(v.values())for v in counts.values()),samples=len(dr['samples']),controlCalls=len(calls),strictHelperNormal0AtDrain=len(helpers(dr['lastRawHelperRows'])),normalQSQuitAfterDrain=True,serviceNormallyClosed=True,declaredCommandsOnly=True,kernelArgvOrPIDstartNotInferred=True,featureSnapshotAtDrain=dr['featureResult'],finalFeatureResult=variant['result'],featureSnapshotNotAuthority=True,invocationAuthority='reviewed frozen invocation control flow plus actual normal wait/PIDstart receipt; separate kernel CLI argv snapshot not retained')
 def native_partial():
  need(variant['normalNativeUnload']is True and variant['actualNativeUnloadReply']=='ok\n'and 'actualProbeUnloadReply'not in variant,'actual candidate/probe distinction missing')
  need('timed out after 5 seconds'in variant['finalNativeEvaluationError']and "'repl'"in variant['finalNativeEvaluationError']and 'timed out after 5 seconds'in variant['error']and "'-j', 'clients'"in variant['error'],'original final IPC failures missing')
  failure=js(V/'evaluation-6-failure.json');need(failure['accepted']is False and failure['ticket']==variant['evaluationTickets'][5],'final evaluation failure erased')
  keys=['evaluation:'+variant['evaluationTickets'][5]['nonce']+':'];observed=[r['operation']for r in events if r['event']=='started'and any(r['operation'].startswith(k)for k in keys)]
  return dict(candidateUnloadReplyRecorded=True,finalNativeEvaluationComplete=False,probeUnloadSubmittedOrReplied=False,actualFinalEvaluationOperations=observed,finalOrdinalReplTimeoutSeconds=5,probePreArmClientsTimeoutSeconds=5,timeoutCause='unclassified',fullNormalNativeRetirementAccepted=False)
 for name,fn in (('originalCasesAndFailures',outcomes),('frozenMainAndPrivateClosure',closure),('actualRawHelperIntegrity',journal),('sixBoundedArmDecisions',arms),('normalPrivateTerminalDrain',drain),('partialFinalNativeRetirement',native_partial)):check(name,fn)
 result=dict(result='pass bounded evidence replay'if all(checks.values())else 'fail bounded evidence replay',checks=checks,errors=errors,details=details,originalWhole52Result='fail',fullHeld52Accepted=False,fullNormalNativeRetirementAccepted=False,nativeCommands=False,mainWrites=False,originalAuditorArtifacts={n:sha(ATTEMPT/n)for n in ('agent-wheel-aware-terminal-replay-v3.json','agent-retirement-replay-v1.json','agent-evaluation-replay-v1.json')},auditorSHA256=sha(Path(__file__)))
 fd=os.open(B/'replay-v2.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w')as out:json.dump(result,out,indent=2);out.write('\n')
 print(json.dumps(dict(result=result['result'],checks=checks,errors=errors)));return int(not all(checks.values()))
if __name__=='__main__':raise SystemExit(main())
