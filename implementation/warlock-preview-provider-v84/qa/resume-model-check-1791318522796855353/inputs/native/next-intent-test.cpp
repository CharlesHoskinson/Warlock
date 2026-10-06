// Reuse the actual socket/peer/bootstrap fixture without changing its evidence.
#define main legacy_feedback_main
#include "local-feedback-test.cpp"
#undef main
int main(){try{
 Server server("feedback-expire");GError* error=nullptr;
 auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);
 check(bootstrap && !error,"Actual trusted native bootstrap");
 auto native=warlock_preview_bootstrap_native_transport(bootstrap,&error);
 gpointer popup=reinterpret_cast<gpointer>(uintptr_t(77));
 char* events=nullptr;char* feedback=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open_dynamic(native,popup,21,1,1,&events,&raw,&error);
 check(owner && events && raw && !error,"Original dynamic owner");g_free(events);events=nullptr;
 check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error),"Original receipt delivery");
 auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);WarlockImportedAdmission admission;
 auto enroll=[&](uint64_t subject,uint64_t publication,uint64_t lease,bool next){
  check((next?warlock_imported_clients_enroll_next_feedback:warlock_imported_clients_enroll_feedback)(owner,popup,subject,publication,lease,&admission,&events,&feedback,&error) && !error,"Actual explicit C enrollment");
  std::pair<std::string,std::string> result{events,feedback};g_free(events);g_free(feedback);events=feedback=nullptr;
  check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error),"Same delivery membership");return result;
 };
 auto getJob=[&](uint64_t entry){return endpoint.native([&](auto& b){for(const auto& row:b.inspect())if(row.entry==entry)return row.job;throw std::runtime_error("Actual retained job");});};
 auto cutoff=[](const std::string& wire){Json value("{\"values\":"+wire+"}");auto list=json_object_get_array_member(value.object(),"values");require(json_array_get_length(list)==2,"Idle source and feedback pair");return decimal(Json::text(json_node_get_object(json_array_get_element(list,1)),"deadline"));};
 enroll(22,1,1,false);check(admission==WARLOCK_IMPORTED_STARTED,"Second actual job");
 const auto first=getJob(1),second=getJob(2);
 auto waiting=enroll(23,1,1,false);check(admission==WARLOCK_IMPORTED_CAPACITY && waiting.first=="[]","Unissued capacity");const auto original=cutoff(waiting.second);
 auto expired=enroll(23,1,1,true);check(admission==WARLOCK_IMPORTED_EXPIRED && expired.first=="[]" && cutoff(expired.second)==original,"Same stamp expiry cannot renew");
 auto partialPublication=enroll(23,2,1,true);check(admission==WARLOCK_IMPORTED_CONFLICT && partialPublication.first=="[]" && cutoff(partialPublication.second)==original,"Publication alone cannot renew");
 auto partialLease=enroll(23,1,2,true);check(admission==WARLOCK_IMPORTED_CONFLICT && partialLease.first=="[]" && cutoff(partialLease.second)==original,"Lease alone cannot renew");
 auto successor=enroll(23,3,2,true);check(admission==WARLOCK_IMPORTED_CAPACITY && successor.first=="[]","Explicit successor waits without fake job");const auto later=cutoff(successor.second);
 check(later>original,"Successor cutoff derives from later native observation");
 check(endpoint.native([](auto& b){return b.recordCount()==2 && b.charge()==8192 && b.requestFloor(3)==0 && b.nextProofSequence()==1;}),"Succession consumes no item, request floor or proof");
 auto replay=enroll(23,1,1,true);check(admission==WARLOCK_IMPORTED_CONFLICT && replay.first=="[]" && cutoff(replay.second)==later,"Expired predecessor cannot become current");
 auto retry=enroll(23,3,2,true);check(admission==WARLOCK_IMPORTED_CAPACITY && cutoff(retry.second)==later,"Successor polling preserves new original cutoff");
 check(getJob(1)==first && getJob(2)==second,"Both original job identities unchanged");
 auto settle=[&](uint64_t entry){auto job=getJob(entry);auto proof=endpoint.native([&](auto& b){return b.producerRefused(entry,job);});char* pending=nullptr;
  check(warlock_preview_bootstrap_pending(bootstrap,popup,&pending,&error) && pending && !error,"Actual pending terminal discovery");g_free(pending);
  Wire ack;auto wire=ack.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",proof.receipts.back().sequence.value).finish();auto identity="family:"+std::to_string(job.context.incarnation.value);
  check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity.c_str(),wire.c_str(),&error) && !error,"Exact original terminal ACK");
 };
 settle(1);auto issued=enroll(23,3,2,true);check(admission==WARLOCK_IMPORTED_STARTED && issued.second=="[]","Actual capacity admission replaces waiting");
 const auto third=getJob(3);check(third.request.value==1 && third.deadline==later && third.context.incarnation.value==23,"First actual job retains successor cutoff");
 auto retained=enroll(23,3,3,true);check(admission==WARLOCK_IMPORTED_RETAINED && retained.first=="[]" && retained.second=="[]" && getJob(3)==third,"Issued job cannot be superseded");
 check(getJob(2)==second,"Unrelated original job retained");settle(3);settle(2);
 check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"Normal original ownership cleanup");
 warlock_preview_bootstrap_free(bootstrap);server.finish();
 std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"waiting\":"<<waiting.second<<",\"expired\":"<<expired.second<<",\"successor\":"<<successor.second<<",\"issued\":"<<issued.first<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}"<<std::endl;return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
