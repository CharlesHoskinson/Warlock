#include "capture-resource-fd-source-fixture.hpp"
#include <cstdlib>
#include <new>
namespace preview::bridge {thread_local int mappedResourceAllocationFault=-1;bool mappedResourceFaultEnabled=false;}
[[gnu::noinline]] void* operator new(std::size_t size){auto& fault=preview::bridge::mappedResourceAllocationFault;if(fault>0 && --fault==0){fault=-1;throw std::bad_alloc();}if(auto p=std::malloc(size?size:1))return p;throw std::bad_alloc();}
[[gnu::noinline]] void operator delete(void* p)noexcept{std::free(p);}
[[gnu::noinline]] void operator delete(void* p,std::size_t)noexcept{std::free(p);}
using namespace preview;
static std::string take(char*& text){require(text,"Actual mapped C output");std::string result(text);g_free(text);text=nullptr;return result;}
static uint64_t count(const fs::path& path){uint64_t value=0;std::ifstream(path)>>value;return value;}
static int importedFD(){int result=-1;for(const auto& path:fs::directory_iterator("/proc/self/fd")) {
 std::error_code error;const auto name=fs::read_symlink(path.path(),error).string();
 if(!error && name.find("memfd:elm-preview-image")!=std::string::npos){require(result<0,"One actual imported sealed descriptor");result=std::stoi(path.path().filename().string());}
}return result;}
int main(int argc,char** argv){try{
 const bool fault=argc>1 && std::string_view(argv[1])=="post-transfer";
 const std::string mode=argc>2?argv[2]:"actual-fd";
 Server server(mode);GError* error=nullptr;auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);
 check(bootstrap && !error,"Actual mapped C bootstrap");auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);
 auto& native=*static_cast<Native*>(transport);const auto binding=native.binding();auto popup=reinterpret_cast<gpointer>(uintptr_t(77));
 char* text=nullptr;char* grantText=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open_controlled(transport,popup,21,1,1,&text,&grantText,&raw,&error);
 check(owner && text && grantText && raw && !error,"Actual controlled mapped owner");take(text);Json grant(take(grantText));const auto epoch=grant.counter("receiverEpoch");
 auto& endpoint=*static_cast<uri::Endpoint*>(raw);
 check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Original actual mapped receipt endpoint");
 auto delivery=warlock_preview_bootstrap_delivery(bootstrap,popup,&error);check(delivery && !error,"Original mapped receipt capability");
 struct Ticket{uint64_t ordinal;std::string wire;};
 auto propose=[&](const std::string& identity,const std::string& command){
  check(warlock_imported_clients_propose_control_at_epoch(owner,delivery,popup,epoch,identity.c_str(),command.c_str(),&text,&error) && !error,"Actual native mapped purpose proposal");
  Json value(take(text));return Ticket{value.counter("controlOrdinal"),Json::text(value.object(),"wire")};
 };
 auto dispatch=[&](const Ticket& ticket,bool expected=true){
  char* receipt=nullptr;auto result=warlock_imported_clients_dispatch_control(owner,delivery,popup,ticket.wire.c_str(),&text,&receipt,&error);
  check(bool(result)==expected && (expected?!error:bool(error)) && text && receipt,"Actual mapped handler return and independent receipt");
  g_clear_error(&error);take(text);Json received(take(receipt));check(received.counter("controlOrdinal")==ticket.ordinal,"Original mapped delivered prefix");
 };
 auto confirm=[&](uint64_t ordinal){
  auto wire=Wire().integer("previewProtocol",3).text("kind","preview-control-confirmed").begin("binding").binding(binding).end().counter("receiverEpoch",epoch).counter("controlOrdinal",ordinal).finish();
  check(warlock_imported_clients_confirm_control(owner,popup,wire.c_str(),&text,&error) && !error,"Original mapped control confirmation");take(text);
 };
 auto poll=[&](bool expected=true){const auto ok=warlock_imported_clients_retirement_poll(owner,delivery,popup,&text,&error);check(bool(ok)==expected && (expected?!error:bool(error)),"Actual original mapped resource polling outcome");if(expected)take(text);else {check(!text,"Lost scoped producer response publishes no fabricated completion");g_clear_error(&error);}};
 const auto job=endpoint.native([](auto& broker){return broker.inspect().front().job;});
 const auto acquire=Wire().text("kind","acquire").begin("job").job(job).end().finish();auto ticket=propose("family:21",acquire);
 check(importedFD()<0,"No imported descriptor before original capture");mappedResourceFaultEnabled=fault;dispatch(ticket,!fault);mappedResourceFaultEnabled=false;confirm(ticket.ordinal);
 const int descriptor=importedFD();check(descriptor>=0 && fcntl(descriptor,F_GETFD)>=0 && count(server.root/"fd-count")==1 && count(server.root/"capture-count")==1,"Actual original SCM_RIGHTS capture descriptor adopted once");
 const auto record=endpoint.native([](auto& broker){return broker.inspect().front();});
 check(record.allocated && record.packet && !record.terminal && record.bytes==4096 && record.producerDone==!fault,"Actual mapping custody survives post-transfer result allocation exception");
 GInputStream* reader=nullptr;gsize length=0;
 if(!fault) {
  check(warlock_imported_clients_uri(owner,"family:21",&text,&error) && !error,"Original adopted URI projection");const auto uri=take(text);
  reader=endpoint.open(77,uri,&length,&error);check(reader && !error && length==16 && endpoint.readers()==1,"Actual GIO reader owns original imported mapping");
  std::array<uint8_t,8> bytes{};check(g_input_stream_read(reader,bytes.data(),bytes.size(),nullptr,&error)==8 && !error && bytes[0]==137 && bytes[1]==80,"Actual sealed imported bytes readable before quarantine");
 }
 const auto reconcile=Wire().text("kind","reconcile").begin("binding").binding(binding).end().finish();auto original=propose("family:21",reconcile);dispatch(original);
 check(warlock_imported_clients_detachment_inventory(owner,popup,"family:21",&text,&error) && !error,"Actual scoped capture detachment inventory");Json seed(take(text));
 const auto ready=Wire().text("kind","detach-ready").begin("binding").binding(binding).end().counter("receiverEpoch",epoch).counter("subject",21).text("entry",Json::text(seed.object(),"entry")).text("entryIssuedThrough",Json::text(seed.object(),"entryIssuedThrough")).text("requestFloor",Json::text(seed.object(),"requestFloor")).finish();
 auto readiness=propose("family:21",ready);dispatch(readiness);confirm(readiness.ordinal);
 auto pending=[&]{check(warlock_imported_clients_detachment_pending(owner,delivery,popup,&text,&error) && !error,"Actual scoped capture completion query");return take(text);};
 auto assertPending=[&]{check(pending()=="[]" && endpoint.native([](auto& broker){return broker.actorCount()==1;}) && !warlock_imported_clients_empty(owner),"Retained scoped readiness cannot bypass original physical or final job ACK barriers");};
 assertPending();

 if(reader) {
  char byte{};check(g_input_stream_read(reader,&byte,1,nullptr,&error)==-1 && error && g_error_matches(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED),"Binding quarantine revokes actual existing reader before first cleanup poll");g_clear_error(&error);
  check(fcntl(descriptor,F_GETFD)>=0 && endpoint.readers()==1,"Read revocation alone cannot close original physical mapping");
 }
 std::ofstream(server.root/"locked")<<1;poll();assertPending();
 check(count(server.root/"producer-count")==1 && count(server.root/"export-count")==0 && fcntl(descriptor,F_GETFD)>=0 && endpoint.native([](auto& broker){return !broker.inspect().front().terminal && broker.charge()==4096;}),"Original locked producer and imported FD retain independent obligations");
 fs::remove(server.root/"locked");poll(mode!="resource-lost-retire");assertPending();
 if(mode=="resource-lost-retire"){poll();assertPending();}
 if(reader) {
  check(count(server.root/"producer-count")==0 && count(server.root/"export-count")==0 && fcntl(descriptor,F_GETFD)>=0 && endpoint.native([](auto& broker){return broker.charge()==4096 && !broker.inspect().front().terminal;}),"Native backend zero cannot close mapping or clear charge while actual reader owns it");
  check(g_input_stream_close(reader,nullptr,&error) && !error,"Actual original GIO reader close");g_object_unref(reader);reader=nullptr;
  check(endpoint.readers()==0 && fcntl(descriptor,F_GETFD)>=0 && endpoint.native([](auto& broker){return broker.charge()==4096;}),"Reader close alone cannot fabricate original terminal proof");poll();
 }
 check(fcntl(descriptor,F_GETFD)==-1 && errno==EBADF && importedFD()<0,"Actual original imported mapping descriptor closes after backend and reader barriers");
 const auto terminal=endpoint.native([](auto& broker){return broker.inspect().front();});
 check(terminal.terminal && terminal.proofs.size()==2 && terminal.proofs.front().kind==Receipt::Kind::Released && terminal.proofs.back().kind==Receipt::Kind::Cancelled && !terminal.bytes,
     "Adopted capture gets actual Released and Cancelled proofs instead of fabricated producer refusal");
 assertPending();confirm(original.ordinal);
 const auto ack=Wire().text("kind","acknowledge").begin("job").job(job).end().counter("sequence",terminal.proofs.back().sequence.value).finish();auto acknowledged=propose("family:21",ack);dispatch(acknowledged);confirm(acknowledged.ordinal);
 check(!warlock_imported_clients_empty(owner),"Actual physical and proof drain cannot fabricate live-window retirement");

 poll();const auto retained=pending();Json final("{\"rows\":"+retained+"}");auto rows=json_object_get_array_member(final.object(),"rows");check(rows && json_array_get_length(rows)==1,"Distinct scoped capture completion retained after final job ACK");auto fact=json_array_get_object_element(rows,0);
 check(std::string_view(Json::text(fact,"kind"))=="native-preview-binding-detach-delivery" && decimal(Json::text(fact,"receiverEpoch"))==epoch,"Scoped completion uses distinct typed epoch domain");
 check(pending()==retained,"Dropped scoped completion delivery retains exact original bytes");
 const auto finalAck=Wire().text("kind","detach-delivery-ack").begin("binding").binding(binding).end().counter("receiverEpoch",epoch).text("deliveryOrdinal",Json::text(fact,"deliveryOrdinal")).finish();auto done=propose("family:21",finalAck);dispatch(done);check(!warlock_imported_clients_empty(owner),"Final mapped actor processing still requires original control confirmation");confirm(done.ordinal);
 check(count(server.root/"capture-count")==1 && count(server.root/"fd-count")==1 && warlock_imported_clients_empty(owner) && warlock_imported_clients_close_bootstrap(owner,bootstrap,&error) && !error,"Original mapped binding closes without capture or FD transfer replay");
 RetirementCursor cursor;check(observeIncarnationRetirement(native,{21},cursor).state==IncarnationState::Active && !fs::exists(server.root/"retired-through") && native.binding()==binding,"Actual scoped resource detachment preserves Active native application and original grant");
 warlock_preview_bootstrap_free(bootstrap);server.finish();
 std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"postTransferAllocationFault\":"<<(fault?"true":"false")<<",\"actualImportedFDClosed\":true,\"actualReaderDrained\":"<<(!fault?"true":"false")<<",\"normalOwnedExit\":true,\"nativeAcceptance\":false}\n";return 0;
}catch(const std::exception& error){mappedResourceAllocationFault=-1;std::cerr<<error.what()<<'\n';return 1;}}
