"""Add a separate real Native/C/socket fixture; do not edit qualified fixtures."""
import pathlib, resource, sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
root=repo/'implementation/warlock-preview-provider-v82'
source=(repo/'implementation/warlock-preview-provider-v81/native/resume-enrollment-test.cpp').read_text()
text=source[:source.index('int main(')]
text='#include "preview_retirement.hpp"\n'+text
marker='struct Server {\n';assert text.count(marker)==1
function=r'''static std::string retirementReply(pid_t peer,uint64_t frontend,JsonObject* request,const std::string& mode) {
    Json::fields(request,{"protocolVersion","kind","binding","requestId","subjectIncarnation"});
    const preview::Binding binding{{UINT64_MAX},{uint64_t(peer)},{frontend}};
    require(decodeBinding(Json::child(request,"binding"))==binding,"Actual retirement query peer grant");
    const auto id=decimal(Json::text(request,"requestId")),subject=decimal(Json::text(request,"subjectIncarnation"));
    const uint64_t sequence=mode=="regress" && id>3?1:id;
    const uint64_t clock=mode=="bad-clock"?1:UINT64_MAX;
    return Wire().integer("protocolVersion",3).text("kind","preview-incarnation-retirement-state")
        .integer("retirementProtocol",1).begin("binding").binding(binding).end()
        .counter("requestId",mode=="bad-request"?id+1:id).counter("subjectIncarnation",subject)
        .counter("sequence",sequence).counter("clock",clock).counter("now",9007199254740993ULL+id*1000000ULL)
        .text("issuedThrough","22").text("state",mode=="retired"?"Retired":"Active").finish();
}
'''
text=text.replace(marker,function+marker)
marker='                    else {require((kind=="preview-capture-probe-scope-request" || kind=="preview-client-scope-request")'
assert text.count(marker)==1
text=text.replace(marker,'                    else if(kind=="preview-incarnation-retirement-state-request") {require(frontend,"Enrolled native retirement peer");text=retirementReply(peer.pid,frontend,envelope.object(),mode);}\n'+marker)
text+=r'''int main(int argc,char** argv){try{
 const std::string mode=argc>1?argv[1]:"valid";Server server(mode);GError* error=nullptr;
 auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);check(bootstrap && !error,"Actual native C bootstrap");
 auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);check(transport && !error,"Actual native C transport");
 auto& native=*static_cast<Native*>(transport);auto popup=reinterpret_cast<gpointer>(uintptr_t(77));char* events=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open(transport,popup,21,22,1,1,&events,&raw,&error);check(owner && events && raw && !error,"Actual two original C jobs");g_free(events);
 auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);
 const auto old=endpoint.native([](auto& broker){return broker.inspect();});check(old.size()==2,"Two real original Broker reservations");
 auto unchanged=[&]{return endpoint.native([&](auto& broker){auto rows=broker.inspect();return rows.size()==2 && rows[0].job==old[0].job && rows[1].job==old[1].job && broker.requestFloor(1)==1 && broker.requestFloor(2)==1 && broker.activeItems()==2 && broker.charge()==8192;});};
 char* facts=nullptr;const bool first=warlock_imported_clients_retirement_state(owner,"family:21",&facts,&error);
 if(mode=="bad-clock" || mode=="bad-request") {
  check(!first && !facts && error,"Malformed real native reply yields no C fact");g_clear_error(&error);
 }else {
  check(first && facts && !error,"Actual C/socket typed retirement fact");Json result(facts);g_free(facts);facts=nullptr;
  check(std::string_view(Json::text(result.object(),"kind"))=="native-incarnation-retirement" && decodeBinding(Json::child(result.object(),"binding"))==native.binding() && result.counter("subject")==21 && result.counter("clock")==UINT64_MAX && result.counter("request")==3 && result.counter("sequence")==3,"Exact native typed C identity and counters");
  check(std::string_view(Json::text(result.object(),"state"))==(mode=="retired"?"Retired":"Active"),"Native factual state remains typed");
  const bool second=warlock_imported_clients_retirement_state(owner,"family:22",&facts,&error);
  if(mode=="regress") {check(!second && !facts && error,"Stale native cursor reply refused at actual C boundary");g_clear_error(&error);}
  else {check(second && facts && !error,"Later own native observation accepted");Json latest(facts);g_free(facts);facts=nullptr;check(latest.counter("subject")==22 && latest.counter("sequence")==4,"Monotonic observation for neighboring actual job");}
 }
 check(unchanged(),"Observation never deletes original jobs, floors or physical obligations");
 check(!warlock_imported_clients_retirement_state(owner,"family:99",&facts,&error) && !facts && error,"Unknown native C subject refused before query");g_clear_error(&error);
 const auto expected=mode=="bad-clock" || mode=="bad-request"?4:5;
 check(endpoint.registerView(reinterpret_cast<uintptr_t>(popup),native.binding(),{1,2}),"Actual receiver replacement epoch");
 check(!warlock_imported_clients_retirement_state(owner,"family:21",&facts,&error) && !facts && error,"Replaced receiver refuses actual C retirement query");g_clear_error(&error);
 check(native.next()==uint64_t(expected),"Foreign subject and receiver replacement never query native scope");
 check(unchanged(),"Receiver refusal preserves all original physical and job owners");
 endpoint.native([&](auto& broker){for(const auto& row:old){auto terminal=broker.producerRefused(row.entry,row.job);check(terminal.status==preview::Result::Status::Complete && !terminal.receipts.empty(),"Actual producer refusal closes untouched original reservation");check(broker.acknowledge(row.entry,row.job.binding,row.job,terminal.receipts.back().sequence),"Exact final original terminal ACK");}check(broker.recordCount()==0 && broker.charge()==0,"No original records or charges after exact cleanup");});
 warlock_imported_clients_close(owner);warlock_preview_bootstrap_close(bootstrap);server.finish();
 std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"mode\":\""<<mode<<"\",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 2;}}
'''
target=root/'native/retirement-observation-test.cpp';assert not target.exists();target.write_text(text)
print(target)
