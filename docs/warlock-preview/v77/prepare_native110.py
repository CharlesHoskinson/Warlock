"""Prepare full native feedback GUI qualification with all109 controls retained."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-client-provider-native-v109';t=r/'implementation/warlock-client-provider-native-v110';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
m=p/'component-manifest.json';d=json.loads(m.read_text());assert d['passed'] and not t.exists()
for name,row in d['files'].items():assert sha(p/name)==row['sha256'],name
def ignore(path,names):return [n for n in names if n in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path).name=='qa' and n.startswith(('native-','prepare-')))]
shutil.copytree(p,t,ignore=ignore)
f=t/'qa/prepare.py';s=f.read_text();old="provider=REPO/'implementation/warlock-preview-provider-v71'";assert s.count(old)==1;s=s.replace(old,"provider=REPO/'implementation/warlock-preview-provider-v74'")
old="assert len(providerProof['commands'])==94";assert s.count(old)==1;s=s.replace(old,"assert len(providerProof['commands'])==95")
marker=" assert all(sha(p)==h for p,h in inputs.items());";assert s.count(marker)==1
addition=" feedbackReport=pathlib.Path(providerHeld['feedbackReport']);feedbackProof=json.loads(feedbackReport.read_text());assert feedbackProof['passed'] and feedbackProof['namedScenarios']==9 and len(feedbackProof['coupledTraces'])==21 and feedbackProof['nativeFixtureControls']['passed'];inputs[str(feedbackReport)]=sha(feedbackReport);pre['feedbackReport']=str(feedbackReport)\n"
s=s.replace(marker,addition+marker);f.write_text(s)
f=t/'qa/native.py';s=f.read_text();marker="   writeControl(growthControl,'2 quit');";assert s.count(marker)==1
addition='''   # Full current Elm/Main/Bar/Popup with three native subjects, one original
   # two-item pool, and the original trusted child bootstrap/receipt endpoint.
   fullLogName='full-imported-feedback'
   web=s.host.launch(fullLogName,[pre['fullHostBinary'],'--assets',pre['fullHostAssets'],'--backend',pre['fullHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open','--qa-preview-imported-dynamic',subject,importPeer,growthThird[0],'--qa-preview-snapshot',str(private/'feedback-webkit.png')],env=env)
   target=wait(sourceButton);fx=round(target['x']+target['width']/2);fy=round(target['y']+target['height']/2);check('feedbackGUIActualGroupPointerInOutput',0<fx<800 and 0<fy<48)
   pointerLog=private/'feedback-pointer.log'
   with pointerLog.open('xb') as output:ptr=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
   record=host.original.process(ptr.pid);record.update(name='feedback-pointer',command=[pre['pointer'],'800','600'],log=str(pointerLog));s.host.processes.append((ptr,record))
   ptr.communicate(('move 10 550\\nsleep 100\\nmove '+str(fx)+' '+str(fy)+'\\nsleep 100\\nbutton 272 1\\nsleep 50\\nbutton 272 0\\nsleep 100\\n').encode(),timeout=5);check('feedbackGUIActualPointerNormalExit',ptr.returncode==0)
   def feedbackPopup(label):
    rows=[json.loads(line[len('surface-report: origin=popup '):]) for line in fullLog().splitlines() if line.startswith('surface-report: origin=popup ')]
    return next((row for row in reversed(rows) if label in row['body']['text']),None)
   waitingGUI=wait(lambda:feedbackPopup('Waiting for preview capacity'))
   nativeLocal=[event for line in fullLog().splitlines() if line.startswith('native-imported-feedback: ') for event in json.loads(line[len('native-imported-feedback: '):]) if event['kind']=='demand-feedback']
   nativeCapacity=[event for event in nativeLocal if event['outcome']=='capacity' and event['subject']==growthThird[0]]
   check('feedbackGUICapacityFromActualOwnNativeScope',len(nativeCapacity)>0 and nativeCapacity[0]['publication']==waitingGUI['body']['publication'] and nativeCapacity[0]['lease']==waitingGUI['body']['lease'] and all(not any(key in event for key in ['job','receipt','token']) for event in nativeCapacity),native=nativeCapacity,rendered=waitingGUI)
   wait(lambda:'native-imported-image:' in fullLog())
   cutoff=nativeCapacity[0]['deadline'];feedbackBatches=events();firstOffers=[event['event']['frame'] for event in feedbackBatches if event['kind']=='event' and event['event']['kind']=='offer']
   check('feedbackGUIOriginalTwoRealOwnersWhileThirdWaits',len(firstOffers)==2 and {frame['job']['context']['incarnation'] for frame in firstOffers}=={subject,importPeer} and any(event['kind']=='demand-seed' and event['identity']=='family:'+growthThird[0] for event in feedbackBatches),offers=firstOffers)
   wait(lambda:'native-imported-complete: physical=0 journal=0 previewEligible=0' in fullLog())
   finalBatches=events();thirdJobs=[event['event']['trigger'] for event in finalBatches if event['kind']=='event' and event['event']['kind']=='request' and event['identity']=='family:'+growthThird[0]]
   finalLocal=[event for line in fullLog().splitlines() if line.startswith('native-imported-feedback: ') for event in json.loads(line[len('native-imported-feedback: '):]) if event['kind']=='demand-feedback' and event['subject']==growthThird[0]]
   expiredGUI=feedbackPopup('Preview request expired') if thirdJobs else wait(lambda:feedbackPopup('Preview request expired'))
   check('feedbackGUIOriginalCutoffCannotRenew',all(event['deadline']==cutoff for event in finalLocal) and all(job['deadline']==cutoff for job in thirdJobs) and (bool(thirdJobs) or (any(event['outcome']=='expired' for event in finalLocal) and bool(expiredGUI))),local=finalLocal,issued=thirdJobs,expired=expiredGUI)
   actualCommands=[json.loads(line[len('native-imported-command: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-command: ')]
   actualACKs=[json.loads(line[len('native-imported-ack: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-ack: ')]
   actualOffers=[event['event']['frame'] for event in finalBatches if event['kind']=='event' and event['event']['kind']=='offer'];acquires=[command['job'] for command in actualCommands if command['kind']=='acquire']
   check('feedbackGUIOnlyActualIssuedJobsCaptureAndSettle',len(acquires)==len(actualOffers)==len(actualACKs)==2+len(thirdJobs) and {json.dumps(job,sort_keys=True) for job in acquires}=={json.dumps(ack['job'],sort_keys=True) for ack in actualACKs},commands=actualCommands,acks=actualACKs)
   # DOM text and actual owned URI loading are distinct from hardware/AT acceptance.
   check('feedbackGUIActualOwnedImagesLoaded','native-imported-image:' in fullLog() and 'native-client-webkit-snapshot: saved=1 hardwarePresentation=0' in fullLog())
   web.terminate();web.wait(timeout=5);check('feedbackGUIFullHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in fullLog() and 'Native imported teardown incomplete:' not in fullLog())
   r['localFeedbackGUIEvidence']={'waiting':waitingGUI,'expired':expiredGUI,'originalCutoff':cutoff,'thirdIssuedJobs':thirdJobs,'nativeLocal':finalLocal,'actualACKs':actualACKs,'hardwarePresentation':False,'assistiveTechnologyAcceptance':False};r['nativeLocalFeedbackGUIBoundedQualified']=True
'''
s=s.replace(marker,addition+marker);f.write_text(s)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),'purpose':'Qualify current full GUI74 feedback with own native child grant, explicit dynamic membership/receipt extension, same two-item pool, three real windows and native capacity label/cutoff/cleanup. Retain all109 original controls, deadlines and owning core16/plugin17/AQ155. DOM and URI evidence are not hardware/AT/ordinaryeligible/fullrelease acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
print(json.dumps({'source':str(t)}))
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS fullGTKfeedback production/nativeC/Elm implemented in ownedGUI74; native110 fresh from held109 preserves alloriginalcontrols and original deadlines. Own additive3-window fullGUIcapacity text + original cutoff + exactissuedonlyCapture/ACK + normalcleanup route uses unchanged owncore16/plugin17/AQ155. CPU source/preflight prerequisites thenserializednative; all original fullrelease gatesactive.'],'progress',[str((t/'ANCESTRY.json').relative_to(r))]);print(json.dumps({'checkpoint':str(e)}))
