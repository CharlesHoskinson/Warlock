#define main retained_fd_fixture_main
#include "capture-resource-fd-test.cpp"
#undef main

int main(){try{
 Server server("actual-fd");GError* error=nullptr;auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);
 check(bootstrap && !error,"Replay actual bootstrap");auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);
 auto& native=*static_cast<Native*>(transport);const auto binding=native.binding();auto popup=reinterpret_cast<gpointer>(uintptr_t(77));
 char* text=nullptr;char* grantText=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open_controlled(transport,popup,21,1,1,&text,&grantText,&raw,&error);
 check(owner && text && grantText && raw && !error,"Replay actual controlled owner");take(text);Json grant(take(grantText));const auto epoch=grant.counter("receiverEpoch");
 auto& endpoint=*static_cast<uri::Endpoint*>(raw);check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Replay own receipt endpoint");
 auto delivery=warlock_preview_bootstrap_delivery(bootstrap,popup,&error);check(delivery && !error,"Replay own receipt capability");
 auto control=[&](const std::string& command){
  check(warlock_imported_clients_propose_control(owner,delivery,popup,"family:21",command.c_str(),&text,&error) && !error,"Replay original native purpose");
  Json proposal(take(text));const auto ordinal=proposal.counter("controlOrdinal");const auto wire=std::string(Json::text(proposal.object(),"wire"));char* receipt=nullptr;
  check(warlock_imported_clients_dispatch_control(owner,delivery,popup,wire.c_str(),&text,&receipt,&error) && !error && text && receipt,"Replay original native dispatch");take(text);take(receipt);
  auto confirmation=Wire().integer("previewProtocol",3).text("kind","preview-control-confirmed").begin("binding").binding(binding).end().counter("receiverEpoch",epoch).counter("controlOrdinal",ordinal).finish();
  check(warlock_imported_clients_confirm_control(owner,popup,confirmation.c_str(),&text,&error) && !error,"Replay native control confirmation");take(text);
 };
 auto poll=[&]{check(warlock_imported_clients_retirement_poll(owner,delivery,popup,&text,&error) && !error,"Replay actual retirement poll");take(text);};
 const auto job=endpoint.native([](auto& broker){return broker.inspect().front().job;});
 control(Wire().text("kind","acquire").begin("job").job(job).end().finish());const int descriptor=importedFD();check(descriptor>=0,"Replay actual adopted descriptor");
 check(warlock_imported_clients_uri(owner,"family:21",&text,&error) && !error,"Replay original opaque URI");const auto uri=take(text);
 const auto reconcile=Wire().text("kind","reconcile").begin("binding").binding(binding).end().finish();
 bool quarantined=false,locked=false;GInputStream* reader=nullptr;int offset=0,last=0;
 auto ack=[&]{auto records=endpoint.native([](auto& broker){return broker.inspect();});check(records.size()==1 && records.front().terminal,"Replay actual final terminal proof");
  control(Wire().text("kind","acknowledge").begin("job").job(job).end().counter("sequence",records.front().proofs.back().sequence.value).finish());};
 std::string event;
 while(std::getline(std::cin,event)) {
  last=0;
  if(event=="OpenReader") {
   check(!reader,"Replay at most one reader");gsize length=0;reader=endpoint.open(77,uri,&length,&error);
   if(reader){check(!error && length==16,"Replay original reader storage");offset=0;last=1;}else {check(error && g_error_matches(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED),"Replay denied reader category");g_clear_error(&error);last=-1;}
  }else if(event=="Read") {
   check(reader,"Replay actual reader before read");char byte{};last=g_input_stream_read(reader,&byte,1,nullptr,&error);
   if(last==-1){check(error && g_error_matches(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED),"Replay denied read category");g_clear_error(&error);}else {check(!error && (last==0 || last==1),"Replay actual byte/EOF");offset+=last;}
  }else if(event=="CloseReader") {if(reader){check(g_input_stream_close(reader,nullptr,&error) && !error,"Replay actual reader close");g_object_unref(reader);reader=nullptr;}}
  else if(event=="Reconcile"){control(reconcile);quarantined=true;}
  else if(event=="Poll")poll();
  else if(event=="Lock"){std::ofstream(server.root/"locked")<<1;locked=true;}
  else if(event=="Unlock"){fs::remove(server.root/"locked");locked=false;}
  else if(event=="Ack")ack();
  else if(event=="Close"){check(!warlock_imported_clients_close(owner,&error) && error,"Replay actual live actor blocks strict close");g_clear_error(&error);last=-1;}
  else throw std::runtime_error("Closed replay event domain");
  const auto records=endpoint.native([](auto& broker){return broker.inspect();});check(records.size()<=1,"Replay original single job");const bool known=!records.empty();
  const auto charge=endpoint.native([](auto& broker){return broker.charge();});const bool mapped=importedFD()>=0;
  if(mapped)check(fcntl(descriptor,F_GETFD)>=0,"Replay original physical descriptor remains owned");else check(fcntl(descriptor,F_GETFD)==-1 && errno==EBADF,"Replay original physical descriptor closed");
  check(endpoint.readers()==(reader?1:0),"Replay actual reader ledger");
  std::cout<<Wire().boolean("quarantined",quarantined).boolean("locked",locked).boolean("producer",count(server.root/"producer-count")!=0)
   .boolean("exported",count(server.root/"export-count")!=0).boolean("mapped",mapped).boolean("reader",reader).boolean("known",known)
   .boolean("terminal",known && records.front().terminal).integer("bytes",charge).integer("proofs",known?records.front().proofs.size():0)
   .integer("offset",offset).integer("captures",count(server.root/"capture-count")).integer("transfers",count(server.root/"fd-count")).integer("last",last).finish()<<'\n';
 }
 // Drain the owned fixture independently of the compared trace. These steps
 // never substitute for a requested event or an expected intermediate state.
 if(reader){check(g_input_stream_close(reader,nullptr,&error) && !error,"Replay teardown reader");g_object_unref(reader);reader=nullptr;}
 fs::remove(server.root/"locked");control(reconcile);poll();if(endpoint.native([](auto& broker){return broker.recordCount()!=0;}))ack();
 std::ofstream(server.root/"retired-through")<<21;
 check(warlock_imported_clients_retirement_observe(owner,popup,"family:21",&text,&error) && !error,"Replay actual incarnation observation");Json facts("{\"rows\":"+take(text)+"}");auto rows=json_object_get_array_member(facts.object(),"rows");check(rows && json_array_get_length(rows)==1,"Replay original incarnation fact");auto fact=json_array_get_object_element(rows,0);
 control(Wire().text("kind","retire-ready").begin("binding").binding(binding).end().counter("subject",21).text("observationRequest",Json::text(fact,"request")).text("observationSequence",Json::text(fact,"sequence")).finish());poll();
 check(warlock_imported_clients_retirement_pending(owner,delivery,popup,&text,&error) && !error,"Replay original final actor delivery");Json final("{\"rows\":"+take(text)+"}");rows=json_object_get_array_member(final.object(),"rows");check(rows && json_array_get_length(rows)==1,"Replay final actor proof");fact=json_array_get_object_element(rows,0);
 control(Wire().text("kind","retire-delivery-ack").begin("binding").binding(binding).end().text("deliveryOrdinal",Json::text(fact,"deliveryOrdinal")).finish());
 check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"Replay strict final closure");warlock_preview_bootstrap_free(bootstrap);server.finish();return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
