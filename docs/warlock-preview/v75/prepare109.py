"""Own native109 preserving original tuple, controls, pixels and deadlines."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-client-provider-native-v108';t=r/'implementation/warlock-client-provider-native-v109';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
m=p/'component-manifest.json';d=json.loads(m.read_text());assert d['passed'] and not t.exists()
for rel,row in d['files'].items():assert sha(p/rel)==row['sha256'],rel
def ignore(path,names):return [n for n in names if n in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path).name=='qa' and (n.startswith('native-') or n.startswith('prepare-')))]
shutil.copytree(p,t,ignore=ignore)
f=t/'qa/prepare.py';s=f.read_text();old="provider=REPO/'implementation/warlock-preview-provider-v65'";assert s.count(old)==1;s=s.replace(old,"provider=REPO/'implementation/warlock-preview-provider-v71'")
marker=" assert all(sha(p)==h for p,h in inputs.items());";assert s.count(marker)==1
added=" resumeReport=pathlib.Path(providerHeld['resumeModelReport']);resumeProof=json.loads(resumeReport.read_text());assert resumeProof['passed'] and resumeProof['namedScenarios']==8 and resumeProof['unsafeMutantsDetected']==3;inputs[str(resumeReport)]=sha(resumeReport);pre['resumeIntentModelReport']=str(resumeReport)\n receiptReport=pathlib.Path(providerHeld['receiptModelReport']);receiptProof=json.loads(receiptReport.read_text());assert receiptProof['passed'] and receiptProof['namedScenarios']==8 and receiptProof['unsafeCounterexamplesDetected']==2;inputs[str(receiptReport)]=sha(receiptReport);pre['receiptCorrelationModelReport']=str(receiptReport)\n cReport=pathlib.Path(providerHeld['resumeCReport']);cProof=json.loads(cReport.read_text());assert cProof['passed'] and cProof['checks']==79 and cProof['elmEvidence']['checks']==17;inputs[str(cReport)]=sha(cReport);pre['resumeCReport']=str(cReport)\n"
s=s.replace(marker,added+marker);f.write_text(s)
f=t/'dynamic-enrollment-probe.cpp';s=f.read_text()
old='const auto keepReader=[&](uint64_t entry){';new='const auto keepReader=[&](uint64_t entry,const std::string& suffix=""){';assert s.count(old)==1;s=s.replace(old,new)
old='std::to_string(entry)+".png"';new='std::to_string(entry)+suffix+".png"';assert s.count(old)==1;s=s.replace(old,new)
marker=' release(1);check(g_input_stream_read';assert s.count(marker)==1
added=''' char* resumeEvents=nullptr;WarlockImportedAdmission resumeAdmission=WARLOCK_IMPORTED_INVALID;const auto secondIdentity="family:"+std::to_string(subjects[1]);const auto priorSecond=jobs[1];
 check(warlock_imported_clients_resume_at(cowner,secondIdentity.c_str(),2,2,&resumeAdmission,&resumeEvents,&error) && !error && resumeEvents && resumeAdmission==WARLOCK_IMPORTED_CAPACITY && std::string_view(resumeEvents)=="[]","Actual native resume capacity without fake job or proof");g_free(resumeEvents);resumeEvents=nullptr;
 Json resumeStatus(ownershipStatus(2));const auto resumeDeadline=resumeStatus.counter("resumeDeadline");check(resumeDeadline && endpoint.native([](auto& b){return b.activeItems()==2 && b.recordCount()==2 && b.requestFloor(2)==1;}),"Actual native waiting resume retains original floor and other physical jobs");
'''
s=s.replace(marker,added+marker)
marker=' release(3);drain(3);';assert s.count(marker)==1
added=''' check(warlock_imported_clients_resume_at(cowner,secondIdentity.c_str(),2,2,&resumeAdmission,&resumeEvents,&error) && !error && resumeEvents && resumeAdmission==WARLOCK_IMPORTED_STARTED && std::string_view(resumeEvents)!="[]","Actual native resume after exact original physical drain and ACK");g_free(resumeEvents);resumeEvents=nullptr;
 jobs[1]=job(2);sequences[1]=0;check(jobs[1].deadline==resumeDeadline && jobs[1].request.value==2 && jobs[1].origin.value==2 && jobs[1].binding==priorSecond.binding && jobs[1].clock==priorSecond.clock,"Actual native resumed job keeps original waiting cutoff and identity domain");
 acquire(2);keepReader(2,".resume");check(endpoint.native([](auto& b){return b.activeItems()==2 && b.recordCount()==2 && b.requestFloor(2)==2 && b.requestFloor(3)==1;}),"Actual resumed FD mapping shares unchanged pool and third original job");
 release(2);drain(2);check(acknowledge(2) && !acknowledge(2),"Actual resumed physical/backend/FD/GIO drain precedes exact new final ACK");
'''
s=s.replace(marker,added+marker)
marker=' check(warlock_imported_clients_close(cowner,&error)';assert s.count(marker)==1
added=''' auto originalView=*endpoint.registeredView(receiver);endpoint.unregisterView(receiver);check(endpoint.registerView(receiver,originalView.binding,originalView.entries),"Explicit actual native receiver replacement");const auto beforeResumeRefusal=native->clientScope({subjects[1]});
 check(!warlock_imported_clients_resume_at(cowner,secondIdentity.c_str(),3,3,&resumeAdmission,&resumeEvents,&error) && error && !resumeEvents,"Actual replaced receiver refuses typed native resume");g_clear_error(&error);
 check(!warlock_imported_clients_resume(cowner,secondIdentity.c_str(),3,3,&resumeEvents,&error) && error && !resumeEvents,"Actual replaced receiver refuses legacy native resume");g_clear_error(&error);
 const auto afterResumeRefusal=native->clientScope({subjects[1]});check(afterResumeRefusal.request==beforeResumeRefusal.request+1,"Both actual receiver refusals happen before native scope queries");check(endpoint.native([](auto& b){return b.recordCount()==0 && b.charge()==0 && b.requestFloor(1)==1 && b.requestFloor(2)==2 && b.requestFloor(3)==1;}),"Actual native resume cleanup preserves all independent request floors");
'''
s=s.replace(marker,added+marker)
old='<<checks<<",\\"providerPID\\"';new='<<checks<<",\\"resumeDeadlineRetained\\":true,\\"receiverResumeGuard\\":true,\\"providerPID\\"';assert s.count(old)==1;s=s.replace(old,new);f.write_text(s)
f=t/'qa/native.py';s=f.read_text();marker="   r['dynamicEnrollmentNativeEvidence']=";assert s.count(marker)==1
added="   check('dynamicResumeActualOriginalCapacityCutoffAndReceiverQueryGuard',dynamicProof['resumeDeadlineRetained'] and dynamicProof['receiverResumeGuard'])\n   resumedDynamic=dynamicPixels(pathlib.Path(str(dynamicPrefix)+'.2.resume.png'));check('dynamicResumeActualMappedPixelsExcludeOtherOriginalSources',resumedDynamic['width']==320 and resumedDynamic['height']==240 and resumedDynamic['green']>0 and resumedDynamic['red']==0 and resumedDynamic['blue']==0,pixels=resumedDynamic)\n"
# Reuse the unchanged exact PNG decoder used by original dynamic specimens.
start=s.index('   dynamicFrames=');line=s[start:s.index('\n',start)];assert 'dynamicPrefix' in line
decoder=line.split('=')[1].split('(')[0].lstrip('[').strip();assert decoder and decoder.isidentifier(),decoder
added=added.replace('dynamicPixels(',decoder+"('dynamic-resume',");s=s.replace(marker,added+marker);f.write_text(s)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),'purpose':'Qualify changed fullGUI71 and actual dynamic C resume retained original cutoff across physical capacity return, exact independent drain/ACK, additional independent resumed PNG, and original receiver guard before native query. Original108 oracles/deadlines and exact owning core/plugin unchanged.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS GUI71 full94/C79/Elm17/newreceipt8/214states/2actualoldcounterexamples pass; native resume8/584states3mutants and demand10/delivery6 retained from unchanged69native. Fresh109 owns exact108 tuple, oldchecks/oracles/deadlines unchanged plus actualresumeCcapacity/retainedcutoff/newphysicaldrain/ACK/independentPNG/receiverqueryguard. CPUpreflight thenserializednative; alloriginalfullreleasegatesactive.'],'progress',[str((t/'ANCESTRY.json').relative_to(r))]);print(json.dumps({'source':str(t),'checkpoint':str(e)}))
