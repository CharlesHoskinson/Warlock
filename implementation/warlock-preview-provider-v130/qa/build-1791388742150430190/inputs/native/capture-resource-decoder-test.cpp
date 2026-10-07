#include "capture-resource-source-fixture.hpp"
using namespace preview;
int main(){try{
 Server server;auto native=server.open();const auto source=native->clientScope({21});const auto intent=prepareClientCapture(*native,source,source.scope.now+2000000000ULL);
 const auto binding=native->binding();const auto request=native->next();
 preview::resources::Result result{{binding.lifetime.value,binding.session.value,binding.frontend.value},{intent.request(),21},
     request,5,binding.lifetime.value,source.scope.now+1000,preview::resources::Operation::Observe,preview::resources::Status::Observed,4096,9007199254740995ULL,4096,true};
 const auto original=preview::resources::wire(result);
 ClientResourceCursor cursor{binding,4,source.scope.now};auto decoded=decodeClientResources(Json(original),intent,ClientResourceOperation::Observe,request,cursor);
 check(decoded.producerBytes==4096 && decoded.exportTransfer==9007199254740995ULL && cursor.sequence==5 && decoded.locked,"Lossless authenticated original native resource observation");
 for(const auto& [old,value]:std::vector<std::pair<std::string,std::string>>{
  {"\"protocolVersion\":3","\"protocolVersion\":3.0"},{"\"protocolVersion\":3","\"protocolVersion\":true"},
  {"\"resourceProtocol\":1","\"resourceProtocol\":2"},{"preview-client-resources","other"},{"\"operation\":\"observe\"","\"operation\":\"retire-producer\""},
  {"\"frontend\":\"9007199254740993\"","\"frontend\":\"1\""},
  {"\"requestId\":\""+std::to_string(request)+"\"","\"requestId\":\""+std::to_string(request+1)+"\""},
  {"\"captureRequest\":\""+std::to_string(intent.request())+"\"","\"captureRequest\":\""+std::to_string(intent.request()+1)+"\""},
  {"\"subjectIncarnation\":\"21\"","\"subjectIncarnation\":\"22\""},
  {"\"sequence\":\"5\"","\"sequence\":\"4\""},{"\"sequence\":\"5\"","\"sequence\":5"},
  {"\"sequence\":\"5\"","\"sequence\":\"05\""},{"\"sequence\":\"5\"","\"sequence\":\"18446744073709551616\""},
  {"\"clock\":\"18446744073709551615\"","\"clock\":\"1\""},
  {"\"now\":\""+std::to_string(result.now)+"\"","\"now\":\""+std::to_string(source.scope.now-1)+"\""},
  {"\"producerState\":\"Owned\"","\"producerState\":\"Retired\""},{"\"exportState\":\"Live\"","\"exportState\":\"Released\""},
  {"\"producerBytes\":\"4096\"","\"producerBytes\":\"0\""},{"\"exportBytes\":\"4096\"","\"exportBytes\":\"0\""},
  {"\"exportBytes\":\"4096\"","\"exportBytes\":\"4097\""},{"\"exportTransfer\":\"9007199254740995\"","\"exportTransfer\":\"0\""},
  {"\"status\":\"Observed\"","\"status\":\"Settled\""},{"\"locked\":true","\"locked\":1"},
  {"\"sequence\":\"5\"","\"sequence\":\"0\""},{"\"kind\":\"preview-client-resources\"","\"extra\":true,\"kind\":\"preview-client-resources\""},
  {"\"sequence\":\"5\"","\"sequence\":\"4\",\"sequence\":\"5\""},
  {"preview-client-resources","preview-client-resources\\u0000tail"}}) {
  auto changed=original;replace(changed,old,value);ClientResourceCursor unchanged{binding,4,source.scope.now};
  check(denied([&]{decodeClientResources(Json(changed),intent,ClientResourceOperation::Observe,request,unchanged);}) &&
      unchanged.binding==std::optional<Binding>{binding} && unchanged.sequence==4 && unchanged.now==source.scope.now,
      "Malformed original native resource reply cannot partially advance cursor");
 }
 ClientResourceCursor foreign{Binding{{1},{2},{3}},4,source.scope.now};
 check(denied([&]{decodeClientResources(Json(original),intent,ClientResourceOperation::Observe,request,foreign);}) && foreign.sequence==4,"Original resource cursor cannot change binding domain");
 check(denied([&]{decodeClientResources(Json(original),intent,ClientResourceOperation::Observe,intent.request(),cursor);}),"Resource query cannot target current or future capture serial");
 result.operation=preview::resources::Operation::RetireProducer;result.status=preview::resources::Status::PendingExport;result.sequence=6;
 check(decodeClientResources(Json(preview::resources::wire(result)),intent,ClientResourceOperation::RetireProducer,request,cursor).status==ClientResourceStatus::PendingExport,"Original native export blocks producer retirement even while locked");
 result.exportTransfer=result.exportBytes=0;result.status=preview::resources::Status::PendingLock;result.sequence=7;
 check(decodeClientResources(Json(preview::resources::wire(result)),intent,ClientResourceOperation::RetireProducer,request,cursor).status==ClientResourceStatus::PendingLock,"Original native locked producer remains pending");
 result.locked=false;result.sequence=8;
 check(denied([&]{decodeClientResources(Json(preview::resources::wire(result)),intent,ClientResourceOperation::RetireProducer,request,cursor);}) && cursor.sequence==7,"PendingLock requires actual original lock observation");
 result.status=preview::resources::Status::Settled;result.producerBytes=0;result.sequence=UINT64_MAX;
 check(decodeClientResources(Json(preview::resources::wire(result)),intent,ClientResourceOperation::RetireProducer,request,cursor).backendEmpty() && cursor.sequence==UINT64_MAX,"Native resource sequence maximum is lossless without reset");
 check(denied([&]{decodeClientResources(Json(preview::resources::wire(result)),intent,ClientResourceOperation::RetireProducer,request,cursor);}) && cursor.sequence==UINT64_MAX,"Exhausted original native sequence cannot be replayed or reset");
 server.finish();std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"normalOwnedExit\":true,\"nativeAcceptance\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
