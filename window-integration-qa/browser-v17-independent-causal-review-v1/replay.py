"""Bounded independent replay of immutable actual B17 evidence; no desktop IPC."""
from pathlib import Path
import base64,hashlib,json,os
B=Path('/home/hoskinson/window-integration-qa/browser-files-flow-v17');A=B/'attempt-1';E=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
f=load(A/'flow/report.json');r=load(A/'report.json');c=load(A/'flow/continuation-0.json');manifest=load(B/'frozen-inputs.json')
checks={}
def check(name,value):checks[name]=bool(value);assert value,name
identity=c['expectedBrowserIdentity'];process=c['expectedBrowserProcess'];keys=('address','stableId','pid')
def exact(peer):return isinstance(peer,dict) and all(peer.get(k)==identity[k] for k in keys)
check('retainedFailureAndExactly8ReachedOriginalPass',r['result']=='fail' and f['result']=='fail' and len(f['checks'])==len(r['toolkitFeatureGates'])==8 and all(x['passed']for x in f['checks']) and f['error']=="RuntimeError('Bounded actual observation timed out:actual continuation at retained caret')")
check('original15MandatoryInFrozenManifest',manifest['featureGates']==15 and manifest['continuationDiagnosticOriginalFeatureAcceptance'] is False)
check('capturedBrowserRootExact',identity['pid']==process['pid']==f['processRoots']['browser']['pid'] and process['start']==f['processRoots']['browser']['start'])
check('all23ActualSamplesBoundAndErrorFree',len(c['samples'])==23 and not any(s.get('errors')for s in c['samples']))
previous=0;observations=[]
for index,s in enumerate(c['samples']):
 for phase in ('before','after'):
  x=s[phase];check(f'sample{index}.{phase}.startAndSelectorExact',x['sameBrowserLifetime'] and x['samePrivateSelector'] and x['browserProcessStart']==x['browserProcessStartAfter']==process['start'] and x['privateSelectorBefore']==x['privateSelectorAfter']==c['selectedEnvironment']['HYPRLAND_INSTANCE_SIGNATURE'])
  check(f'sample{index}.{phase}.actualClientUnique',len([p for p in x['actualPrivateClients']if p['pid']==process['pid']])==1 and exact(next(p for p in x['actualPrivateClients']if p['pid']==process['pid'])))
  check(f'sample{index}.{phase}.coreAndSeatBrowserSeparately',exact(x['native']['nativeFocus']) and exact(x['seatKeyboard']['keyboardOwner']) and exact(x['seatKeyboard']['coreNativeFocus']) and x['seatKeyboard']['keyboardSurfacePresent'] and x['seatKeyboard']['keyboardResourcePresent'])
  check(f'sample{index}.{phase}.rawRepliesReconstruct',json.loads(x['seatKeyboardRaw'])==x['seatKeyboard'] and json.loads(x['keyboardEventsRaw'])==x['keyboardEvents'])
  check(f'sample{index}.{phase}.temporalOrder',x['monotonicNs']>=previous);previous=x['monotonicNs']
  check(f'sample{index}.{phase}.bufferBound',len(x['keyboardEvents'])<=512)
  observations.append({'sample':index,'phase':phase,'core':x['native']['nativeFocus']['address'],'seat':x['seatKeyboard']['keyboardOwner']['address'],'lastKeySequence':x['keyboardEvents'][-1]['sequence']})
check('beforeTypeCaptionIsOriginalAcceptedGate',c['acceptedCaptionDom']==f['checks'][-1]['dom'] and c['samples'][0]['dom']==c['acceptedCaptionDom'])
old=c['acceptedCaptionDom'];more=c['requestedContinuation'];start,end=old['selection'];expected=old['value'][:start]+more+old['value'][end:];missing=old['value'][:start]+more[1:]+old['value'][end:]
check('unchangedExpectedFullTextAndLeadingHyphen',more=='-continued0' and c['expectedValue']==expected and start==end==29)
check('all22DOMPollsHaveOnlyLeadingHyphenMissing',all(s['dom']['value']==missing and s['dom']['selection']==[39,39] and s['dom']['active']=='draft' for s in c['samples'][1:]))
check('samePageUrlTitleTimeOriginAcrossEveryPoll',all(s['dom']['url']==old['url'] and s['dom']['title']==old['title'] and s['dom']['timeOrigin']==old['timeOrigin']for s in c['samples']))
check('oneExactActualWtypeCommandAndNormalExit',len(c['commands'])==1)
cmd=c['commands'][0];p=cmd['actualOwnedProcess'];raw=base64.b64decode(p['rawCmdlineBase64'],validate=True)
check('actualKernelArgvAndExeExact',raw.endswith(b'\0') and raw.split(b'\0')[:-1]==[x.encode()for x in ['/usr/bin/wtype','-d','20','--',more]] and cmd['command']==['/usr/bin/wtype','-d','20','--',more] and p['exe']=='/usr/bin/wtype')
check('actualWtypeLifetimeUidAndExit',p['identity']==cmd['identity'] and p['lifetimeBefore'] and p['lifetimeAfter'] and not p['errors'] and p['statusFields']['Uid'].split()==[str(os.getuid())]*4 and cmd['returncode']==0 and cmd['normalExit'] and cmd['originalProcessGoneAfterWait'] and cmd['pidPathAbsentAfterWait'] and cmd['stdout']==cmd['stderr']=='')
baseline=c['samples'][0]['after']['keyboardEvents'][-1]['sequence'];events=[x for x in c['samples'][-1]['after']['keyboardEvents']if x['sequence']>baseline]
check('22SerialPrecoreEventsAndLeadingKeycode1Symbol45',len(events)==22 and [x['sequence']for x in events]==list(range(baseline+1,baseline+23)) and [(x['keycode'],x['keyState'],x['seatKeySymAtObservation'])for x in events[:2]]==[(1,1,45),(1,0,45)])
check('allNewPrecoreEventsSeatBrowserAndNotCancelledAtObservation',all(exact(x['seat']['keyboardOwner']) and x['seat']['keyboardSurfacePresent'] and not x['cancelledAtObservation']for x in events))
final=c['samples'][-1]['dom'];delta=final['events'][len(old['events']):]
check('originalEventHistoryImmutablePrefix',final['events'][:len(old['events'])]==old['events'])
check('actual11TrustedDownUpBut10Inputs',len(delta)==32 and sum(x['type']=='keydown'for x in delta)==11 and sum(x['type']=='keyup'for x in delta)==11 and sum(x['type']=='input'for x in delta)==10 and all(x['trusted'] and x['target']=='draft'for x in delta))
check('firstDownUpNoValueOrCaretMutation',[(x['type'],x['value'],x['selection'])for x in delta[:2]]==[('keydown',old['value'],old['selection']),('keyup',old['value'],old['selection'])])
inputs=[x for x in delta if x['type']=='input']
check('allRemainingCharactersInsertedAtExactRetainedCaret',all(x['value']==old['value'][:start]+more[1:n+2]+old['value'][end:] and x['selection']==[start+n+1]*2 for n,x in enumerate(inputs)))
check('all18MainAndNormalRecordedLifecycle',len(r['mainPreservation'])==18 and all(r['mainPreservation'].values()) and all(f['preservation'].values()) and r['cleanup']['probeUnloadedNormally'] and r['cleanup']['pluginUnloadedNormally'])
proof={'result':'pass','checks':checks,'artifacts':{str(p):sha(p)for p in (A/'report.json',A/'flow/report.json',A/'flow/continuation-0.json',B/'frozen-inputs.json',B/'compose.html',B/'continuation-primary-InputManager.cpp',B/'continuation-primary-wtype-v0.4-main.c')},'sampleCount':23,'nativeSeatSamples':46,'wtypePidStart':cmd['identity'],'actualCommand':cmd['command'],'precoreNewKeyEvents':22,'trustedDomDown':11,'trustedDomUp':11,'trustedDomInput':10,'oldCaret':29,'actualCaret':39,'expectedCaret':40,'finding':'Only leading hyphen missing; every remaining character inserted at original caret; actual core focus and Seat keyboard owner stayed exact Browser','notProved':['Final compositor send/cancel/IME/merge decision','DOM key/code/modifier/beforeinput identity of leading event','Physical hardware','Cause or installed-primary-source revision equivalence'],'originalFeatureAccepted':False,'nativeExecuted':False,'mainWrites':False,'observations':observations}
p=E/'causal-replay.json';assert not p.exists();p.write_text(json.dumps(proof,indent=2)+'\n');p.chmod(0o600);print(json.dumps({'result':'pass','checks':len(checks),'artifact':str(p),'sha256':sha(p),'finding':proof['finding']}))
