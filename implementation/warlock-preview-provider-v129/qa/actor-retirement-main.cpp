int main(int argc,char** argv){try{
 const std::string mode=argc>1?argv[1]:"turnover";Server server("turnover");GError* error=nullptr;
 auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);check(bootstrap && !error,"Actual owning C bootstrap");
 auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);check(transport && !error,"Actual own Native transport");
 auto& native=*static_cast<Native*>(transport);auto popup=reinterpret_cast<gpointer>(uintptr_t(77));char* events=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open_dynamic(transport,popup,21,1,1,&events,&raw,&error);
 check(owner && events && raw && !error,"Actual dynamic C owner");g_free(events);
 auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);
 check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Actual original receipt enrollment");
 auto journal=warlock_preview_bootstrap_delivery(bootstrap,popup,&error);check(journal && !error,"Own journal capability");
 auto enroll=[&](uint64_t subject) {
  WarlockImportedAdmission admission=WARLOCK_IMPORTED_INVALID;char* json=nullptr;
  bool result=warlock_imported_clients_enroll(owner,popup,subject,1,1,&admission,&json,&error);
  check(result && json && !error && admission==WARLOCK_IMPORTED_STARTED,"Actual new C subject reserves original native job");g_free(json);
  check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error) && !error,"Same journal and receiver grows");
 };
 enroll(22);
 const auto epoch=endpoint.registeredView(uintptr_t(popup))->epoch;
 auto rows=endpoint.native([](auto& broker){return broker.inspect();});check(rows.size()==2,"Two actual original jobs");
 auto neighbor=rows[1].job;
 const auto originalScope=endpoint.native([](auto& broker){return broker.nativeScope(1);});
 auto inventory=[&] {
  char* json=nullptr;check(warlock_imported_clients_actor_counts(owner,journal,&json,&error) && json && !error,"Validated native inventory");
  auto result=std::string(json);g_free(json);return result;
 };
 auto settledInventory=[&](uint64_t count,uint64_t issued) {
  Json facts(inventory());
  for(auto key:{"subjects","frames","intents","slots","actors","receiverEntries","deliverySubjects"})
   check(Json::integer(facts.object(),key)==int64_t(count),"All native actor owners have equal retained membership");
  check(Json::integer(facts.object(),"predecessors")==0,"No predecessor history leaked");
  check(facts.counter("entryIssuedThrough")==issued && facts.counter("nativeEntryIssuedThrough")==issued &&
   facts.counter("brokerEntryIssuedThrough")==issued,"Nonreused frontiers survive retirement");
 };
 auto retiredThrough=[&](uint64_t subject) {std::ofstream(server.root/"retired-through")<<subject;};
 auto retire=[&](uint64_t subject,bool expected) {
  const auto identity="family:"+std::to_string(subject);gboolean retired=FALSE;char* json=nullptr;
  check(warlock_imported_clients_retire_native(owner,journal,popup,identity.c_str(),&retired,&json,&error) && json && !error,"Actual aggregate C retirement executes");
  check(bool(retired)==expected,"Physical journal guards determine actual retirement");
  if(expected) {Json fact(json);check(std::string_view(Json::text(fact.object(),"kind"))=="native-actor-retired" &&
   fact.counter("subject")==subject && decodeBinding(Json::child(fact.object(),"binding"))==native.binding(),"Exact native transaction fact");}
  else check(std::string_view(json)=="null","Unsettled actor yields no fabricated retirement fact");
  g_free(json);
 };
 auto terminal=[&](uint64_t entry) {
  return endpoint.native([&](auto& broker) {
   auto job=broker.inspect();auto row=std::find_if(job.begin(),job.end(),[&](const auto& item){return item.entry==entry;});
   require(row!=job.end(),"Actual known reservation");
   auto result=broker.producerRefused(entry,row->job);
   check(result.status==preview::Result::Status::Complete && !result.receipts.empty(),"Actual untouched producer closes reservation with retained receipt");
   return result.receipts.back();
  });
 };
 auto ack=[&](const preview::Receipt& receipt) {
  const auto identity="family:"+std::to_string(receipt.job.context.incarnation.value);
  const auto command=Wire().text("kind","acknowledge").begin("job").job(receipt.job).end().counter("sequence",receipt.sequence.value).finish();
  check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity.c_str(),command.c_str(),&error) && !error,"Exact final journal ACK removes only its original record");
 };
 settledInventory(2,2);const auto before=inventory();retire(21,false);check(inventory()==before,"Active observation changes no actor membership");
 retiredThrough(21);retire(21,false);
 check(endpoint.native([](auto& broker){return broker.recordCount()==2 && broker.activeItems()==2 && broker.charge()==8192;}),"Native Retired does not erase physical obligations");
 auto receipt=terminal(1);retire(21,false);
 check(endpoint.native([](auto& broker){return broker.recordCount()==2 && broker.activeItems()==1 && broker.charge()==4096;}),"Unacknowledged terminal remains after retirement refusal");
 ack(receipt);
 // A second registered native receiver must retain its membership until closed.
 check(endpoint.registerView(78,native.binding(),{1,2}),"Second real native view");
 retire(21,false);check(inventory()==before,"Foreign receiver ownership prevents partial removal");endpoint.unregisterView(78);
 const auto nextBeforeForeign=native.next();
 auto foreignPopup=reinterpret_cast<gpointer>(uintptr_t(78));
 check(!warlock_preview_bootstrap_delivery(bootstrap,foreignPopup,&error) && error,"Wrong popup cannot borrow journal");g_clear_error(&error);
 preview::uri::Endpoint foreign({256,8,2,4096},4,2);
 foreign.native([&](auto& broker){check(broker.enroll(1,originalScope,4096),"Synthetic foreign endpoint has independent scope");});
 check(foreign.registerView(77,native.binding(),{1}),"Foreign endpoint receiver");ReceiptDelivery wrong(foreign,native.binding(),77);
 gboolean removed=FALSE;char* fact=nullptr;
 check(!warlock_imported_clients_retire_native(owner,&wrong,popup,"family:21",&removed,&fact,&error) && !removed && !fact && error,"Wrong endpoint journal rejected before native query");g_clear_error(&error);
 check(native.next()==nextBeforeForeign,"Foreign capability attempts never query native");
 retire(21,true);settledInventory(1,2);
 check(endpoint.native([&](auto& broker){auto retained=broker.inspect();return retained.size()==1 && retained[0].job==neighbor && broker.requestFloor(2)==1 && broker.charge()==4096;}),"Live neighbor job/floor/charge untouched");
 check(!endpoint.native([&](auto& broker){return broker.enroll(1,originalScope,4096);}),"Old absent Broker serial can never be reenrolled");
 const auto afterRetirement=native.next();
 check(!warlock_imported_clients_retirement_state(owner,"family:21",&fact,&error) && !fact && error,"Old retired C identity refused");g_clear_error(&error);
 check(!warlock_imported_clients_command(owner,"family:21","{}",&fact,&error) && !fact && error,"Old command refused before native query");g_clear_error(&error);
 check(native.next()==afterRetirement,"Old controls cannot query native or resurrect actor");
 const auto afterBeforeClosed=inventory();WarlockImportedAdmission deniedAdmission=WARLOCK_IMPORTED_INVALID;
 check(!warlock_imported_clients_enroll(owner,popup,21,1,1,&deniedAdmission,&events,&error) && !events && error,"Closed native subject denied actual scope");g_clear_error(&error);
 check(inventory()==afterBeforeClosed,"Scope denial consumes no C membership, serial or capacity");
 const uint64_t last=mode=="turnover"?300:23;
 for(uint64_t subject=23;subject<=last;++subject) {
  enroll(subject);const uint64_t entry=subject-20;settledInventory(2,entry);
  retiredThrough(subject);auto proof=terminal(entry);retire(subject,false);ack(proof);retire(subject,true);settledInventory(1,entry);
  check(endpoint.native([&](auto& broker){auto retained=broker.inspect();return retained.size()==1 && retained[0].job==neighbor && broker.requestFloor(2)==1;}),"Turnover retains exact original neighbor and floor");
  check(endpoint.registeredView(uintptr_t(popup))->epoch==epoch,"Turnover never replaces original receiver epoch");
 }
 ack(terminal(2));retiredThrough(last);
 check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"Actual original C drain and close");warlock_preview_bootstrap_free(bootstrap);server.finish();
 std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"mode\":\""<<mode<<"\",\"sequentialSubjects\":"<<last-20<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 2;}}
