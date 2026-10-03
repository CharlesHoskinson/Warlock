from pathlib import Path
import base64,hashlib,importlib.util,json,stat
B=Path(__file__).resolve().parent
P=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3/frontend')
spec=importlib.util.spec_from_file_location('unchanged_capture_command',P/'pin_capture.py');capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def raw(row):
 result=base64.b64decode(row['rawBase64']);assert len(result)==row['capturedBytes']and hashlib.sha256(result).hexdigest()==row['rawSHA256']and row['truncated']is False and 'readError'not in row;return result
reports=[];checks={};actors=[]
for case in ['normal-changed-command','cancelled-changed-command','same-command-reuse']:
 found=list(B.glob('terminal-disconnect-evidence/*/terminal-registry-'+case+'-*.json'));assert len(found)==1;path=found[0];r=json.loads(path.read_text());a=json.loads(r['stdout']);first=a['first'];second=a['second'];fresh=a['freshArmed']
 per={'normalCPUExit0':r['result']=='pass'and r['exitCode']==0,'noRepeatOrHelperControl':a['helperLaunches']==2 and a['helperRetries']==0 and r['helperWaitSleepOrRetryAdded']is False and r['originalEachHelperTransactionSeconds']==2,'freshLeaseAndKernelProof':second['lease']>first['lease']and all(second[k]is True for k in ['complete','kernelBound','normalLifecycle','historicalKernelProof','workerJoined','stdoutEOF','stderrEOF','receiptVerified','kernelGone']),'noInheritedProofBeforeSecondLaunch':all(fresh[k]is False for k in ['started','historicalKernelProof','stdoutEOF','stderrEOF','receiptVerified','complete']),'firstNormalActorClosure':all(first[k]is True for k in ['normalLifecycle','historicalKernelProof','workerJoined','stdoutEOF','stderrEOF','receiptVerified','kernelGone']),'typedEightRefusals':len(a['typedRefusals'])==8 and all(x['refused']is True for x in a['typedRefusals']),'privateCleanupAndSourceStable':r['normalFixtureCleanup']is True and r['normalCPUPrivateRuntimeRemoved']is True and r['sourcesUnchanged']is True,'exactTwoDurableReceipts':len(r['durableReceipts']['files'])==2,'durableReport0600':stat.S_IMODE(path.stat().st_mode)==0o600}
 receipts=[json.loads(raw(data))for data in r['durableReceipts']['files'].values()];firstReceipt=json.loads(first['stdout']);secondReceipt=json.loads(second['stdout']);per['receiptsEqualBoundExactOutputs']=firstReceipt in receipts and secondReceipt in receipts
 for i,receipt in enumerate([firstReceipt,secondReceipt]):
  per['actualRequest'+str(i)+'EqualsUnchangedCommand']=raw(r['receivedRequests'][str(i)])==capture.command(receipt['publicIdentity']);actors.append(receipt['authority']['frontend'])
 actors.extend([r['actualRequester']['identity'],r['config']['compositor']['identity']]);before=json.loads(raw(r['durableBeforeHookEvidence']));beforeSecond=json.loads(raw(r['durableBeforeSecondHelperEvidence']));per['durableFirstStateExact']=before['state']==first;per['durableFreshArmExact']=beforeSecond['state']==fresh
 if case=='cancelled-changed-command':per['consumerCancelledWithoutActorClosureLoss']=first['current']is False and first['complete']is False and first['kernelBound']is False
 else:per['firstComplete']=first['complete']is True
 if case=='same-command-reuse':per['sameCommandExact']=firstReceipt['publicIdentity']==secondReceipt['publicIdentity']
 else:per['explicitTypedRetireBeforeChangedCommand']=a['terminalRetire']['terminalRetired']is True and a['terminalRetire']['lease']==first['lease']and firstReceipt['publicIdentity']!=secondReceipt['publicIdentity']
 per['distinctIndependentActors']=firstReceipt['authority']['frontend']!=secondReceipt['authority']['frontend']and a['independentSecondActor']is True
 assert all(per.values()),(case,per);checks[case]=per;reports.append({'case':case,'path':str(path),'sha256':sha(path),'elapsedSeconds':r['elapsedSeconds'],'helperActors':2})
for case in ['actual-public-provider-refusal','final-admission-primitive']:
 path=B/'narrow-components'/case/'report.json';r=json.loads(path.read_text());a=json.loads(r['stdout']);per={'normalExit0':r['result']=='pass'and r['exitCode']==0,'actualActorGone':r['actualActorGone']is True,'sourcesStable':r['sourcesUnchanged']is True,'durableReport0600':stat.S_IMODE(path.stat().st_mode)==0o600}
 if case=='actual-public-provider-refusal':per['actualSixPublicRefusals']=len(a['observations'])==6 and all(x['result']['error']=='Exact private runtime required'and x['result']['nativeWrites']==0 and 'terminalRetired'not in x['result']for x in a['observations']);per['positiveNotClaimed']=a['installedQSRetirePositive']is False and a['nativeTypedParserReachedClaim']is False
 else:per['exactWhiteboxFourChecks']=a['checks']==4 and a['whiteBoxFinalAdmissionPrimitive']is True and a['actualRegistryFixture']is False and a['genuineQtSignalAtDisconnect']is False and a['actualActorClosureProved']is False
 assert all(per.values()),(case,per);checks[case]=per;reports.append({'case':case,'path':str(path),'sha256':sha(path),'elapsedSeconds':r['elapsedSeconds'],'helperActors':0})
observed=[]
for identity in actors:
 p=Path('/proc')/str(identity['pid']);row={'pid':identity['pid'],'expectedStart':identity['start'],'present':p.exists()}
 if p.exists():text=(p/'stat').read_text();row['observedStart']=text[text.rfind(')')+2:].split()[19]
 observed.append(row)
assert all(x['present']is False for x in observed)
row={'result':'pass','components':reports,'checks':checks,'actualReplayChecks':sum(len(v)for v in checks.values()),'capturedCPUActors':observed,'helperTransactions':6,'namedComponentsExecuted':5,'eachExecutedOnce':True,'publicProviderRefusalAtPrivateRuntimeGuardOnly':True,'publicQSPositive':False,'finalAdmissionPrimitiveScopeOnly':True,'reliabilityAccepted':False,'firstHungFixtureCauseKnown':False,'GUI':False};p=B/'actual-required-components-replay-v1.json';assert not p.exists();p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({'result':'pass','report':str(p),'actualReplayChecks':row['actualReplayChecks'],'components':5,'helperTransactions':6}))
