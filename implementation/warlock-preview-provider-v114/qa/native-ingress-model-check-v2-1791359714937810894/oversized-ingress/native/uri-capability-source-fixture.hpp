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
