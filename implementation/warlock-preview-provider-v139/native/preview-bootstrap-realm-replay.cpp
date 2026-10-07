#define main original_realm_fixture_main
#include "preview-realm-c-test.cpp"
#undef main
#include "preview_bootstrap_lifetime.hpp"

int main(){try{
 Server server;Server foreign;GError* error=nullptr;auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);
 check(bootstrap && !error,"Realm replay authenticated bootstrap");auto foreignBootstrap=warlock_preview_bootstrap_open(foreign.config().c_str(),&error);check(foreignBootstrap && !error,"Realm replay foreign Bootstrap");auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);
 auto& native=*static_cast<Native*>(transport);const auto binding=native.binding();auto popup=reinterpret_cast<gpointer>(uintptr_t(77));
 WarlockImportedClients* owner=nullptr;uri::Endpoint* endpoint=nullptr;ReceiptDelivery* delivery=nullptr;
 char* text=nullptr;char* grantText=nullptr;void* raw=nullptr;uint64_t epoch=0,subject=19,processed=0;int closed=0;
 std::string currentTicket,oldTicket;const auto reconcile=Wire().text("kind","reconcile").begin("binding").binding(binding).end().finish();
 auto open=[&](uint64_t target){return warlock_imported_clients_open_controlled(transport,popup,target,1,1,&text,&grantText,&raw,&error);};
 auto refusedOpen=[&](uint64_t target){auto rejected=open(target);check(!rejected && error && !text && !grantText && !raw,"Realm replay refused factory has no published capability");g_clear_error(&error);};
 auto confirm=[&](uint64_t ordinal){const auto wire=Wire().integer("previewProtocol",3).text("kind","preview-control-confirmed").begin("binding").binding(binding).end().counter("receiverEpoch",epoch).counter("controlOrdinal",ordinal).finish();check(warlock_imported_clients_confirm_control(owner,popup,wire.c_str(),&text,&error) && !error,"Realm replay original confirmation");take(text);};
 auto control=[&](const std::string& command,bool confirmed=true){
  check(warlock_imported_clients_propose_control(owner,delivery,popup,("family:"+std::to_string(subject)).c_str(),command.c_str(),&text,&error) && !error,"Realm replay original proposal");Json p(take(text));const auto ordinal=p.counter("controlOrdinal");const auto wire=std::string(Json::text(p.object(),"wire"));char* receipt=nullptr;
  check(warlock_imported_clients_dispatch_control(owner,delivery,popup,wire.c_str(),&text,&receipt,&error) && !error && text && receipt,"Realm replay original dispatch");take(text);take(receipt);if(confirmed)confirm(ordinal);if(command==reconcile)currentTicket=wire;return ordinal;
 };
 auto poll=[&]{check(warlock_imported_clients_retirement_poll(owner,delivery,popup,&text,&error) && !error,"Realm replay actual poll");take(text);};
 auto retire=[&]{std::ofstream(server.root/"retired-through")<<subject;
  check(warlock_imported_clients_retirement_observe(owner,popup,("family:"+std::to_string(subject)).c_str(),&text,&error) && !error,"Realm replay original incarnation observation");Json facts("{\"rows\":"+take(text)+"}");auto fact=row(facts);
  control(Wire().text("kind","retire-ready").begin("binding").binding(binding).end().counter("subject",subject).text("observationRequest",Json::text(fact,"request")).text("observationSequence",Json::text(fact,"sequence")).finish());poll();
 };
 auto ackJob=[&]{const auto record=endpoint->native([](auto& b){return b.inspect().front();});control(Wire().text("kind","acknowledge").begin("job").job(record.job).end().counter("sequence",record.proofs.back().sequence.value).finish());};
 auto ackActor=[&]{check(warlock_imported_clients_retirement_pending(owner,delivery,popup,&text,&error) && !error,"Realm replay final actor journal");Json final("{\"rows\":"+take(text)+"}");auto fact=row(final);processed=control(Wire().text("kind","retire-delivery-ack").begin("binding").binding(binding).end().text("deliveryOrdinal",Json::text(fact,"deliveryOrdinal")).finish(),false);};
 // Used only for owned fixture teardown, never to infer an expected trace state.
 int phase=0,last=0;std::string event;
 while(std::getline(std::cin,event)){
  last=1;
  if(event=="Open"){
   subject+=2;if(subject==22)subject+=2;owner=open(subject);check(owner && !error && raw && grantText && text,"Realm replay actual new owner");take(text);Json grant(take(grantText));epoch=grant.counter("receiverEpoch");endpoint=static_cast<uri::Endpoint*>(raw);check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Realm replay own Bootstrap attachment");delivery=static_cast<ReceiptDelivery*>(warlock_preview_bootstrap_delivery(bootstrap,popup,&error));check(delivery && !error,"Realm replay original Bootstrap capability");phase=1;
  }else if(event=="FailedOpen"){refusedOpen(subject);last=-1;}
  else if(event=="ConcurrentOpen"){refusedOpen(subject+2);last=-1;}
  else if(event=="Legacy"){try{Native::LegacyPreviewClaim legacy(native);}catch(const std::exception&){last=-1;}}
  else if(event=="Reconcile"){control(reconcile);phase=2;}
  else if(event=="Poll"){poll();phase=3;}
  else if(event=="AckJob"){ackJob();phase=4;}
  else if(event=="RetireActor"){retire();phase=5;}
  else if(event=="AckActor"){ackActor();phase=6;}
  else if(event=="ConfirmActor"){confirm(processed);phase=7;}
  else if(event=="OldTicket"){
   char* receipt=nullptr;check(!oldTicket.empty() && !warlock_imported_clients_dispatch_control(owner,delivery,popup,oldTicket.c_str(),&text,&receipt,&error) && error && !text && !receipt,"Realm replay old exact ticket rejects before handler");g_clear_error(&error);last=-1;
  }else if(event=="ForeignClose"){check(!warlock_imported_clients_close_bootstrap(owner,foreignBootstrap,&error) && error,"Realm replay foreign Bootstrap refuses");g_clear_error(&error);last=-1;
  }else if(event=="Close"){
   if(warlock_imported_clients_close_bootstrap(owner,bootstrap,&error)){check(!error,"Realm replay normal close");oldTicket=currentTicket;owner=nullptr;endpoint=nullptr;delivery=nullptr;phase=0;++closed;}
   else {check(error,"Realm replay refused close category");g_clear_error(&error);last=-1;}
  }else throw std::runtime_error("Closed realm replay event domain");
  check(native.binding()==binding,"Realm replay stable shared Native binding");
  size_t records=0,actors=0,proofs=0;bool terminal=false;
  if(endpoint){check(endpoint->registeredView(77)->epoch==epoch,"Realm replay Native epoch equals actual receiver grant");endpoint->native([&](auto& b){records=b.recordCount();actors=b.actorCount();const auto rows=b.inspect();if(!rows.empty()){terminal=rows.front().terminal;proofs=rows.front().proofs.size();}});}
  std::cout<<Wire().text("epoch",std::to_string(epoch)).integer("closed",closed).boolean("active",native.previewControlClaimed()).boolean("attached",bootstrapHasImportedDelivery(bootstrap)).integer("records",records).integer("actors",actors).boolean("terminal",terminal).integer("proofs",proofs).boolean("ready",owner && warlock_imported_clients_empty(owner)).integer("last",last).finish()<<'\n';
 }
 if(owner){if(phase==1){control(reconcile);phase=2;}if(phase==2){poll();phase=3;}if(phase==3){ackJob();phase=4;}if(phase==4){retire();phase=5;}if(phase==5){ackActor();phase=6;}if(phase==6)confirm(processed);check(warlock_imported_clients_close_bootstrap(owner,bootstrap,&error) && !error,"Realm replay original teardown close");delivery=nullptr;}
 check(!native.previewControlClaimed(),"Realm replay complete owned cleanup");warlock_preview_bootstrap_free(bootstrap);warlock_preview_bootstrap_free(foreignBootstrap);server.finish();foreign.finish();return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
