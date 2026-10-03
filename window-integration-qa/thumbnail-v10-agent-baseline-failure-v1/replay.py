"""External read-only terminal evidence replay; feature failures remain failures."""
from pathlib import Path
import collections,hashlib,importlib.util,json,os,stat
QA=Path('/home/hoskinson/window-integration-qa');B=QA/'family-preparation-thumbnail-v10';A=B/'attempt-baseline-1';OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(n):return json.loads((A/n).read_text())
def save(n,r):
 with os.fdopen(os.open(OUT/n,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:json.dump(r,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def lifetime(row):
 p=int(row['pid']);s=str(row['start'])
 try:
  raw=Path('/proc/'+str(p)+'/stat').read_text();tail=raw[raw.rfind(')')+2:].split();return {'pid':p,'start':s,'actualStart':tail[19],'selectedLifetimeGone':tail[19]!=s,'state':tail[0]}
 except(FileNotFoundError,ProcessLookupError):return {'pid':p,'start':s,'selectedLifetimeGone':True,'actualStart':None}
def main():
 report=read('report.json');terminal=read('actual-terminal-binding.json');confirmation=read('actual-terminal-binding-confirmation.json');retired=read('service-retirement-1.json');archive=read('terminal-helpers/archive.json');completed=read('completed-helpers.json')
 manifest=B/'frozen-inputs.json';expected='bcabc3433ce35d76a9fb403fc9dac9f4c6f5444b0e14e83108a213ee688811d9';assert sha(manifest)==expected
 packet=json.loads(manifest.read_text());path=B/'collector_v9_closure.py';assert sha(path)=='3ef9b46881587023d642cee353ed84b4bf8de6eb9e264bfbaf1448980e1c0742'
 spec=importlib.util.spec_from_file_location('v10_readonly_alias',path);closure=importlib.util.module_from_spec(spec);spec.loader.exec_module(closure)
 closure.verify_links(packet['symlinks']);assert set(packet['inputs'])==set(packet['inputModes'])
 for n,d in packet['inputs'].items():closure.retained_file(n,d,packet['inputModes'][n],packet['inputs'],packet['inputModes'],packet['symlinks'])
 closure.verify_links(packet['symlinks'])
 assert sha(A/'terminal-helpers/helper-events.jsonl')==archive['logSHA256'];assert sha(A/'terminal-helpers/helper-config.json')==archive['configSHA256']
 events=[json.loads(line)for line in (A/'terminal-helpers/helper-events.jsonl').read_text().splitlines()]
 key=lambda x:(x.get('helper'),x.get('operation'),x['wrapper']['pid'],str(x['wrapper']['start']))
 starts={};ends={};refused=[]
 for e in events:
  if e.get('event')=='started':assert key(e)not in starts;starts[key(e)]=e
  elif e.get('event')=='terminal':assert key(e)not in ends;ends[key(e)]=e
  elif e.get('event')=='refused':refused.append(e)
 identities={}
 def add(row):
  if isinstance(row,dict)and 'pid'in row and 'start'in row:identities[(int(row['pid']),str(row['start']))]={'pid':int(row['pid']),'start':str(row['start'])}
 for e in events:
  for name in ('wrapper','delegate'):add(e.get(name))
 for row in report['processes']:add(row)
 host=report['hostEvidence']
 for name in ('weston','hyprland'):add(host.get(name))
 add({'pid':host['compositorPID'],'start':host['compositorStart']})
 for row in host.get('observedDescendantIdentities',[]):add(row)
 for row in host.get('unexpectedInnerDescendants',[]):add(row)
 batches=confirmation['terminalBatchConfirmation'];renderer=[]
 for batch in batches:
  r=batch['renderer'];life=r['lifecycle'];owner=r['stable'];add(owner['ownership']);add({'pid':owner['keeperPID'],'start':owner['keeperStart']});kt=life['keeperTerminal']
  for job in kt['jobs']:add(job)
  renderer.append({'actor':batch['actor'],'batchRelations':batch['relations'],'rendererRelations':r['relations'],'rendererErrors':r['errors'],'rendererReturncode':life['rendererReturncode'],'keeperReturncode':life['keeperReturncode'],'keeperNormalStop':kt['normalStop'],'allKernelGroupsEmpty':kt['allGroupsEmpty'],'registeredJobs':kt['registrations'],'allJobTerminalNormal':all(j['normalCompletion']is True and j['groupEmpty']is True for j in kt['jobs'])})
 gone=[lifetime(row)for row in identities.values()]
 history=terminal['ledger']['history'];failed=[(i,x)for i,x in enumerate(history)if x['outcome']!='complete'];assert len(failed)==1
 index,query=failed[0];assert query['outcome']=='refused'and query['closed']is True and query['published']is True and query['request']=='j/clients';assert query['error']['type']=='TimeoutError'
 scene=retired['history'][0];profile=scene['profile'];commitrows=scene['results'];timing=[{'identity':r['identity'],'reason':r['reason'],'committedNs':r['committedNs'],'insideQueryRegisteredFinishedInterval':query['registeredNs']<=r['committedNs']<=query['finishedNs']}for r in commitrows]
 captures=[]
 for row in retired['retainedEpochSources']:
  p=Path(row['retainedPath']);captures.append({'path':str(p),'sha256':sha(p),'expectedSHA256':row['sha256'],'exact':sha(p)==row['sha256']==row['source']['digest'],'captureCallbackDelegatedOnce':row['captureCallbackDelegatedOnce'],'sourceResultUnchanged':row['sourceResultUnchanged']})
 cache=[{'path':str(p),'sha256':sha(p),'digestFilenameExact':sha(p)==p.stem}for p in sorted((A/'service-cache-pairs').iterdir())if p.is_file()]
 renderer_events=retired['rendererEvents'];eventcounts=collections.Counter(e.get('event')for e in renderer_events)
 seeded=[e for e in renderer_events if e.get('event')=='seeded'];uploads=[e for e in renderer_events if e.get('event')=='uploaded'];presented=[e for e in renderer_events if e.get('event')=='presented'and e.get('accepted')is True];endpoint=[e for e in presented if e.get('endpoint')is True]
 journal=terminal['journal'];firstfailed=next(x for x in report['checks']if not x['passed']);g=firstfailed['journal']
 artifacts={str(p):{'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)}for p in sorted(A.rglob('*'))if p.is_file()and not p.is_symlink()}
 result={'campaignResult':'fail','featureChecksReached':len(report['checks']),'featureChecksPassed':sum(x['passed']for x in report['checks']),'originalRequired':38,'unreached':38-len(report['checks']),'firstFailedCheck':firstfailed['name'],'primaryPredicate':{'actorSerial':g['actorSerial'],'resourceErrors':g['resourceErrors'],'housekeepingErrors':g['housekeepingErrors'],'liveActors':g['liveActors'],'retiringActors':g['retiringActors'],'pending':g['pending'],'closedActorOutcomes':[r.get('outcome')for r in g['actorResources']]},'sourceClosure':{'manifestSHA256':expected,'inputs':len(packet['inputs']),'modes':len(packet['inputModes']),'links':len(packet['symlinks']),'exact':True},'preservation':{'gates':report['mainPreservation'],'allPassed':all(report['mainPreservation'].values()),'count':len(report['mainPreservation'])},'nativeUnload':report['normalNativeUnload'],'clientCleanup':report['clientCleanup'],'rendererTerminal':renderer,'terminalBindingAccepted':False,'terminalBindingErrors':terminal['errors'],'terminalConfirmationErrors':confirmation['errors'],'readonly':{'historyCount':len(history),'completeCount':len(history)-len(failed),'refusedIndex':index,'refused':query,'registeredToFinishedMs':(query['finishedNs']-query['registeredNs'])/1e6,'originalHousekeepingBudgetSeconds':.6,'completeServerEOFObserved':query['evidence']['completeServerEOF'],'nativeLockHolderProven':False,'exactDeadlineCheckSiteProven':False,'commitCompletionChronology':timing,'housekeepingErrorPublishedNs':g['housekeepingErrors'][0]['timeNs'],'distinctFromV9PreconnectRefusal':query['evidence']['peer']is not None and query['evidence']['replyBytes']>0},'scene':{'token':scene['token'],'profile':profile,'allResults':commitrows,'sourceCount':len(scene['sources']),'validated':scene['validated'],'visual':scene['visual'],'ready':scene['ready']},'capture':{'count':len(captures),'retained':captures,'allExact':all(c['exact']for c in captures),'cacheFiles':cache,'allCacheFilenameHashesExact':all(c['digestFilenameExact']for c in cache),'rendererEventCounts':dict(eventcounts),'seeded':seeded,'uploaded':uploads,'acceptedPresentations':len(presented),'acceptedEndpoints':endpoint,'nativePerformanceAccepted':False,'baselineSeedGateActualPassed':True},'helpers':{'starts':len(starts),'terminals':len(ends),'refusals':refused,'nonzeroTerminals':[e for e in ends.values()if e['exitCode']!=0],'unpairedStarts':[starts[k]for k in starts.keys()-ends.keys()],'extraTerminals':[ends[k]for k in ends.keys()-starts.keys()],'queryRoots':dict(collections.Counter(e.get('queryRoot')for e in starts.values())),'compositorOperations':[e['operation']for e in starts.values()if e.get('class')=='compositor'],'wholeExpectedHelperWorkloadAccepted':False,'originalSummaryResult':completed['result'],'originalSummaryReason':completed['reason'],'rawCompleteEOF':archive['completeEOF'],'normalLifecycleAccepted':False},'lifetimes':gone,'allSelectedLifetimesGone':all(r['selectedLifetimeGone']for r in gone),'host':{'runtime':host['runtime'],'runtimeGone':host['runtimeGone'],'runtimeCurrentlyAbsent':not Path(host['runtime']).exists(),'remainingDescendants':host['remainingDescendants'],'unexpectedInnerDescendants':host['unexpectedInnerDescendants'],'cleanupErrors':host['cleanupErrors'],'normalHostExitProven':False},'artifacts':artifacts,'fault34Authorized':False,'nativeBaselineAccepted':False,'fullContractAccepted':False,'mainWrites':False}
 save('report.json',result)
 print(json.dumps({k:result[k]for k in ('campaignResult','featureChecksPassed','featureChecksReached','unreached','firstFailedCheck','allSelectedLifetimesGone')}));print(json.dumps({'sourceInputs':len(packet['inputs']),'mainGates':len(report['mainPreservation']),'queryRows':len(history),'refusalDurationMs':result['readonly']['registeredToFinishedMs'],'helperStarts':len(starts),'helperTerminals':len(ends),'selectedLifetimeCount':len(gone),'nativeAccepted':False}))
if __name__=='__main__':main()
