"""Reuse exact socket/peer/bootstrap fixture for new resume API controls."""
import hashlib,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v81');original=r/'native/resume-enrollment-test.cpp';out=r/'native/next-resume-test.cpp';assert not out.exists()
prefix=original.read_text().split('int main(',1)[0];old='mode=="resume-expire" && id>=5';assert prefix.count(old)==1;prefix=prefix.replace(old,'mode=="resume-expire" && id>=8')
body=r'''int main(int argc,char** argv){try{
 const std::string mode=argc>1?argv[1]:"next-resume";Server server("resume-expire");GError* error=nullptr;
 auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);check(bootstrap && !error,"Actual own successor-resume bootstrap");
 auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);auto popup=reinterpret_cast<gpointer>(uintptr_t(77));char* events=nullptr;char* feedback=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open_dynamic(transport,popup,21,1,1,&events,&raw,&error);check(owner && events && raw && !error,"Original actual source registration");const std::string registration(events);g_free(events);events=nullptr;
 auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);WarlockImportedAdmission admission;
 auto enroll=[&](uint64_t subject){check(warlock_imported_clients_enroll(owner,popup,subject,1,1,&admission,&events,&error) && !error && admission==WARLOCK_IMPORTED_STARTED,"Unrelated actual reservation");g_free(events);events=nullptr;};
 enroll(22);check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Original delivery/receiver");
 auto getJob=[&](uint64_t entry){return endpoint.native([&](auto& b){for(const auto& row:b.inspect())if(row.entry==entry)return row.job;throw std::runtime_error("Original native job");});};
 const auto original=getJob(1),other=getJob(2);
 auto proof=[&](uint64_t entry){auto job=getJob(entry);auto result=endpoint.native([&](auto& b){return b.producerRefused(entry,job);});char* pending=nullptr;check(warlock_preview_bootstrap_pending(bootstrap,popup,&pending,&error) && !error && pending,"Actual native proof discovery");std::string visible(pending);g_free(pending);return std::pair{result.receipts.back().sequence.value,visible};};
 auto ack=[&](uint64_t entry,uint64_t sequence){auto job=getJob(entry);Wire w;auto text=w.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",sequence).finish();auto identity="family:"+std::to_string(job.context.incarnation.value);check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity.c_str(),text.c_str(),&error) && !error,"Exact actual terminal ACK");};
 auto resume=[&](uint64_t publication,uint64_t lease){check(warlock_imported_clients_resume_next_feedback(owner,"family:21",publication,lease,&admission,&events,&feedback,&error) && !error,"Actual explicit C next-resume API");std::pair<std::string,std::string> value{events,feedback};g_free(events);g_free(feedback);events=feedback=nullptr;return value;};
 auto cutoff=[](const std::string& text){Json json("{\"values\":"+text+"}");auto rows=json_object_get_array_member(json.object(),"values");require(json_array_get_length(rows)==1,"Resume feedback without extra idle seed");return decimal(Json::text(json_node_get_object(json_array_get_element(rows,0)),"deadline"));};
 auto originalProof=proof(1);
 if(mode=="guard-retirement") {
  auto* native=static_cast<Native*>(transport);auto before=native->clientScope({21});auto refused=resume(3,2);auto after=native->clientScope({21});
  check(admission==WARLOCK_IMPORTED_INVALID && refused.first=="[]" && refused.second=="[]" && after.request==before.request+1,"Old terminal journal blocks succession before native query");
  check(endpoint.native([](auto& b){return b.recordCount()==2 && b.charge()==4096 && b.requestFloor(1)==1;}),"Old proof and other physical owner retained");
  ack(1,originalProof.first);auto remaining=proof(2);ack(2,remaining.first);
 }else if(mode=="guard-receiver") {
  ack(1,originalProof.first);auto view=*endpoint.registeredView(77);endpoint.unregisterView(77);check(endpoint.registerView(77,view.binding,view.entries),"Actual changed receiver epoch");
  auto* native=static_cast<Native*>(transport);auto before=native->clientScope({21});
  check(!warlock_imported_clients_resume_next_feedback(owner,"family:21",3,2,&admission,&events,&feedback,&error) && error && !events && !feedback,"Replacement cannot invoke next-resume API");g_clear_error(&error);auto after=native->clientScope({21});
  check(after.request==before.request+1 && endpoint.native([](auto& b){return b.recordCount()==1 && b.requestFloor(1)==1;}),"Receiver guard precedes native query and retains floor");
  endpoint.native([&](auto& b){auto result=b.producerRefused(2,other);require(b.acknowledge(2,other.binding,other,result.receipts.back().sequence),"Original native owner cleanup despite lost UI epoch");});
 }else {
  check(mode=="next-resume","Selected C fixture mode");ack(1,originalProof.first);enroll(23);check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error) && !error,"Same receiver journal extension");
  auto waiting=resume(3,2);check(admission==WARLOCK_IMPORTED_CAPACITY && waiting.first=="[]","Initial unissued resume retains floor");const auto oldCutoff=cutoff(waiting.second);
  auto pending=resume(5,3);check(admission==WARLOCK_IMPORTED_CONFLICT && cutoff(pending.second)==oldCutoff,"Pending intent cannot be replaced");
  auto partialPublication=resume(5,2);check(admission==WARLOCK_IMPORTED_CONFLICT && cutoff(partialPublication.second)==oldCutoff,"Publication alone cannot advance");
  auto partialLease=resume(3,3);check(admission==WARLOCK_IMPORTED_CONFLICT && cutoff(partialLease.second)==oldCutoff,"Lease alone cannot advance");
  auto expired=resume(3,2);check(admission==WARLOCK_IMPORTED_EXPIRED && expired.first=="[]" && cutoff(expired.second)==oldCutoff,"Same expired intent cannot renew");
  auto successor=resume(5,3);check(admission==WARLOCK_IMPORTED_CAPACITY && successor.first=="[]","Later explicit intent still respects physical capacity");const auto newCutoff=cutoff(successor.second);check(newCutoff>oldCutoff,"Successor cutoff from later native clock");
  check(warlock_imported_clients_status(owner,&events,&error) && !error,"Bounded predecessor status");Json status("{\"values\":"+std::string(events)+"}");g_free(events);events=nullptr;auto first=json_node_get_object(json_array_get_element(json_object_get_array_member(status.object(),"values"),0));
  check(decimal(Json::text(first,"resumeDeadline"))==newCutoff && decimal(Json::text(first,"previousResumeDeadline"))==oldCutoff && decimal(Json::text(first,"previousResumePublication"))==3 && decimal(Json::text(first,"previousResumeLease"))==2,"One exact unissued predecessor and current successor");
  auto oldReplay=resume(3,2);check(admission==WARLOCK_IMPORTED_CONFLICT && cutoff(oldReplay.second)==newCutoff,"Predecessor cannot replace current intent");
  auto retry=resume(5,3);check(admission==WARLOCK_IMPORTED_CAPACITY && cutoff(retry.second)==newCutoff,"Successor retry does not renew");
  check(endpoint.native([](auto& b){return b.recordCount()==2 && b.charge()==8192 && b.requestFloor(1)==1 && b.nextProofSequence()==2;}),"No fabricated successor job or proof");
  auto released=proof(3);ack(3,released.first);
  check(endpoint.native([](auto& b){auto wrong=b.nativeScope(1);wrong.context.privacy={1};return !b.observe(1,wrong,4096);}),"Actual retained native Broker incoherence");
  auto issued=resume(5,3);check(admission==WARLOCK_IMPORTED_NATIVE_REJECTED && issued.first!="[]" && issued.second=="[]","Real rejected successor is registered, never local feedback");const auto job=getJob(1);
  check(job.request.value==2 && job.deadline==newCutoff && job.binding==original.binding && job.context.incarnation==original.context.incarnation && job.clock==original.clock,"Exact next request with original successor cutoff");
  check(getJob(2)==other,"Other original job retains identity and deadline");
  check(warlock_preview_bootstrap_pending(bootstrap,popup,&events,&error) && events && !error,"Actual rejected successor terminal proof");const std::string receipts(events);g_free(events);events=nullptr;Wire originalWire,jobWire;
  std::cout<<"{\"originalRegistration\":"<<registration<<",\"originalReceipts\":"<<originalProof.second<<",\"originalJob\":"<<originalWire.job(original).finish()<<",\"waiting\":"<<waiting.second<<",\"expired\":"<<expired.second<<",\"successor\":"<<successor.second<<",\"registration\":"<<issued.first<<",\"receipts\":"<<receipts<<",\"job\":"<<jobWire.job(job).finish()<<",\"identity\":\"family:21\",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}"<<std::endl;
  bool acquired=false,settled=false;std::string text;
  while(std::getline(std::cin,text)) {
   Json command(text);const auto kind=std::string_view(Json::text(command.object(),"kind"));bool accepted=false;std::string emitted="[]";
   if(kind=="acquire") {check(!acquired && !settled,"One actual Elm acquire for known rejected successor");acquired=true;accepted=warlock_imported_clients_command(owner,"family:21",text.c_str(),&events,&error);check(accepted && !error && std::string_view(events)=="[]","Native rejection suppresses capture replay");emitted=events;g_free(events);events=nullptr;}
   else {require(kind=="acknowledge","Typed actual Elm terminal ACK");accepted=warlock_preview_bootstrap_acknowledge(bootstrap,popup,"family:21",text.c_str(),&error);check(!error,"Exact native terminal response");if(accepted)settled=true;}
   auto counters=endpoint.native([](auto& b){return std::pair{b.recordCount(),b.requestFloor(1)};});check(counters.second==2,"No reset of the retained native request floor");
   std::cout<<"{\"accepted\":"<<(accepted?"true":"false")<<",\"events\":"<<emitted<<",\"records\":"<<counters.first<<",\"floor\":"<<counters.second<<"}"<<std::endl;
  }
  check(acquired && settled,"Actual optimized Elm settles only the issued rejected successor");auto remaining=proof(2);ack(2,remaining.first);
 }
 check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"Normal exact C ownership closure");warlock_preview_bootstrap_free(bootstrap);server.finish();
 std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"mode\":\""<<mode<<"\",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}"<<std::endl;return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
'''
out.write_text(prefix+body);print(out)
