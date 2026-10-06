"""Retain original114 gates and add actual same-host expiry/reopen capture."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-client-provider-native-v114';t=r/'implementation/warlock-client-provider-native-v115';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
m=p/'component-manifest.json';d=json.loads(m.read_text());assert d['passed'] and d['sourceHeld'] and not t.exists()
current=r/'implementation/warlock-preview-provider-v80/component-manifest.json';held=json.loads(current.read_text());assert held['passed'] and held['sourceHeld']
def ignore(path,names):return [n for n in names if n in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path)==p/'qa' and n.startswith(('native-','prepare-')))]
shutil.copytree(p,t,ignore=ignore)
f=t/'qa/native.py';s=f.read_text();marker="   web.terminate();web.wait(timeout=5);check('feedbackGUIFullHostNormalExit'";assert s.count(marker)==1
phase='''   # Preserve every initial feedback oracle above, then test a distinct
   # later picker intent in this SAME owner/receiver/Elm/broker instance.
   def nextIntentClick(label):
    pointerLog=private/('feedback-next-'+label+'.log')
    with pointerLog.open('xb') as output:ptr=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
    record=host.original.process(ptr.pid);record.update(name='feedback-next-'+label,command=[pre['pointer'],'800','600'],log=str(pointerLog));s.host.processes.append((ptr,record))
    ptr.communicate(('move '+str(fx)+' '+str(fy)+'\\nsleep 50\\nbutton 272 1\\nsleep 50\\nbutton 272 0\\nsleep 100\\n').encode(),timeout=5)
    check('nextIntentActualPointerNormalExit-'+label,ptr.returncode==0)
   closeOffset=len(fullLog());nextIntentClick('close');wait(lambda:'view-commit: popup=0 ' in fullLog()[closeOffset:])
   nextIntentClick('reopen')
   def nextThirdOffer():
    return next((event['event']['frame'] for event in events() if event['kind']=='event' and event['event']['kind']=='offer' and event['identity']=='family:'+growthThird[0]),None)
   nextOffer=wait(nextThirdOffer)
   nextSeed=next(event for event in events() if event['kind']=='source-seed' and event['identity']=='family:'+growthThird[0])
   nextRequests=[event['event']['trigger'] for event in events() if event['kind']=='event' and event['event']['kind']=='request' and event['identity']=='family:'+growthThird[0]]
   check('nextIntentGUIFirstThirdJobWithLaterPickerLease',len(nextRequests)==1 and nextOffer['job']['request']=='1' and int(nextSeed['publication'])>int(nativeCapacity[0]['publication']) and int(nextSeed['lease'])>int(nativeCapacity[0]['lease']),seed=nextSeed,offer=nextOffer)
   check('nextIntentGUIOriginalTwoSecondSuccessorCutoff',int(nextOffer['job']['deadline'])==int(nextSeed['source']['scope']['now'])+2000000000 and int(nextOffer['job']['deadline'])>int(cutoff),previous=cutoff,current=nextOffer['job']['deadline'])
   nextURI='elm-shell://preview/'+nextOffer['handle']
   def nextImages():
    return next((images for line in reversed(fullLog().splitlines()) if line.startswith('native-imported-image: ') for images in [json.loads(line[len('native-imported-image: '):])] if any(image['uri']==nextURI for image in images)),None)
   loadedThird=wait(nextImages)
   check('nextIntentGUIActualThirdOwnedURIComplete',any(image['uri']==nextURI and image['complete'] and image['naturalWidth']>0 and image['naturalHeight']>0 for image in loadedThird),images=loadedThird)
   wait(lambda:any(json.loads(line[len('native-imported-ack: '):])['job']==nextOffer['job'] for line in fullLog().splitlines() if line.startswith('native-imported-ack: ')))
   def nextPoolDrained():
    statuses=[json.loads(line[len('native-imported-status: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-status: ')]
    return statuses and all(row.get('records',0)==0 and int(row.get('charge','0'))==0 for row in statuses[-1])
   wait(nextPoolDrained)
   allNextCommands=[json.loads(line[len('native-imported-command: '):]) for line in fullLog().splitlines() if line.startswith('native-imported-command: ')]
   thirdAcquires=[command['job'] for command in allNextCommands if command['kind']=='acquire' and command['job']['context']['incarnation']==growthThird[0]]
   check('nextIntentGUIExactSingleThirdCaptureAndTerminalACK',thirdAcquires==[nextOffer['job']] and sum(json.loads(line[len('native-imported-ack: '):])['job']==nextOffer['job'] for line in fullLog().splitlines() if line.startswith('native-imported-ack: '))==1,job=nextOffer['job'])
   r['nextIntentGUIEvidence']={'sameHostPID':web.pid,'previousCutoff':cutoff,'seed':nextSeed,'offer':nextOffer,'images':loadedThird,'exactACK':True,'hardwarePresentation':False,'assistiveTechnologyAcceptance':False};r['nativeNextUnissuedIntentGUIBoundedQualified']=True
'''
s=s.replace(marker,phase+marker);ast.parse(s);f.write_text(s)
f=t/'qa/prepare.py';s=f.read_text();old="provider=REPO/'implementation/warlock-preview-provider-v76'";assert s.count(old)==1;s=s.replace(old,"provider=REPO/'implementation/warlock-preview-provider-v80'")
marker=" assert all(sha(p)==h for p,h in inputs.items());";assert s.count(marker)==1
added=" nextIntentReport=pathlib.Path(providerHeld['nextIntentReport']);nextProof=json.loads(nextIntentReport.read_text());assert nextProof['passed'] and nextProof['namedScenarios']==10 and nextProof['unsafeMutantsDetected']==2 and nextProof['wireControls']['checks']==21 and nextProof['wireControls']['cControls']==45;inputs[str(nextIntentReport)]=sha(nextIntentReport);pre['nextIntentReport']=str(nextIntentReport)\n"
s=s.replace(marker,added+marker);ast.parse(s);f.write_text(s)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),'providerManifest':str(current),'providerManifestSHA256':sha(current),'purpose':'Original114 native controls retained, current80 unissued-priority host. New actual pointer close/reopen and third owned image through same original bootstrap/receiver/Elm/pool after expired unissued intent. Original cutoffs/limits/owningABI and normal ordered cleanup unchanged. No hardware/AT/ordinary eligible/full release claim.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
print(json.dumps({'source':str(t),'nativeLaunched':False,'next':'Review/preflight then serialized original protected native launcher.'}))
