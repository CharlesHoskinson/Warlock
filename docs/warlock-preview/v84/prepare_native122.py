"""Use the current held GUI bridge in the unchanged owning native campaign."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-client-provider-native-v121'
target=repo/'implementation/warlock-client-provider-native-v122'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=parent/'component-manifest.json';held=json.loads(manifest.read_text());assert held['sourceHeld'] and held['passed']
for rel,row in held['files'].items():assert sha(parent/rel)==row['sha256'],rel
assert not target.exists()
def ignore(path,names):return [name for name in names if name in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path)==parent/'qa' and name.startswith(('native-','prepare-')))]
shutil.copytree(parent,target,ignore=ignore)
shutil.copy2(pathlib.Path(__file__).parent/'retirement-native-probe.cpp',target/'retirement-native-probe.cpp')
path=target/'qa/prepare.py';text=path.read_text()
old="provider=REPO/'implementation/warlock-preview-provider-v81'";assert text.count(old)==1
text=text.replace(old,"provider=REPO/'implementation/warlock-preview-provider-v84'")
marker=' assert all(sha(p)==h for p,h in inputs.items());';assert text.count(marker)==1
extra=''' retirementC=pathlib.Path(providerHeld['retirementCReport']);retirementCProof=json.loads(retirementC.read_text());assert retirementCProof['passed'] and [row['mode'] for row in retirementCProof['controls']]==['valid','retired','bad-clock','bad-request','regress'];inputs[str(retirementC)]=sha(retirementC);pre['retirementCReport']=str(retirementC)
 retirementDecoder=pathlib.Path(providerHeld['retirementDecoderReport']);retirementDecoderProof=json.loads(retirementDecoder.read_text());assert retirementDecoderProof['passed'] and retirementDecoderProof['namedScenarios']==13 and len(retirementDecoderProof['coupledTraces'])==25 and retirementDecoderProof['unsafeMutantsDetected']==3;inputs[str(retirementDecoder)]=sha(retirementDecoder);pre['retirementDecoderReport']=str(retirementDecoder)
 for proofPath,checked in [(retirementC,retirementCProof),(retirementDecoder,retirementDecoderProof)]:
  for rel,value in checked['inputs'].items():assert sha(provider/rel)==value,rel;inputs[str(provider/rel)]=value
  for rel,value in checked['artifacts'].items():assert sha(proofPath.parent/rel)==value,rel;inputs[str(proofPath.parent/rel)]=value
 prior121=REPO/'implementation/warlock-client-provider-native-v121/qa/native-1791317280340052228/report.json';proof121=json.loads(prior121.read_text());assert proof121['passed'] and proof121['cleanupPassed'] and len(proof121['checks'])==2458 and len(proof121['ownedExitCodes'])==276 and all(row['exitCode']==0 for row in proof121['ownedExitCodes']);inputs[str(prior121)]=sha(prior121);pre['retainedNative121Report']=str(prior121)
 retirement=OUT/'retirement-native-probe';dependency=OUT/'retirement-native-probe.d';retirementArgv=['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','-MD','-MF',str(dependency),'-I'+str(provider/'native'),str(ROOT/'retirement-native-probe.cpp'),str(provider/'native/imported-clients.cpp'),str(provider/'native/preview_uri.cpp'),str(provider/'native/preview-provider-bootstrap.cpp'),'-o',str(retirement),*growthFlags];retirementBuild=subprocess.run(retirementArgv,capture_output=True,text=True,timeout=180);(OUT/'retirement-native-compile.stdout').write_text(retirementBuild.stdout);(OUT/'retirement-native-compile.stderr').write_text(retirementBuild.stderr);assert retirementBuild.returncode==0,retirementBuild.stderr
 for dependencyPath in shlex.split(dependency.read_text().replace('\\\\\\n',' ').split(':',1)[1]):inputs[str(pathlib.Path(dependencyPath).resolve())]=sha(pathlib.Path(dependencyPath))
 for line in subprocess.check_output(['ldd',str(retirement)],text=True).splitlines():
  assert 'not found' not in line
  for word in line.split():
   if word.startswith('/') and pathlib.Path(word).is_file():inputs[str(pathlib.Path(word).resolve())]=sha(pathlib.Path(word))
 inputs[str(retirement)]=sha(retirement);pre['retirementNativeProbe']=str(retirement);r['retirementNativeBuild']={'argv':retirementArgv,'exitCode':retirementBuild.returncode,'sha256':sha(retirement)}
'''
text=text.replace(marker,extra+marker);ast.parse(text);path.write_text(text)
path=target/'qa/native.py';text=path.read_text()
marker="   writeControl(growthControl,'2 quit');growthSource.wait(timeout=5);check('receiverGrowthThirdSourceNormalExit',growthSource.returncode==0);wait(lambda:not any(row['pid']==growthSource.pid for row in s.data('clients')))"
assert text.count(marker)==1
before='''   retirementControl=s.host.runtime/'typed-retirement-control';writeControl(retirementControl,'hold')
   retirementProbe=s.host.launch('typed-native-retirement-probe',[pre['retirementNativeProbe'],str(config),growthThird[0],subject,str(retirementControl)],env=env)
   def typedRetirementRows():return [json.loads(line) for line in (private/'typed-native-retirement-probe.log').read_text().splitlines() if line.startswith('{')]
   ready=wait(lambda:next((row for row in typedRetirementRows() if row['stage']=='ready'),None))
   observed=[row['fact'] for row in typedRetirementRows() if row['stage']=='observation']
   check('typedNativeCOriginalActiveSubjects',len(observed)==2 and [row['subject'] for row in observed]==[growthThird[0],subject] and all(row['state']=='Active' and row['binding']==observed[0]['binding'] and row['clock']==row['binding']['lifetime'] for row in observed) and observed[0]['binding']!=attached['binding'],evidence=observed)
'''
after='''   writeControl(retirementControl,'closed');retirementProbe.wait(timeout=5)
   rows=typedRetirementRows();observed=[row['fact'] for row in rows if row['stage']=='observation'];complete=next((row for row in rows if row['stage']=='complete'),None)
   check('typedNativeCClosedAndRetainedNeighbor',len(observed)==4 and [row['state'] for row in observed]==['Active','Active','Retired','Active'] and [row['subject'] for row in observed]==[growthThird[0],subject,growthThird[0],subject] and all(row['binding']==observed[0]['binding'] and row['clock']==row['binding']['lifetime'] for row in observed),evidence=observed)
   check('typedNativeCSequenceClockFrontierContinuity',all(int(b['sequence'])>int(a['sequence']) and int(b['now'])>=int(a['now']) and int(b['issuedThrough'])>=int(a['issuedThrough']) for a,b in zip(observed,observed[1:])),evidence=observed)
   check('typedNativeCExactOriginalReservationsAndJournalDrain',retirementProbe.returncode==0 and complete and complete['passed'] and complete['checks']>=20 and not complete['actorTurnoverAccepted'],evidence=complete)
   r['typedNativeRetirementEvidence']={'observations':observed,'ready':ready,'complete':complete,'normalExit':retirementProbe.returncode==0,'scope':'Real own native C/socket/bootstrap/ImportedClients observations and original untouched reservation/journal cleanup; no actor removal, pixels or whole GUI release acceptance.'};r['typedNativeRetirementObservationBoundedQualified']=True
'''
text=text.replace(marker,before+marker+'\n'+after.rstrip())
marker=" check('allPriorNative118FixedOrderedAndActualRetryAssertionsRetained',len(prior118['checks'])==2467 and comparison['passed'],evidence=comparison)";assert text.count(marker)==1
extra="\n prior121=json.loads(pathlib.Path(pre['retainedNative121Report']).read_text());comparison121=compare(prior121,r,stableNames)\n check('allPriorNative121FixedOrderedAndActualRetryAssertionsRetained',len(prior121['checks'])==2458 and comparison121['passed'],evidence=comparison121)"
text=text.replace(marker,marker+extra);ast.parse(text);path.write_text(text)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),
 'purpose':'Unchanged owning core16/plugin18 and original121 runtime oracles/deadlines. Current GUI84 full Elm/native assets and typed C retirement boundary, real own native helper around the already required source closure. Preserve exact job/allocator/journal ownership and original ordered predicates; no actual actor removal or ordinary capture eligibility change.',
 'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),
 ['PROGRESS PUBLIC59 ba21f432 verified4548 ownerblobs, receipt70d888 local. Current GUI84 full95/typeddecoder13/25/439states/3mutants/Csocket five modes passed; original regression batch3708 live. Prepare native122 real typed C bridge observation around original source closure on exact core16/plugin18, retaining original121 runtime and physical/receipt/deadline gates. Next hold84/preflight122/serialized native, then atomic actor turnover beyond256; full release remains open.'],
 'progress',[str((target/'ANCESTRY.json').relative_to(repo))]))
