#include "client_frame.hpp"
#include "preview_delivery.hpp"
#include "preview-provider-bootstrap.h"
#include <fstream>
#include <iostream>
using namespace preview;using namespace preview::bridge;
int main(int argc,char** argv){try{
 require(argc==4,"Own config/native subject/private PNG destination");unsigned checks=0;
 auto check=[&](bool ok,const char* reason){require(ok,reason);++checks;};GError* error=nullptr;
 auto owner=warlock_preview_bootstrap_open(argv[1],&error);check(owner && !error,"Own native bootstrap");
 auto native=static_cast<Native*>(warlock_preview_bootstrap_native_transport(owner,&error));check(native && !error,"Borrowed same native grant");
 const auto subject=decimal(argv[2]);char* scopeWire=nullptr;
 check(warlock_preview_bootstrap_client_scope(owner,subject,&scopeWire,&error) && !error,"Actual C client scope");
 const std::string scopeJSON(scopeWire);g_free(scopeWire);auto observed=native->clientScope({subject});
 check(observed.kind==SourceObservation::Kind::UnqualifiedClientMain && !observed.previewEligible && observed.scope.binding==native->binding(),"Exact own client source");
 const auto deadline=observed.scope.now+2000000000ULL;const auto cost=observed.maximumTransferBytes;
 fd::Header frame{};bool haveFrame=false;
 uri::Endpoint endpoint({1,4,1,cost},1,1,[&](uint64_t)->std::optional<uri::NativeTime>{return haveFrame?native->time(frame):std::nullopt;});
 check(endpoint.enableDemand({{1,4,1,cost},observed.scope.binding.lifetime,observed.scope.clock,1}),"One physical native demand/Broker");
 demand::NativeDemand input{1,1,observed.scope,{1},cost,true};check(endpoint.nativeDemand([&](auto& q){return q.observe(input).accepted;}),"Explicit native qualification scope");
 auto attempt=endpoint.nativeDemand([&](auto& q){return q.start(1,deadline);});check(attempt.status==demand::Attempt::Status::Started && attempt.job.has_value(),"Original-deadline admitted job");const auto job=*attempt.job;
 auto capture=captureClient(*native,observed,job.deadline);auto imported=native->query(fd::Get,capture.request,subject);
 check(imported && imported->rights.size()==1 && clientFrameMatches(imported->words,capture),"Exact native client FD envelope");const auto h=imported->words;frame=h;haveFrame=true;
 check(!fd::imageHeaderFor(h,fd::SourcePlane::Monitor),"Client never aliases monitor");const auto descriptor=imported->rights.front().get();
 auto mapping=std::make_unique<fd::Mapped>(std::move(imported->rights.front()),h,cost,fd::SourcePlane::ClientMain);auto physical=mapping.get();
 std::unique_ptr<const Buffer> payload=std::move(mapping);auto offered=endpoint.native([&](auto& b){return b.allocate(1,job,payload,h[fd::Expires]);});
 check(offered.receipts.size()==1 && offered.receipts.front().packet.has_value() && !payload,"Actual Broker adopts physical client payload");const auto packet=*offered.receipts.front().packet;
 auto signaled=endpoint.native([&](auto& b){return b.producerComplete(1,job);});check(signaled.receipts.size()==1,"Completed immutable native capture signals readiness");
 constexpr uint64_t receiver=77;check(endpoint.registerView(receiver,job.binding,{1}),"Explicit private native receiver");
 check(warlock_preview_bootstrap_attach_delivery(owner,&endpoint,reinterpret_cast<gpointer>(receiver),&error) && !error,"Same bootstrap retains actual Broker journal");
 gsize length=0;auto stream=endpoint.open(receiver,uri::encode(packet.token),&length,&error);check(stream && !error && length==capture.bytes && endpoint.readers()==1,"Actual GIO client stream");
 std::vector<uint8_t> png(length);gsize read=0;check(g_input_stream_read_all(stream,png.data(),png.size(),&read,nullptr,&error) && !error && read==png.size(),"Read complete immutable client PNG");
 std::ofstream image(argv[3],std::ios::binary);image.write(reinterpret_cast<const char*>(png.data()),png.size());image.close();check(bool(image),"Retained independent PNG artifact");
 endpoint.native([&](auto& b){return b.release(1,job.binding,job,packet.token);});
 check(!endpoint.native([&](auto& b){return b.consumerComplete(1,job);}) && endpoint.native([](auto& b){return b.charge();})==cost,"Held reader prevents physical retirement");
 uint8_t byte{};check(g_input_stream_read(stream,&byte,1,nullptr,&error)==-1 && error,"Revoked URI blocks retained reader");g_clear_error(&error);
 bool blocked=false;try{retireClient(*native);}catch(const std::exception&){blocked=true;}check(blocked,"Native producer refuses held export");
 check(g_input_stream_close(stream,nullptr,&error) && !error,"Physical URI reader closes");g_object_unref(stream);
 check(endpoint.readers()==0 && endpoint.native([&](auto& b){return b.consumerComplete(1,job);}),"Consumer references drained");
 check(physical->close() && physical->png().empty() && ::fcntl(descriptor,F_GETFD)<0 && errno==EBADF,"Physical mapping/FD closed before native export");
 check(endpoint.native([](auto& b){return b.charge();})==cost && warlock_preview_bootstrap_pending(owner,reinterpret_cast<gpointer>(receiver),&scopeWire,&error) && std::string_view(scopeWire)=="[]","Charge retained and no early cleanup proof");g_free(scopeWire);scopeWire=nullptr;
 check(releaseClient(*native,capture,h[fd::Transfer]),"Exact native export released");check(retireClient(*native),"Original native producer memory retired");
 auto retired=endpoint.native([&](auto& b){return b.destroy(1,job);});check(retired.receipts.size()==1 && endpoint.native([](auto& b){return b.charge();})==0,"Final physical Broker retirement");
 check(warlock_preview_bootstrap_pending(owner,reinterpret_cast<gpointer>(receiver),&scopeWire,&error) && !error && std::string_view(scopeWire)!="[]" && endpoint.native([](auto& b){return b.recordCount();})==1,"Terminal delivery retained until exact ACK");
 const std::string receipts(scopeWire);g_free(scopeWire);scopeWire=nullptr;
 Wire ack;auto command=ack.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",retired.receipts.back().sequence.value).finish();
 check(warlock_preview_bootstrap_acknowledge(owner,reinterpret_cast<gpointer>(receiver),("family:"+std::to_string(subject)).c_str(),command.c_str(),&error) && !error && endpoint.native([](auto& b){return b.recordCount();})==0,"Exact retained final ACK");
 endpoint.unregisterView(receiver);warlock_preview_bootstrap_free(owner);
 std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"providerPID\":"<<getpid()<<",\"clientScope\":"<<scopeJSON<<",\"terminalReceipts\":"<<receipts<<",\"previewEligible\":false}\n";return 0;
}catch(const std::exception& e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
