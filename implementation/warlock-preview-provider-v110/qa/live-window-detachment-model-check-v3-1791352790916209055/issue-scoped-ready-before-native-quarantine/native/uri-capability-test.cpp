#define main retained_provider_ownership_main
#include "provider-ownership-test.cpp"
#undef main
#include "preview-uri-router.h"
#include "preview_fd.hpp"
#include <thread>
struct ImageRealm {
 std::shared_ptr<uint64_t> now=std::make_shared<uint64_t>(1);
 std::unique_ptr<uri::Endpoint> endpoint;
 std::string image;int descriptor=-1;
 ImageRealm(uint64_t epoch,uint64_t frontend=3){
  const auto clock=now;endpoint=std::make_unique<uri::Endpoint>(Limits{2,8,2,64},2,1,[clock](uint64_t)->std::optional<uri::NativeTime>{return uri::NativeTime{{10},*clock};});
  check(endpoint->registerControlView(77,{{1},{2},{frontend}},epoch),"Actual fresh capability receiver epoch");
  check(endpoint->enableDemand({{2,8,2,64},{1},{10},2}),"Actual capability physical broker scheduling");auto d=observation();d.scope.binding.frontend={frontend};
  check(endpoint->nativeDemand([&](auto& q){return q.observe(d).accepted;}),"Actual capability original native scope");auto attempted=endpoint->nativeDemand([](auto& q){return q.start(1,20);});check(attempted.job.has_value(),"Actual capability original job reservation");const auto job=*attempted.job;
  const std::array<uint8_t,16> bytes{137,80,78,71,13,10,26,10,1,2,3,4,5,6,7,8};auto file=fd::seal(bytes);descriptor=file.get();fd::Header header{};header[fd::Magic]=fd::MAGIC;header[fd::Version]=1;for(size_t i=fd::Lifetime;i<fd::Count;++i)header[i]=1;
  header[fd::Bytes]=bytes.size();header[fd::Charge]=32;header[fd::Flags]=11;header[fd::Deadline]=20;header[fd::Expires]=50;
  std::unique_ptr<const Buffer> payload=std::make_unique<const fd::Mapped>(std::move(file),header,32,fd::SourcePlane::ClientMain);
  auto offer=endpoint->native([&](auto& broker){return broker.allocate(1,job,payload,50);});check(offer.receipts.size()==1,"Actual sealed mapping adoption");image=uri::encode(offer.receipts.front().packet->token);
  endpoint->native([&](auto& broker){return broker.producerComplete(1,job);});endpoint->nativeDemand([](auto& q){q.poll();});check(endpoint->extendView(77,job.binding,{1}),"Actual image receiver membership");
 }
};
int main(){try{
 GError* error=nullptr;gsize length=0;auto view=reinterpret_cast<gpointer>(uintptr_t(77));auto foreignView=reinterpret_cast<gpointer>(uintptr_t(78));
 auto refused=[&](GInputStream* reader){check(!reader && error && g_error_matches(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED) && length==0,"Stale native read capability refuses before reader allocation");g_clear_error(&error);};
 auto readDenied=[&](GInputStream* reader){char byte{};check(g_input_stream_read(reader,&byte,1,nullptr,&error)==-1 && error && g_error_matches(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED),"Original reader authority is revoked independently of retained physical storage");g_clear_error(&error);};
 auto close=[&](GInputStream* reader){check(g_input_stream_close(reader,nullptr,&error) && !error,"Actual capability reader close");g_object_unref(reader);};
 auto first=std::make_unique<ImageRealm>(1);const auto firstFD=first->descriptor;const auto oldURI=first->image;auto capability=first->endpoint->readCapability(77,1);auto router=preview_uri_router_new();check(router,"Native stable router allocation");
 check(preview_uri_router_bind(router,first->endpoint.get(),view,1,&error) && !error,"Exact native router enrollment");check(preview_uri_router_bind(router,first->endpoint.get(),view,1,&error) && !error,"Exact same realm bind is idempotent");
 auto callback=preview_uri_router_ref(router);check(callback==router,"Context has independent native router reference");
 refused(capability.open(78,oldURI,&length,&error));refused(preview_uri_router_open(callback,foreignView,oldURI.c_str(),&length,&error));
 auto reader=preview_uri_router_open(callback,view,oldURI.c_str(),&length,&error);check(reader && !error && length==16 && first->endpoint->readers()==1,"Actual stable callback opens original sealed image");char byte{};check(g_input_stream_read(reader,&byte,1,nullptr,&error)==1 && !error && uint8_t(byte)==137,"Actual original mapping read before owner retirement");
 std::thread other([&]{GError* e=nullptr;check(!preview_uri_router_clear(router,&e) && e,"Foreign thread cannot clear native URI router");g_clear_error(&e);check(!preview_uri_router_bind(router,first->endpoint.get(),view,1,&e) && e,"Foreign thread cannot bind native URI router");g_clear_error(&e);gsize size=0;check(!preview_uri_router_open(router,view,oldURI.c_str(),&size,&e) && e && !size,"Foreign thread cannot open native URI route");g_clear_error(&e);});other.join();
 check(first->endpoint->readers()==1 && fcntl(firstFD,F_GETFD)>=0,"Foreign router operations retain original reader and descriptor");
 first->endpoint.reset();check(fcntl(firstFD,F_GETFD)>=0,"Endpoint destruction cannot free mapping retained by original reader");refused(capability.open(77,oldURI,&length,&error));refused(preview_uri_router_open(callback,view,oldURI.c_str(),&length,&error));readDenied(reader);close(reader);check(fcntl(firstFD,F_GETFD)==-1 && errno==EBADF,"Weak callback capability does not retain physical mapping after last reader close");
 auto second=std::make_unique<ImageRealm>(2);check(second->image!=oldURI,"Replacement native Broker nonce never aliases original URI");check(preview_uri_router_bind(router,second->endpoint.get(),view,2,&error) && !error,"Greater same-binding realm replaces stable route");refused(preview_uri_router_open(callback,view,oldURI.c_str(),&length,&error));check(second->endpoint->readers()==0,"Old exact opaque URI does not allocate replacement reader");
 ImageRealm foreign(3,4);check(!preview_uri_router_bind(router,foreign.endpoint.get(),view,3,&error) && error,"Foreign Native binding cannot replace original router authority");g_clear_error(&error);
 auto oldRealm=second->endpoint->readCapability(77,2);auto current=preview_uri_router_open(callback,view,second->image.c_str(),&length,&error);check(current && !error && second->endpoint->readers()==1,"Foreign binding refusal preserves original current route");
 second->endpoint->unregisterView(77);check(second->endpoint->registerView(77,{{1},{2},{3}},{1}) && second->endpoint->registeredView(77)->epoch==3,"Actual same-Shared receiver replacement advances epoch");refused(oldRealm.open(77,second->image,&length,&error));refused(preview_uri_router_open(callback,view,second->image.c_str(),&length,&error));readDenied(current);close(current);
 check(preview_uri_router_bind(router,second->endpoint.get(),view,3,&error) && !error,"Trusted current receiver capability restores route");
 check(preview_uri_router_clear(router,&error) && !error,"Native clear revokes route without resetting its frontier");check(!preview_uri_router_bind(router,second->endpoint.get(),view,3,&error) && error,"Clear refuses old current realm rebind");g_clear_error(&error);refused(preview_uri_router_open(callback,view,second->image.c_str(),&length,&error));
 auto third=std::make_unique<ImageRealm>(4);check(preview_uri_router_bind(router,third->endpoint.get(),view,4,&error) && !error,"Clear retains frontier and permits greater trusted realm");
 auto fresh=preview_uri_router_open(callback,view,third->image.c_str(),&length,&error);check(fresh && !error && third->endpoint->readers()==1,"Greater routed realm opens actual current image");*third->now=50;refused(preview_uri_router_open(callback,view,third->image.c_str(),&length,&error));readDenied(fresh);check(third->endpoint->readers()==1 && fcntl(third->descriptor,F_GETFD)>=0,"Original expiry cannot erase a retained reader or physical mapping");close(fresh);
 check(preview_uri_router_clear(router,&error) && !error,"Owner clears callback route before releasing its reference");preview_uri_router_unref(router);router=nullptr;refused(preview_uri_router_open(callback,view,third->image.c_str(),&length,&error));preview_uri_router_unref(callback);
 const auto secondFD=second->descriptor,thirdFD=third->descriptor,foreignFD=foreign.descriptor;second.reset();third.reset();foreign.endpoint.reset();check(fcntl(secondFD,F_GETFD)==-1 && errno==EBADF && fcntl(thirdFD,F_GETFD)==-1 && fcntl(foreignFD,F_GETFD)==-1,"All actual owned fixture mappings close normally");
 std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"actualSealedFDs\":4,\"staleCapabilityRefused\":true,\"independentCallbackReference\":true,\"actualFDsClosed\":true,\"actualWebKitCallback\":false,\"nativeAcceptance\":false}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
