"""Prepare reviewed feedback fixtures without modifying the live build inputs."""
from pathlib import Path
r=Path('/home/hoskinson/omarchy-windows-parity');root=r/'implementation/warlock-preview-provider-v72'
old=(root/'native/resume-enrollment-test.cpp').read_text().split('int main(int argc,char** argv)')[0]
old=old.replace('(mode=="resume-expire" && id>=5?', '(mode=="feedback-expire" && id>=4?')
assert 'mode=="feedback-expire" && id>=4' in old
body=r'''int main(int argc,char** argv){try{
 const std::string mode=argc>1?argv[1]:"normal";Server server(mode);GError* error=nullptr;
 auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);check(bootstrap && !error,"Own feedback bootstrap");
 auto native=warlock_preview_bootstrap_native_transport(bootstrap,&error);gpointer popup=reinterpret_cast<gpointer>(uintptr_t(77));
 char* events=nullptr;char* feedback=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open_dynamic(native,popup,21,1,1,&events,&raw,&error);
 check(owner && events && raw && !error,"Original dynamic source");g_free(events);events=nullptr;
 check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Original delivery");
 auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);WarlockImportedAdmission admission;
 auto enroll=[&](uint64_t subject){
  check(warlock_imported_clients_enroll_feedback(owner,popup,subject,1,1,&admission,&events,&feedback,&error) && !error,"Typed feedback enrollment");
  std::pair<std::string,std::string> outputs{events,feedback};g_free(events);g_free(feedback);events=feedback=nullptr;
  check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error) && !error,"Explicit original delivery extension");return outputs;
 };
 auto second=enroll(22);check(admission==WARLOCK_IMPORTED_STARTED && second.second=="[]","Issued job has no local feedback");
 auto waiting=enroll(23);check(admission==WARLOCK_IMPORTED_CAPACITY && waiting.first=="[]","Third source waits without fabricated job");
 Json capacity("{\"values\":"+waiting.second+"}");auto array=json_object_get_array_member(capacity.object(),"values");
 check(json_array_get_length(array)==2,"Distinct idle source and local outcome");
 auto local=json_node_get_object(json_array_get_element(array,1));
 check(std::string_view(Json::text(local,"kind"))=="demand-feedback" && std::string_view(Json::text(local,"outcome"))=="capacity","Actual local wire outcome");
 auto deadline=decimal(Json::text(local,"deadline"));auto sequence=decimal(Json::text(local,"sequence"));
 check(decodeBinding(Json::child(local,"binding"))==static_cast<Native*>(native)->binding() && decimal(Json::text(local,"subject"))==23 && decimal(Json::text(local,"clock"))==UINT64_MAX,"Actual own lossless source identity");
 check(endpoint.native([](auto& b){return b.recordCount()==2 && b.charge()==8192 && b.requestFloor(3)==0 && b.nextProofSequence()==1;}),"Feedback does not issue job, advance floor or create proof");
 auto getJob=[&](uint64_t entry){return endpoint.native([&](auto& b){for(const auto& row:b.inspect())if(row.entry==entry)return row.job;throw std::runtime_error("Actual owned job");});};
 auto settle=[&](uint64_t entry){
  auto job=getJob(entry);auto proof=endpoint.native([&](auto& b){return b.producerRefused(entry,job);});char* pending=nullptr;
  check(warlock_preview_bootstrap_pending(bootstrap,popup,&pending,&error) && pending && !error,"Original proof discovery");g_free(pending);
  Wire ack;auto wire=ack.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",proof.receipts.back().sequence.value).finish();
  auto identity="family:"+std::to_string(job.context.incarnation.value);
  check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity.c_str(),wire.c_str(),&error) && !error,"Exact original terminal ACK");
 };
 const auto other=getJob(2);settle(1);
 auto retry=enroll(23);Json feedbackValue("{\"values\":"+retry.second+"}");
 if(mode=="feedback-expire") {
  check(admission==WARLOCK_IMPORTED_EXPIRED && retry.first=="[]","Return of capacity cannot renew expired intent");
  auto list=json_object_get_array_member(feedbackValue.object(),"values");auto expired=json_node_get_object(json_array_get_element(list,1));
  check(std::string_view(Json::text(expired,"outcome"))=="expired" && decimal(Json::text(expired,"deadline"))==deadline && decimal(Json::text(expired,"sequence"))>sequence,"Exact original cutoff and newer native sequence");
  check(endpoint.native([](auto& b){return b.recordCount()==1 && b.requestFloor(3)==0 && b.nextProofSequence()==2;}),"Expired feedback retains floor and other ownership");
 }else{
  check(admission==WARLOCK_IMPORTED_STARTED && retry.second=="[]","Admission replaces local wait with actual issued events");
  auto job=getJob(3);check(job.deadline==deadline && job.request.value==1 && job.context.incarnation.value==23,"Actual admission retains original cutoff and first request");settle(3);
 }
 check(getJob(2)==other,"Original other job identity and cutoff preserved");settle(2);
 check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"Normal exact C ownership cleanup");
 warlock_preview_bootstrap_free(bootstrap);server.finish();
 std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"mode\":\""<<mode<<"\",\"waiting\":"<<waiting.second<<",\"retryEvents\":"<<retry.first<<",\"retryFeedback\":"<<retry.second<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}"<<std::endl;return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
'''
target=root/'native/local-feedback-test.cpp';assert not target.exists();target.write_text(old+body)
print(target)
