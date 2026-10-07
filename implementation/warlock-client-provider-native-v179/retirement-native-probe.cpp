#include "imported_clients.hpp"
#include "imported-clients.h"
#include "preview-provider-bootstrap.h"
#include <chrono>
#include <fstream>
#include <iostream>
#include <thread>
using namespace preview;using namespace preview::bridge;
int main(int argc,char** argv){try{
 require(argc==5,"Own authority config, two native subjects and private control file");
 unsigned checks=0;auto check=[&](bool ok,const char* reason){require(ok,reason);++checks;};
 GError* error=nullptr;const auto first=decimal(argv[2]),second=decimal(argv[3]);
 check(first!=second,"Distinct actual native retirement subjects");
 auto bootstrap=warlock_preview_bootstrap_open(argv[1],&error);check(bootstrap && !error,"Actual own native bootstrap");
 auto native=static_cast<Native*>(warlock_preview_bootstrap_native_transport(bootstrap,&error));check(native && !error,"Actual authenticated native transport");
 auto popup=reinterpret_cast<gpointer>(uintptr_t(77));char* events=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open(native,popup,first,second,1,1,&events,&raw,&error);
 check(owner && events && raw && !error,"Actual C imported source admission");g_free(events);
 auto& endpoint=*static_cast<uri::Endpoint*>(raw);
 check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Exact native C receipt receiver");
 const auto old=endpoint.native([](auto& broker){return broker.inspect();});check(old.size()==2,"Actual two retained native reservations");
 const auto unchanged=[&]{return endpoint.native([&](auto& broker){auto rows=broker.inspect();return rows.size()==2 && rows[0].job==old[0].job && rows[1].job==old[1].job && broker.requestFloor(1)==1 && broker.requestFloor(2)==1 && broker.activeItems()==2 && broker.charge()==old[0].bytes+old[1].bytes;});};
 uint64_t sequence=0,now=0,frontier=0,request=0;
 const auto observe=[&](uint64_t subject,const char* state){
  char* facts=nullptr;const auto identity="family:"+std::to_string(subject);
  check(warlock_imported_clients_retirement_state(owner,identity.c_str(),&facts,&error) && facts && !error,"Actual typed C retirement observation");
  const std::string text(facts);g_free(facts);Json fact(text);auto object=fact.object();
  check(std::string_view(Json::text(object,"kind"))=="native-incarnation-retirement" && decodeBinding(Json::child(object,"binding"))==native->binding() && fact.counter("subject")==subject && fact.counter("clock")==native->binding().lifetime.value && std::string_view(Json::text(object,"state"))==state,"Exact real native C retirement identity and state");
  check(fact.counter("sequence")>sequence && fact.counter("now")>=now && decimal(Json::text(object,"issuedThrough"))>=frontier && subject<=decimal(Json::text(object,"issuedThrough")),"Monotonic real native C retirement facts");
  sequence=fact.counter("sequence");now=fact.counter("now");frontier=decimal(Json::text(object,"issuedThrough"));request=fact.counter("request");
  check(unchanged(),"Native retirement observation preserves all original job and allocator ownership");
  std::cout<<"{\"stage\":\"observation\",\"fact\":"<<text<<"}\n"<<std::flush;
 };
 observe(first,"Active");observe(second,"Active");
 char* facts=nullptr;check(!warlock_imported_clients_retirement_state(owner,"family:18446744073709551615",&facts,&error) && !facts && error,"Foreign C actor refused before real native query");g_clear_error(&error);
 check(native->next()==request+1,"Foreign C actor consumes no native request");
 std::cout<<"{\"stage\":\"ready\",\"checks\":"<<checks<<"}\n"<<std::flush;
 const auto cutoff=std::chrono::steady_clock::now()+std::chrono::seconds(10);
 for(;;){std::ifstream control(argv[4]);std::string action;std::getline(control,action);if(action=="closed")break;check(std::chrono::steady_clock::now()<cutoff,"Private parent retirement trigger arrives");std::this_thread::sleep_for(std::chrono::milliseconds(10));}
 observe(first,"Retired");observe(second,"Active");
 endpoint.native([&](auto& broker){for(const auto& row:old){auto terminal=broker.producerRefused(row.entry,row.job);check(terminal.status==Result::Status::Complete && !terminal.receipts.empty(),"Actual untouched native reservation terminal proof");}});
 for(const auto& row:old){const auto sequence=endpoint.native([&](auto& broker){for(const auto& record:broker.inspect())if(record.entry==row.entry){require(record.terminal && !record.proofs.empty(),"Exact final own native proof");return record.proofs.back().sequence;}throw std::runtime_error("Retained native terminal proof");});
  Wire out;auto command=out.text("kind","acknowledge").begin("job").job(row.job).end().counter("sequence",sequence.value).finish();
  auto identity="family:"+std::to_string(row.job.context.incarnation.value);
  check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity.c_str(),command.c_str(),&error) && !error,"Exact actual C final journal ACK");
 }
 check(warlock_imported_clients_empty(owner) && endpoint.readers()==0 && endpoint.native([](auto& broker){return broker.recordCount()==0 && broker.charge()==0 && broker.activeItems()==0;}),"Complete original reservation and journal cleanup");
 check(warlock_imported_clients_close(owner,&error) && !error,"Actual native C owner closes");warlock_preview_bootstrap_free(bootstrap);
 std::cout<<"{\"stage\":\"complete\",\"passed\":true,\"checks\":"<<checks<<",\"actorTurnoverAccepted\":false,\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n"<<std::flush;return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 2;}}
