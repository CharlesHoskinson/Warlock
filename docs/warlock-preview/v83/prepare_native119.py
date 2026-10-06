"""Fresh full campaign for native18 retirement facts; preserve118 controls."""
import ast, hashlib, json, pathlib, resource, shutil, sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-client-provider-native-v118'
target=repo/'implementation/warlock-client-provider-native-v119'
native=repo/'implementation/warlock-family-style-crop-capture-v18'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
manifest=parent/'component-manifest.json';held=json.loads(manifest.read_text())
assert held['passed'] and held['sourceHeld'] and not target.exists()
assert json.loads((native/'component-manifest.json').read_text())['passed']
for name,row in held['files'].items():assert sha(parent/name)==row['sha256'],name
def ignore(path,names):return [name for name in names if name in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__','native-build-report.json'} or (pathlib.Path(path)==parent/'qa' and name.startswith(('native-','prepare-')))]
shutil.copytree(parent,target,ignore=ignore)
shutil.copy2(native/'native-build-report.json',target/'native-build-report.json')
path=target/'qa/prepare.py';text=path.read_text()
old="owner=REPO/'implementation/warlock-family-style-crop-capture-v17'";assert text.count(old)==1
text=text.replace(old,"owner=REPO/'implementation/warlock-family-style-crop-capture-v18'")
marker=' assert all(sha(p)==h for p,h in inputs.items());';assert text.count(marker)==1
extra=" retirementManifest=owner/'component-manifest.json';retirementHeld=json.loads(retirementManifest.read_text());assert retirementHeld['passed'] and retirementHeld['sourceHeld'];inputs[str(retirementManifest)]=sha(retirementManifest);pre['incarnationRetirementManifest']=str(retirementManifest)\n"
extra+=" for rel,row in retirementHeld['files'].items():assert sha(owner/rel)==row['sha256'],rel;inputs[str(owner/rel)]=row['sha256']\n"
extra+=" classifier=pathlib.Path(retirementHeld['modelReport']);classifierProof=json.loads(classifier.read_text());assert classifierProof['passed'] and classifierProof['namedScenarios']==8 and classifierProof['unsafeMutantsDetected']==2;inputs[str(classifier)]=sha(classifier);pre['incarnationRetirementClassifierReport']=str(classifier)\n"
extra+=" prior118=REPO/'"+str(pathlib.Path(held['nativeReport']).relative_to(repo))+"';proof118=json.loads(prior118.read_text());assert proof118['passed'] and proof118['cleanupPassed'] and len(proof118['checks'])==2467 and all(row['exitCode']==0 for row in proof118['ownedExitCodes']);inputs[str(prior118)]=sha(prior118);pre['retainedNative118Report']=str(prior118)\n"
text=text.replace(marker,extra+marker);ast.parse(text);path.write_text(text)
path=target/'qa/native.py';text=path.read_text()
marker='   def sourceScope():\n';assert text.count(marker)==1
extra='''   retirementObservations=[]
   def incarnationRetirement(targetSubject,expected):
    value=request('preview-incarnation-retirement-state-request',subjectIncarnation=targetSubject)
    check('incarnationRetirementExactNativeEnvelope-'+expected,set(value)=={'protocolVersion','kind','retirementProtocol','binding','requestId','subjectIncarnation','sequence','clock','now','issuedThrough','state'} and value['protocolVersion']==3 and value['kind']=='preview-incarnation-retirement-state' and value['retirementProtocol']==1 and value['binding']==attached['binding'] and value['requestId']==str(requestId) and value['subjectIncarnation']==targetSubject and value['clock']==attached['binding']['lifetime'] and value['state']==expected and int(value['sequence'])>0 and int(value['now'])>0,response=value)
    check('incarnationRetirementMonotonicFrontierAndClock-'+expected,(not retirementObservations or (int(value['sequence'])>int(retirementObservations[-1]['sequence']) and int(value['now'])>=int(retirementObservations[-1]['now']) and int(value['issuedThrough'])>=int(retirementObservations[-1]['issuedThrough']))) and (int(targetSubject)>int(value['issuedThrough']) if expected=='Future' else int(targetSubject)<=int(value['issuedThrough'])),response=value)
    retirementObservations.append(value);return value
   incarnationRetirement(subject,'Active')
   incarnationRetirement('18446744073709551615','Future')
   wrongBinding={**attached['binding'],'lifetime':str(int(attached['binding']['lifetime'])^1)}
   foreign=observe({'protocolVersion':3,'kind':'preview-incarnation-retirement-state-request','binding':wrongBinding,'requestId':'999999','subjectIncarnation':subject})
   check('incarnationRetirementForeignBindingRefused',foreign.get('kind')=='error' and foreign.get('reason')=='binding-mismatch',response=foreign)
   zero=request('preview-incarnation-retirement-state-request',subjectIncarnation='0')
   check('incarnationRetirementZeroSubjectRefused',zero.get('kind')=='error',response=zero)
'''
text=text.replace(marker,extra+marker)
marker="   check('stoppedActualFirstClassMinimized',minimizedMember['minimized'] is True,window=minimizedMember,outcome=minimizeOutcome)\n";assert text.count(marker)==1
text=text.replace(marker,marker+"   incarnationRetirement(subject,'Active')\n")
marker="   writeControl(growthControl,'2 quit');growthSource.wait(timeout=5);check('receiverGrowthThirdSourceNormalExit',growthSource.returncode==0);wait(lambda:not any(row['pid']==growthSource.pid for row in s.data('clients')))\n";assert text.count(marker)==1
text=text.replace(marker,marker+"   incarnationRetirement(growthThird[0],'Retired')\n   incarnationRetirement(subject,'Active')\n   r['incarnationRetirementNativeEvidence']={'observations':retirementObservations,'foreign':foreign,'zero':zero,'physicalRetirementAccepted':False,'actorTurnoverAccepted':False};r['nativeIncarnationRetirementObservationBoundedQualified']=True\n")
marker=" check('allPriorNative116StableOrderedAssertionsRetained',";start=text.index(marker);end=text.index('\n',start)+1
extra=" prior118=json.loads(pathlib.Path(pre['retainedNative118Report']).read_text());prior118Stable=stableNames(prior118['checks']);prior118Names=set(prior118Stable)\n check('allPriorNative118StableOrderedAssertionsRetained',len(prior118['checks'])==2467 and [name for name in stableNames(r['checks']) if name in prior118Names]==prior118Stable,stableControls=len(prior118Stable),priorRawControls=2467)\n"
text=text[:end]+extra+text[end:];ast.parse(text);path.write_text(text)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'nativeModuleManifest':str(native/'component-manifest.json'),'nativeModuleManifestSHA256':sha(native/'component-manifest.json'),'purpose':'Actual authenticated owning-core16/plugin18 incarnation retirement observation with original fullGUI81/native118 campaign. Existing real minimization/source destruction reused; new read-only observations cannot retire resources or change old deadlines/oracles. Retain all118 stable ordered identities.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),
 ['PROGRESS native18 retirement observation compiled/classifier8/20/438states/2mutants held. Fresh full native119 preserves118 GUI/controls/deadlines, adds authenticated live/minimized/future/foreign/zero/closed/read-only retirement facts using actual original source events. Next preflight then serial full owningABI native campaign. No actor removal/ordinary eligibility/fullrelease acceptance.'],
 'progress',[str((target/'ANCESTRY.json').relative_to(repo))]))
