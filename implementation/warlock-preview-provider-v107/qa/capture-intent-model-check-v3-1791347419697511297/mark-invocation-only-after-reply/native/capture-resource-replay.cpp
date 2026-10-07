#include "capture-resource-source-fixture.hpp"
using namespace preview;
int main(){try{
 Server server;auto native=server.open();const auto source=native->clientScope({21});const auto original=prepareClientCapture(*native,source,source.scope.now+2000000000ULL);
 const auto binding=native->binding();std::map<pid_t,ResourceProbe> captures;
 auto make=[&](uint64_t request){ResourceProbe p;p.session=binding.session.value;p.frontend=binding.frontend.value;p.incarnation=21;p.request=request;captures.insert_or_assign(getpid(),std::move(p));};
 make(original.request());uint64_t sequence=0;ClientResourceCursor cursor;bool locked=false,unknown=true;uint64_t seenProducer=4096;bool seenExport=true;int status=0;
 for(std::string event;std::getline(std::cin,event);){int last=0;
  try{
   if(event=="Lock")locked=true;
   else if(event=="Unlock")locked=false;
   else if(event=="OtherCapture") {check(captures.empty(),"Original resource retirement precedes another capture");make(original.request()+1);}
   else if(event!="Confirm") {
    const bool release=event=="Release" || event=="LostRelease" || event=="BadTransfer";
    const bool retire=event=="Retire" || event=="LostRetire";
    const auto operation=release?preview::resources::Operation::ReleaseExport:retire?preview::resources::Operation::RetireProducer:preview::resources::Operation::Observe;
    const auto request=native->next();
    auto wire=preview::resources::execute(captures,getpid(),preview::resources::Binding{binding.lifetime.value,binding.session.value,binding.frontend.value},
        preview::resources::Target{original.request(),event=="BadSubject"?22ULL:21ULL},request,source.scope.now+request*1000,
        locked,operation,release?(event=="BadTransfer"?1ULL:9007199254740995ULL):0,sequence,[&](const preview::resources::Result& result){
          if(event=="FailPrepare")throw std::bad_alloc();
          return preview::resources::wire(result);
        });
    if(event=="LostRelease" || event=="LostRetire"){unknown=true;last=2;}
    else {
     if(event=="BadReply")replace(wire,"\"status\":\"Observed\"","\"status\":\"Bogus\"");
     try {
      auto fact=decodeClientResources(Json(wire),original,release?ClientResourceOperation::ReleaseExport:retire?ClientResourceOperation::RetireProducer:ClientResourceOperation::Observe,request,cursor);
      seenProducer=fact.producerBytes;seenExport=bool(fact.exportTransfer);unknown=false;status=static_cast<int>(fact.status);last=1;
     }catch(const std::exception&){unknown=true;last=2;}
    }
   }
  }catch(const std::exception&){last=-1;}
  auto it=captures.find(getpid());const bool present=it!=captures.end(),other=present && it->second.request!=original.request();
  std::cout<<Wire().boolean("producer",present && !other).boolean("exported",present && !other && bool(it->second.exported))
    .boolean("other",other).boolean("locked",locked).integer("sequence",sequence).integer("cursor",cursor.sequence)
    .integer("seenProducer",seenProducer).boolean("seenExport",seenExport).boolean("unknown",unknown).integer("status",status).integer("last",last).finish()<<'\n';
 }
 captures.clear();server.finish();return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
