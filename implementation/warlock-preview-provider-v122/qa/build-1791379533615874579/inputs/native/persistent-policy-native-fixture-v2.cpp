#include "capture-resource-source-fixture.hpp"
#include "elm-preview-policy.h"
using namespace preview;
static std::string take(char*& text){require(text,"Native outbox output");std::string value(text);g_free(text);text=nullptr;return value;}
int main(int argc,char** argv){try{
 require(argc==2,"Held compiled native Elm worker required");
 Server server("capture-refused");GError* error=nullptr;
 gchar* program=nullptr;gsize programSize=0;require(g_file_get_contents(argv[1],&program,&programSize,&error) && !error,"Held compiled policy asset");
 auto policy=warlock_preview_policy_new(program,programSize,&error);g_free(program);if(!policy || error){std::string why=error?error->message:"No native policy";g_clear_error(&error);throw std::runtime_error(why);}
 auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);check(bootstrap && !error,"Original authenticated Bootstrap");
 auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);require(transport && !error,"Original Native transport");
 auto& native=*static_cast<Native*>(transport);const auto binding=native.binding();auto popup=reinterpret_cast<gpointer>(uintptr_t(77));
 WarlockImportedClients* owner=nullptr;ReceiptDelivery* delivery=nullptr;uri::Endpoint* endpoint=nullptr;uint64_t epoch=0;char* text=nullptr;
 auto open=[&]{char* grant=nullptr;void* raw=nullptr;owner=warlock_imported_clients_open_controlled(transport,popup,21,1,1,&text,&grant,&raw,&error);
  require(owner && text && grant && raw && !error,"Actual controlled C owner");auto seeds=take(text);auto grantWire=take(grant);Json g(grantWire);epoch=g.counter("receiverEpoch");endpoint=static_cast<uri::Endpoint*>(raw);
  require(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Actual borrowed receipt channel");
  delivery=static_cast<ReceiptDelivery*>(warlock_preview_bootstrap_delivery(bootstrap,popup,&error));require(delivery && !error,"Original borrowed delivery");
  return "{\"events\":"+seeds+",\"grant\":"+grantWire+",\"epoch\":\""+std::to_string(epoch)+"\"}";
 };
 std::cout<<open()<<std::endl;std::string line;
 while(std::getline(std::cin,line)){
  require(line.size()<=65536,"Bounded fixture operation");Json request(line);auto obj=request.object();const std::string op=Json::text(obj,"op");bool ok=false;std::string result="null",receipt="null";
  if(op=="policy") {ok=warlock_preview_policy_invoke(policy,Json::text(obj,"input"),&text,&error);if(text)result=take(text);}
  else if(op=="policy-close-probe") {ok=warlock_preview_policy_close(policy,&error);require(!ok && error,"Original policy cannot discard retained membership or open realm");}
  else if(op=="propose") {ok=warlock_imported_clients_propose_control_at_epoch(owner,delivery,popup,request.counter("epoch"),Json::text(obj,"identity"),Json::text(obj,"command"),&text,&error);if(text)result=take(text);}
  else if(op=="propose-envelope") {ok=warlock_imported_clients_propose_envelope(owner,delivery,popup,Json::text(obj,"envelope"),&text,&error);if(text)result=take(text);}
  else if(op=="dispatch") {char* delivered=nullptr;ok=warlock_imported_clients_dispatch_control(owner,delivery,popup,Json::text(obj,"wire"),&text,&delivered,&error);if(text)result=take(text);if(delivered)receipt=take(delivered);}
  else if(op=="confirm") {ok=warlock_imported_clients_confirm_control(owner,popup,Json::text(obj,"wire"),&text,&error);if(text)result=take(text);}
  else if(op=="recovery-begin") {ok=warlock_imported_clients_control_recovery_begin(owner,popup,request.counter("epoch"),&text,&error);if(text)result=take(text);}
  else if(op=="recovery-next") {
   auto count=[&](const char* name){auto value=std::string(Json::text(obj,name));return value=="0"?uint64_t(0):decimal(value);};
   ok=warlock_imported_clients_control_recovery_next(owner,popup,request.counter("epoch"),count("issued"),count("delivered"),count("confirmed"),count("after"),&text,&error);if(text)result=take(text);
  }
  else if(op=="terminal") {ok=warlock_preview_bootstrap_pending(bootstrap,popup,&text,&error);if(text)result=take(text);}
  else if(op=="close-probe") {ok=warlock_imported_clients_close_bootstrap(owner,bootstrap,&error);require(!ok && error && native.previewControlClaimed(),"Actual strict close refuses unsettled owner");}
  else if(op=="poll") {ok=warlock_imported_clients_retirement_poll(owner,delivery,popup,&text,&error);if(text)result=take(text);}
  else if(op=="seed") {ok=warlock_imported_clients_detachment_inventory(owner,popup,"family:21",&text,&error);if(text)result=take(text);}
  else if(op=="pending") {ok=warlock_imported_clients_detachment_pending(owner,delivery,popup,&text,&error);if(text)result=take(text);}
  else if(op=="status") {
   result=endpoint->native([&](auto& broker){auto rows=broker.inspect();Wire w;w.text("records",std::to_string(rows.size())).text("charge",std::to_string(broker.charge()));uint64_t captures=0;std::ifstream(server.root/"capture-count")>>captures;w.text("captures",std::to_string(captures));if(!rows.empty()){auto& row=rows.front();w.begin("job").job(row.job).end().boolean("terminal",row.terminal).text("proofs",std::to_string(row.proofs.size()));if(!row.proofs.empty())w.counter("sequence",row.proofs.back().sequence.value);}return w.finish();});ok=true;
  }else if(op=="replace" || op=="finish") {
   require(warlock_imported_clients_empty(owner) && warlock_imported_clients_close_bootstrap(owner,bootstrap,&error) && !error,"Original strict settled realm close");owner=nullptr;delivery=nullptr;endpoint=nullptr;
   require(native.binding()==binding && !native.previewControlClaimed(),"No Native grant reset on close");
   RetirementCursor cursor;require(observeIncarnationRetirement(native,{21},cursor).state==IncarnationState::Active,"Synthetic native application stays Active");
   if(op=="replace"){result=open();ok=true;}
   else {const auto close=std::string("{\"kind\":\"closed\",\"value\":{")+"\"binding\":"+Wire().binding(binding).finish()+",\"receiverEpoch\":\""+std::to_string(epoch)+"\"}}";
    require(warlock_preview_policy_invoke(policy,close.c_str(),&text,&error) && !error,"Actual native strict close notifies retained policy");take(text);
    require(warlock_preview_policy_close(policy,&error) && !error,"Original native-owned policy normal closed exit");policy=nullptr;
    warlock_preview_bootstrap_free(bootstrap);server.finish();std::cout<<"{\"finished\":true,\"normalOwnedPeerExit\":true}"<<std::endl;return 0;}
  }else require(false,"Closed fixture operation set");
  const bool refused=bool(error);g_clear_error(&error);
  std::cout<<"{\"ok\":"<<(ok?"true":"false")<<",\"refused\":"<<(refused?"true":"false")<<",\"result\":"<<result<<",\"receipt\":"<<receipt<<"}"<<std::endl;
 }
 require(false,"Explicit normal fixture close");
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
