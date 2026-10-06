"""Build a distinct monotonic-observation fixture for actual C resume checks."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v67')
prefix=(r/'native/rejected-enrollment-test.cpp').read_text().split('int main(){try{')[0]
assert prefix.count('.counter("observation",UINT64_MAX)')==1
prefix=prefix.replace('.counter("observation",UINT64_MAX)','.counter("observation",id)').replace('mode=="expire-wait" && id>=4','mode=="resume-expire" && id>=5')
prefix='#include <thread>\n'+prefix
body=r'''int main(int argc,char** argv){try{
 const std::string mode=argc>1?argv[1]:"normal";Server server(mode);GError* error=nullptr;auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);check(bootstrap && !error,"Own resume native C bootstrap");
 auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);auto popup=reinterpret_cast<gpointer>(uintptr_t(77));char* events=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open_dynamic(transport,popup,21,1,1,&events,&raw,&error);check(owner && events && raw && !error,"Original resume C source");g_free(events);events=nullptr;
 auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);WarlockImportedAdmission admission;
 auto enroll=[&](uint64_t subject){check(warlock_imported_clients_enroll(owner,popup,subject,1,1,&admission,&events,&error) && admission==WARLOCK_IMPORTED_STARTED && !error,"Own unrelated C reservation");g_free(events);events=nullptr;};
 enroll(22);check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Original C resume journal");
 auto getJob=[&](uint64_t entry){return endpoint.native([&](auto& b){for(const auto& row:b.inspect())if(row.entry==entry)return row.job;throw std::runtime_error("Owned original job");});};
 auto settle=[&](uint64_t entry){auto job=getJob(entry);auto proof=endpoint.native([&](auto& b){return b.producerRefused(entry,job);});Wire ack;auto message=ack.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",proof.receipts.back().sequence.value).finish();auto identity="family:"+std::to_string(job.context.incarnation.value);check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity.c_str(),message.c_str(),&error) && !error,"Actual original final proof and exact C ACK");};
 const auto prior=getJob(1);
 check(warlock_imported_clients_resume_at(owner,"family:21",2,2,&admission,&events,&error) && admission==WARLOCK_IMPORTED_INVALID && std::string_view(events)=="[]" && !error,"Existing actual record prevents resume and intent");g_free(events);events=nullptr;
 settle(1);enroll(23);check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Explicit same journal membership extension");
 if(mode=="replace-receiver"){
  auto view=*endpoint.registeredView(77);endpoint.unregisterView(77);check(endpoint.registerView(77,view.binding,view.entries),"Receiver replacement epoch");
  auto* native=static_cast<Native*>(transport);const auto before=native->clientScope({21});
  check(!warlock_imported_clients_resume_at(owner,"family:21",2,2,&admission,&events,&error) && error && !events,"Replaced receiver refuses typed C resume");g_clear_error(&error);
  const auto after=native->clientScope({21});check(after.request==before.request+1,"Receiver refusal occurs before any native scope query");
  check(endpoint.native([](auto& b){return b.requestFloor(1)==1 && b.recordCount()==2 && b.charge()==8192;}),"Receiver loss retains other actual jobs and own floor");
  // Original UI receipt receiver is intentionally gone. Owned physical cleanup
  // and exact native ACK remain possible; no record reset or invented UI ACK.
  endpoint.native([](auto& b){for(const auto& row:b.inspect()){auto proof=b.producerRefused(row.entry,row.job);require(b.acknowledge(row.entry,row.job.binding,row.job,proof.receipts.back().sequence),"Owned stale receiver native settlement");}});
 }else{
  bool foreignAccepted=true;std::thread foreign([&]{GError* deniedError=nullptr;char* ignored=nullptr;WarlockImportedAdmission deniedAdmission;foreignAccepted=warlock_imported_clients_resume_at(owner,"family:21",2,2,&deniedAdmission,&ignored,&deniedError);check(!foreignAccepted && deniedError && !ignored,"Foreign thread cannot admit resume");g_clear_error(&deniedError);});foreign.join();check(!foreignAccepted,"Creator thread guard retained");
  check(warlock_imported_clients_resume_at(owner,"family:21",2,2,&admission,&events,&error) && admission==WARLOCK_IMPORTED_CAPACITY && std::string_view(events)=="[]" && !error,"Actual resume Capacity has no issued job or proof");g_free(events);events=nullptr;
  check(warlock_imported_clients_status(owner,&events,&error) && !error,"Retained resume intent status");std::string snapshot(events);g_free(events);events=nullptr;
  auto marker=snapshot.find("\"resumeDeadline\":\"");check(marker!=snapshot.npos,"Original cutoff discoverable without fake job");marker+=18;auto end=snapshot.find('"',marker);auto deadline=decimal(std::string_view(snapshot).substr(marker,end-marker));
  check(endpoint.native([](auto& b){return b.requestFloor(1)==1 && b.recordCount()==2 && b.nextProofSequence()==2;}),"Local Capacity does not advance floor or terminal sequence");
  if(mode!="resume-expire"){
   check(warlock_imported_clients_resume_at(owner,"family:21",3,2,&admission,&events,&error) && admission==WARLOCK_IMPORTED_CONFLICT && std::string_view(events)=="[]" && !error,"Changed pending publication conflicts");g_free(events);events=nullptr;
  }
  settle(3);
  if(mode=="reject")check(endpoint.native([](auto& b){auto incoherent=b.nativeScope(1);incoherent.context.privacy={1};return !b.observe(1,incoherent,4096);}),"Actual retained Broker incoherence");
  check(warlock_imported_clients_resume_at(owner,"family:21",2,2,&admission,&events,&error) && !error,"Actual typed resume retry");
  if(mode=="resume-expire"){
   check(admission==WARLOCK_IMPORTED_EXPIRED && std::string_view(events)=="[]" && endpoint.native([](auto& b){return b.requestFloor(1)==1 && b.recordCount()==1;}),"Capacity returning after original cutoff cannot revive intent");g_free(events);events=nullptr;
  }else{
   check(admission==(mode=="reject"?WARLOCK_IMPORTED_NATIVE_REJECTED:WARLOCK_IMPORTED_STARTED) && std::string_view(events)!="[]","Real issued resume job registers before any proof");std::string registration(events);g_free(events);events=nullptr;
   const auto job=getJob(1);check(job.deadline==deadline && job.request.value==2 && prior.request.value==1 && job.binding==prior.binding,"Exact resumed job keeps original cutoff and monotonic identity");
   if(mode=="reject"){
    check(warlock_preview_bootstrap_pending(bootstrap,popup,&events,&error) && !error,"Actual resumed rejection proof discoverable");std::string receipts(events);g_free(events);events=nullptr;Wire w;
    std::cout<<"{\"registration\":"<<registration<<",\"receipts\":"<<receipts<<",\"job\":"<<w.job(job).finish()<<",\"identity\":\"family:21\",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}"<<std::endl;
    std::string request;bool acquired=false,settled=false;
    while(std::getline(std::cin,request)){
     Json value(request);auto kind=std::string_view(Json::text(value.object(),"kind"));bool accepted=false;std::string emitted="[]";
     if(kind=="acquire"){check(!acquired && !settled,"One actual Elm resume acquire");acquired=true;accepted=warlock_imported_clients_command(owner,"family:21",request.c_str(),&events,&error);check(accepted && !error && std::string_view(events)=="[]","Rejected resume suppresses capture");emitted=events;g_free(events);events=nullptr;}
     else{require(kind=="acknowledge","Exact actual Elm ACK");accepted=warlock_preview_bootstrap_acknowledge(bootstrap,popup,"family:21",request.c_str(),&error);check(!error,"Own resume terminal result");if(accepted)settled=true;}
     const auto counters=endpoint.native([](auto& b){return std::pair{b.recordCount(),b.requestFloor(1)};});check(counters.second==2,"Resume floor never reset");
     std::cout<<"{\"accepted\":"<<(accepted?"true":"false")<<",\"events\":"<<emitted<<",\"records\":"<<counters.first<<",\"floor\":"<<counters.second<<"}"<<std::endl;
    }
    check(acquired && settled,"Actual optimized Elm resume job settled");
   }else settle(1);
  }
  settle(2);
 }
 check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"Exact original cleanup and C close");warlock_preview_bootstrap_free(bootstrap);server.finish();
 if(mode!="reject")std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"nativeAcceptance\":false,\"mode\":\""<<mode<<"\"}"<<std::endl;return 0;
}catch(const std::exception& exception){std::cerr<<exception.what()<<'\n';return 1;}}
'''
target=r/'native/resume-enrollment-test.cpp';assert not target.exists();target.write_text(prefix+body)
js=(r/'qa/rejected-enrollment-replay.js').read_text()
js=js.replace("spawn(process.argv[2],[],","spawn(process.argv[2],['reject'],").replace("publication:'1',lease:'1'","publication:'2',lease:'2'").replace('actual.floor===1','actual.floor===2')
target=r/'qa/resume-enrollment-replay.js';assert not target.exists();target.write_text(js)
print(str(target))
