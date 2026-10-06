#include "preview_retirement.hpp"
#include "imported_clients.hpp"
#include <thread>
#include "preview_delivery.hpp"
#include "imported-clients.h"
#include "preview-provider-bootstrap.h"
#include <filesystem>
#include <functional>
#include <iostream>
#include <sys/wait.h>
#include <climits>

using namespace preview::bridge;
namespace fs=std::filesystem;
namespace fd=preview::fd;
static unsigned passed;
static void check(bool value,const char* name) {require(value,name);++passed;}
template<class F> static bool denied(F&& function) {try{function();return false;}catch(const std::exception&){return true;}}
static std::string digest() {
    auto data=g_checksum_new(G_CHECKSUM_SHA256);std::ifstream file("/proc/self/exe",std::ios::binary);std::array<char,8192> buffer{};
    while(file){file.read(buffer.data(),buffer.size());g_checksum_update(data,reinterpret_cast<const guchar*>(buffer.data()),file.gcount());}
    auto result=std::string(g_checksum_get_string(data));g_checksum_free(data);return result;
}
static void replace(std::string& text,std::string_view old,std::string_view value) {auto pos=text.find(old);require(pos!=text.npos,"Fixture mutation found");text.replace(pos,old.size(),value);}
static std::string reply(pid_t core,pid_t peer,const std::string& mode,uint64_t frontend) {
    std::string text="{\"protocolVersion\":3,\"kind\":\"attached\",\"binding\":{\"lifetime\":\"18446744073709551615\",\"session\":\""+std::to_string(peer)+"\",\"frontend\":\""+std::to_string(frontend)+"\"},\"previewFdAddress\":\"fixture_preview\",\"compositor\":{\"pid\":"+std::to_string(core)+",\"instance\":\"fixture\",\"coreHash\":\"fixture-ABI\"},\"capabilities\":{\"observe\":true,\"effects\":true,\"minimizedState\":true,\"effectProtocol\":1,\"operations\":[\"minimize\",\"restore\",\"activate\"],\"canonicalScene\":false,\"taskbarProjectionProtocol\":1,\"effectInvalidationProtocol\":1}}";
    if(mode=="quoted-abi")replace(text,"fixture-ABI","fixture-ABI\\\"\\\\tail");
    if(mode=="version")replace(text,"\"protocolVersion\":3","\"protocolVersion\":4");
    if(mode=="bool-version")replace(text,"\"protocolVersion\":3","\"protocolVersion\":true");
    if(mode=="float-version")replace(text,"\"protocolVersion\":3","\"protocolVersion\":3.0");
    if(mode=="duplicate")replace(text,"\"kind\":\"attached\"","\"kind\":\"refused\",\"kind\":\"attached\"");
    if(mode=="escaped-duplicate")replace(text,"\"kind\":\"attached\"","\"k\\u0069nd\":\"refused\",\"kind\":\"attached\"");
    if(mode=="nested-duplicate")replace(text,"\"frontend\":\"9007199254740993\"","\"frontend\":\"1\",\"frontend\":\"9007199254740993\"");
    if(mode=="nul")replace(text,"\"attached\"","\"attached\\u0000anything\"");
    if(mode=="zero")replace(text,"\"9007199254740993\"","\"0\"");
    if(mode=="leading-zero")replace(text,"\"9007199254740993\"","\"01\"");
    if(mode=="overflow")replace(text,"\"18446744073709551615\"","\"18446744073709551616\"");
    if(mode=="numeric-counter")replace(text,"\"9007199254740993\"","9007199254740993");
    if(mode=="wrong-pid")replace(text,"\"pid\":"+std::to_string(core),"\"pid\":"+std::to_string(core+1));
    if(mode=="float-pid")replace(text,"\"pid\":"+std::to_string(core),"\"pid\":"+std::to_string(core)+".0");
    if(mode=="wrong-instance")replace(text,"\"fixture\"","\"other\"");
    if(mode=="extra")text.insert(1,"\"unknown\":true,");
    if(mode=="wrong-caps")replace(text,"\"observe\":true","\"observe\":1");
    if(mode=="wrong-operations")replace(text,"\"activate\"","\"close\"");
    if(mode=="bad-fd")replace(text,"\"fixture_preview\"","\"\"");
    if(mode=="oversized")return std::string(65537,' ')+text;
    if(mode=="raw-nul")text.insert(5,1,'\0');
    return text;
}
static std::string scopeReply(pid_t peer,uint64_t frontend,JsonObject* request,const std::string& mode) {
    Json::fields(request,{"protocolVersion","kind","binding","requestId","subjectIncarnation"});
    require(Json::integer(request,"protocolVersion")==3,"Fixture scope protocol");
    preview::Binding binding{{UINT64_MAX},{uint64_t(peer)},{frontend}};
    require(decodeBinding(Json::child(request,"binding"))==binding,"Fixture scope actual peer grant");
    const auto id=decimal(Json::text(request,"requestId")),subject=decimal(Json::text(request,"subjectIncarnation"));
    preview::Context context{{UINT64_MAX},{subject},{9007199254740993ULL},{2},{3},{4},{5}};
    const bool client=std::string_view(Json::text(request,"kind"))=="preview-client-scope-request";
    const std::string source=client?"isolated-root-client-unqualified":"root-surface-commit-monitor-plane-unqualified";
    const std::string kind=client?"preview-client-scope":"preview-capture-probe-scope";
    Wire out;out.integer("protocolVersion",3).text("kind",kind).begin("binding").binding(binding).end().counter("requestId",id).begin("scope").begin("binding").binding(binding).end().begin("context").context(context).end().counter("observation",id).counter("clock",UINT64_MAX).counter("now",9007199254740993ULL+id*1000000ULL+(mode=="resume-expire" && id>=5?3000000000ULL:0)).boolean("present",true).boolean("sourceLive",true).boolean("locked",false).boolean("gpuReady",true).end().counter("maximumTransferBytes",4096).boolean("previewEligible",false).text("scopeKind",source);
    auto text=out.finish();
    if(mode=="scope-kind")replace(text,kind+"\"","other\"");
    if(mode=="scope-request")replace(text,"\"requestId\":\""+std::to_string(id)+"\"","\"requestId\":\""+std::to_string(id+1)+"\"");
    if(mode=="scope-binding")replace(text,"\"frontend\":\""+std::to_string(frontend)+"\"","\"frontend\":\"1\"");
    if(mode=="scope-inner-binding") {auto start=text.find("\"scope\"");auto tail=text.substr(start);replace(tail,"\"frontend\":\""+std::to_string(frontend)+"\"","\"frontend\":\"1\"");text.replace(start,text.size()-start,tail);}
    if(mode=="scope-subject")replace(text,"\"incarnation\":\""+std::to_string(subject)+"\"","\"incarnation\":\"1\"");
    if(mode=="scope-lifetime") {auto start=text.find("\"context\"");auto tail=text.substr(start);replace(tail,"\"lifetime\":\"18446744073709551615\"","\"lifetime\":\"1\"");text.replace(start,text.size()-start,tail);}
    if(mode=="scope-clock")replace(text,"\"clock\":\"18446744073709551615\"","\"clock\":\"1\"");
    if(mode=="scope-zero")replace(text,"\"observation\":\"18446744073709551615\"","\"observation\":\"0\"");
    if(mode=="scope-float")replace(text,"\"observation\":\"18446744073709551615\"","\"observation\":1.0");
    if(mode=="scope-numeric")replace(text,"\"now\":\"9007199254740993\"","\"now\":9007199254740993");
    if(mode=="scope-bool")replace(text,"\"present\":true","\"present\":1");
    if(mode=="scope-extra")text.insert(1,"\"extra\":true,");
    if(mode=="scope-context-extra")replace(text,"\"context\":{","\"context\":{\"extra\":true,");
    if(mode=="scope-duplicate")replace(text,"\"scene\":\"4\"","\"scene\":\"1\",\"scene\":\"4\"");
    if(mode=="scope-eligible")replace(text,"\"previewEligible\":false","\"previewEligible\":true");
    if(mode=="scope-source-kind")replace(text,source,"family");
    if(mode=="scope-cost")replace(text,"\"maximumTransferBytes\":\"4096\"","\"maximumTransferBytes\":\"4097\"");
    return text;
}
static std::string retirementReply(pid_t peer,uint64_t frontend,JsonObject* request,const std::string& mode) {
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
struct Server {
    fs::path root;pid_t pid{-1};fd::Owned stop;std::string mode;
    explicit Server(std::string behavior="valid"):mode(std::move(behavior)) {
        char pattern[]="/tmp/wl-grant-XXXXXX";auto path=mkdtemp(pattern);require(path,"Fixture private directory");root=path;fs::create_directories(root/"hypr/fixture");chmod((root/"hypr").c_str(),0700);chmod((root/"hypr/fixture").c_str(),0700);
        int signal[2],ready[2];require(pipe2(signal,O_CLOEXEC)==0 && pipe2(ready,O_CLOEXEC)==0,"Fixture pipes");pid=fork();require(pid>=0,"Fixture server fork");
        if(!pid) {
            close(signal[1]);close(ready[0]);int code=0;
            try {
                fd::Owned listener(::socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0));sockaddr_un address{};address.sun_family=AF_UNIX;auto path=(root/"hypr/fixture/.socket.sock").string();memcpy(address.sun_path,path.c_str(),path.size()+1);
                require(listener && bind(listener.get(),reinterpret_cast<sockaddr*>(&address),sizeof(address))==0 && listen(listener.get(),8)==0,"Fixture listens in actual server process");require(write(ready[1],"R",1)==1,"Fixture ready");close(ready[1]);
                bool running=true;std::map<pid_t,uint64_t> frontends;
                while(running) {
                    pollfd items[2]{{signal[0],POLLIN,0},{listener.get(),POLLIN,0}};auto n=poll(items,2,10000);if(n<0 && errno==EINTR)continue;require(n>0,"Fixture control wait");if(items[0].revents)break;
                    fd::Owned connection(accept4(listener.get(),nullptr,nullptr,SOCK_CLOEXEC));require(bool(connection),"Fixture accept");timeval timeout{1,0};setsockopt(connection.get(),SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout));
                    ucred peer{};socklen_t size=sizeof(peer);require(getsockopt(connection.get(),SOL_SOCKET,SO_PEERCRED,&peer,&size)==0,"Fixture actual client peer");
                    std::string request;std::array<char,1024> buffer{};bool complete=false;
                    for(;;){auto got=recv(connection.get(),buffer.data(),buffer.size(),0);if(got<0 && errno==EINTR)continue;if(got<0)break;if(!got){complete=true;break;}request.append(buffer.data(),got);if(request.size()>4112)break;}
                    if(!complete || !request.starts_with("j/elm_observe "))continue;
                    Json envelope(request.substr(14));const auto kind=std::string_view(Json::text(envelope.object(),"kind"));
                    auto& frontend=frontends[peer.pid];std::string text;
                    if(kind=="hello") {frontend=frontend?frontend+1:9007199254740993ULL;text=reply(getpid(),peer.pid,mode,frontend);}
                    else if(kind=="preview-incarnation-retirement-state-request") {require(frontend,"Enrolled native retirement peer");uint64_t retired=0;std::ifstream(root/"retired-through")>>retired;const auto subject=decimal(Json::text(envelope.object(),"subjectIncarnation"));text=retirementReply(peer.pid,frontend,envelope.object(),subject!=22 && subject<=retired?"retired":"valid");replace(text,"\"issuedThrough\":\"22\"","\"issuedThrough\":\"100000\"");}
                    else {require((kind=="preview-capture-probe-scope-request" || kind=="preview-client-scope-request") && frontend,"Fixture known enrolled scope request");uint64_t retired=0;std::ifstream(root/"retired-through")>>retired;const auto subject=decimal(Json::text(envelope.object(),"subjectIncarnation"));text=subject!=22 && subject<=retired?"{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"preview-client-scope-source-unavailable\"}":scopeReply(peer.pid,frontend,envelope.object(),mode);}
                    fd::Owned replacement;
                    if(mode=="replace-socket") {require(unlink(path.c_str())==0,"Fixture socket unlink");replacement=fd::Owned(::socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0));require(bind(replacement.get(),reinterpret_cast<sockaddr*>(&address),sizeof(address))==0,"Fixture replacement socket");}
                    if(mode=="replace-directory") {fs::rename(root/"hypr/fixture",root/"hypr/old");fs::create_directory(root/"hypr/fixture");chmod((root/"hypr/fixture").c_str(),0700);replacement=fd::Owned(::socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0));require(bind(replacement.get(),reinterpret_cast<sockaddr*>(&address),sizeof(address))==0,"Fixture replacement directory socket");}
                    if(mode=="slow" || (mode=="scope-slow" && kind!="hello")) {
                        for(char c:text) {if(send(connection.get(),&c,1,MSG_NOSIGNAL)!=1)break;pollfd wait{signal[0],POLLIN,0};if(poll(&wait,1,150)>0){running=false;break;}}
                    }else {size_t sent=0;while(sent<text.size()){auto got=send(connection.get(),text.data()+sent,text.size()-sent,MSG_NOSIGNAL);if(got<0 && errno==EINTR)continue;if(got<=0)break;sent+=got;}}
                }
            }catch(const std::exception& e){std::cerr<<"Fixture child: "<<e.what()<<'\n';code=2;}
            close(signal[0]);_exit(code);
        }
        close(signal[0]);close(ready[1]);stop=fd::Owned(signal[1]);fd::Owned init(ready[0]);char value{};require(read(init.get(),&value,1)==1 && value=='R',"Fixture startup acknowledged");
    }
    std::unique_ptr<Native> open() {return std::make_unique<Native>(pid,processStart(pid),root.string(),"fixture",digest());}
    void finish() {if(pid<0)return;require(write(stop.get(),"S",1)==1,"Fixture graceful stop");int status=0;require(waitpid(pid,&status,0)==pid && WIFEXITED(status) && !WEXITSTATUS(status),"Fixture normal terminal");pid=-1;fs::remove_all(root);}
    ~Server(){if(pid>=0){write(stop.get(),"S",1);int status=0;waitpid(pid,&status,0);fs::remove_all(root);}}
    fs::path config(const std::string& content="") {
        auto path=root/"authority.json";auto text=content.empty()?"{\"runtime\":\""+root.string()+"\",\"instance\":\"fixture\",\"pid\":"+std::to_string(pid)+",\"expected_start\":"+std::to_string(processStart(pid))+",\"binary_sha256\":\""+digest()+"\"}":content;
        std::ofstream(path)<<text;chmod(path.c_str(),0600);return path;
    }
};
int main(int argc,char** argv){try{
 const std::string mode=argc>1?argv[1]:"turnover";Server server("turnover");GError* error=nullptr;
 auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);check(bootstrap && !error,"Actual owning C bootstrap");
 auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);check(transport && !error,"Actual own Native transport");
 auto& native=*static_cast<Native*>(transport);auto popup=reinterpret_cast<gpointer>(uintptr_t(77));char* events=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open_dynamic(transport,popup,21,1,1,&events,&raw,&error);
 check(owner && events && raw && !error,"Actual dynamic C owner");g_free(events);
 auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);
 check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Actual original receipt enrollment");
 auto journal=warlock_preview_bootstrap_delivery(bootstrap,popup,&error);check(journal && !error,"Own journal capability");
 auto enroll=[&](uint64_t subject) {
  WarlockImportedAdmission admission=WARLOCK_IMPORTED_INVALID;char* json=nullptr;
  bool result=warlock_imported_clients_enroll(owner,popup,subject,1,1,&admission,&json,&error);
  check(result && json && !error && admission==WARLOCK_IMPORTED_STARTED,"Actual new C subject reserves original native job");g_free(json);
  check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error) && !error,"Same journal and receiver grows");
 };
 enroll(22);
 const auto epoch=endpoint.registeredView(uintptr_t(popup))->epoch;
 auto rows=endpoint.native([](auto& broker){return broker.inspect();});check(rows.size()==2,"Two actual original jobs");
 auto neighbor=rows[1].job;
 const auto originalScope=endpoint.native([](auto& broker){return broker.nativeScope(1);});
 auto inventory=[&] {
  char* json=nullptr;check(warlock_imported_clients_actor_counts(owner,journal,&json,&error) && json && !error,"Validated native inventory");
  auto result=std::string(json);g_free(json);return result;
 };
 auto settledInventory=[&](uint64_t count,uint64_t issued) {
  Json facts(inventory());
  for(auto key:{"subjects","frames","intents","slots","actors","receiverEntries","deliverySubjects"})
   check(Json::integer(facts.object(),key)==int64_t(count),"All native actor owners have equal retained membership");
  check(Json::integer(facts.object(),"predecessors")==0,"No predecessor history leaked");
  check(facts.counter("entryIssuedThrough")==issued && facts.counter("nativeEntryIssuedThrough")==issued &&
   facts.counter("brokerEntryIssuedThrough")==issued,"Nonreused frontiers survive retirement");
 };
 auto retiredThrough=[&](uint64_t subject) {std::ofstream(server.root/"retired-through")<<subject;};

 std::string deferredAck;const uint64_t lastSubject=mode=="turnover"?300:23;
 auto retirementPending=[&] {
  char* text=nullptr;check(warlock_imported_clients_retirement_pending(owner,journal,popup,&text,&error) && text && !error,"Original native completion journal read");
  std::string result=text;g_free(text);return result;
 };
 auto retire=[&](uint64_t subject,bool expected) {
  const auto identity="family:"+std::to_string(subject);char* json=nullptr;
  check(warlock_imported_clients_retirement_observe(owner,popup,identity.c_str(),&json,&error) && json && !error,"Actual original-receiver retirement observation");
  const std::string encoded=json;g_free(json);json=nullptr;Json observed("{\"rows\":"+encoded+"}");
  auto rows=json_object_get_array_member(observed.object(),"rows");require(rows,"Observation array");
  if(json_array_get_length(rows)==0){check(!expected,"Active source yields no retirement readiness grant");return;}
  check(json_array_get_length(rows)==1,"One retained exact native observation");
  auto original=json_node_get_object(json_array_get_element(rows,0));
  const auto ready=Wire().text("kind","retire-ready").begin("binding").binding(native.binding()).end().counter("subject",subject)
   .text("observationRequest",Json::text(original,"request")).text("observationSequence",Json::text(original,"sequence")).finish();
  const auto before=native.next();auto bad=ready;replace(bad,"\"subject\":\""+std::to_string(subject)+"\"","\"subject\":\"999999\"");
  check(!warlock_imported_clients_retirement_control(owner,journal,popup,identity.c_str(),bad.c_str(),&json,&error) && !json && error,"Mismatched readiness refused before native query");g_clear_error(&error);
  check(native.next()==before+1,"Mismatched readiness consumes no native query");
  check(warlock_imported_clients_retirement_control(owner,journal,popup,identity.c_str(),ready.c_str(),&json,&error) && json && !error,"Actual readiness validates native aggregate transaction");
  std::string result=json;g_free(json);json=nullptr;Json completed("{\"rows\":"+result+"}");
  auto deliveries=json_object_get_array_member(completed.object(),"rows");require(deliveries,"Completion array");
  check((json_array_get_length(deliveries)==1)==expected,"Actual physical/journal/receiver guards determine completion");
  if(!expected)return;
  auto delivery=json_node_get_object(json_array_get_element(deliveries,0));
  check(std::string_view(Json::text(delivery,"kind"))=="native-actor-retirement-delivery","Completion has independent typed delivery identity");
  auto final=Json::child(delivery,"fact");
  check(std::string_view(Json::text(final,"kind"))=="native-actor-retired" && decimal(Json::text(final,"subject"))==subject &&
    decodeBinding(Json::child(final,"binding"))==native.binding(),"Exact retained native aggregate fact");
  const auto ordinal=decimal(Json::text(delivery,"deliveryOrdinal"));
  check(retirementPending()==result && retirementPending()==result,"Lost completion remains byte-identical after native actor erasure");
  const auto acknowledged=Wire().text("kind","retire-delivery-ack").begin("binding").binding(native.binding()).end().counter("deliveryOrdinal",ordinal).finish();
  const auto gap=Wire().text("kind","retire-delivery-ack").begin("binding").binding(native.binding()).end().counter("deliveryOrdinal",ordinal+1).finish();
  check(!warlock_imported_clients_retirement_control(owner,journal,popup,identity.c_str(),gap.c_str(),&json,&error) && !json && error,"Future delivery ACK cannot skip retained completion");g_clear_error(&error);
  check(retirementPending()==result,"Gap ACK retains original final fact");
  auto foreignPopup=reinterpret_cast<gpointer>(uintptr_t(78));
  check(!warlock_imported_clients_retirement_pending(owner,journal,foreignPopup,&json,&error) && !json && error,"Foreign popup cannot read completion journal");g_clear_error(&error);
  if(subject==lastSubject){deferredAck=acknowledged;return;}
  check(warlock_imported_clients_retirement_control(owner,journal,popup,identity.c_str(),acknowledged.c_str(),&json,&error) && json && !error,"Original processing acknowledgment confirms final delivery");g_free(json);json=nullptr;
  check(retirementPending()=="[]","Confirmed completion alone removed from transport journal");
  check(warlock_imported_clients_retirement_control(owner,journal,popup,identity.c_str(),acknowledged.c_str(),&json,&error) && json && !error,"Lost ACK replay confirms without actor lookup or recreation");g_free(json);
 };
 auto terminal=[&](uint64_t entry) {
  return endpoint.native([&](auto& broker) {
   auto job=broker.inspect();auto row=std::find_if(job.begin(),job.end(),[&](const auto& item){return item.entry==entry;});
   require(row!=job.end(),"Actual known reservation");
   auto result=broker.producerRefused(entry,row->job);
   check(result.status==preview::Result::Status::Complete && !result.receipts.empty(),"Actual untouched producer closes reservation with retained receipt");
   return result.receipts.back();
  });
 };
 auto ack=[&](const preview::Receipt& receipt) {
  const auto identity="family:"+std::to_string(receipt.job.context.incarnation.value);
  const auto command=Wire().text("kind","acknowledge").begin("job").job(receipt.job).end().counter("sequence",receipt.sequence.value).finish();
  check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity.c_str(),command.c_str(),&error) && !error,"Exact final journal ACK removes only its original record");
 };
 settledInventory(2,2);const auto before=inventory();retire(21,false);check(inventory()==before,"Active observation changes no actor membership");
 retiredThrough(21);retire(21,false);
 check(endpoint.native([](auto& broker){return broker.recordCount()==2 && broker.activeItems()==2 && broker.charge()==8192;}),"Native Retired does not erase physical obligations");
 auto receipt=terminal(1);retire(21,false);
 check(endpoint.native([](auto& broker){return broker.recordCount()==2 && broker.activeItems()==1 && broker.charge()==4096;}),"Unacknowledged terminal remains after retirement refusal");
 ack(receipt);
 // A second registered native receiver must retain its membership until closed.
 check(endpoint.registerView(78,native.binding(),{1,2}),"Second real native view");
 retire(21,false);check(inventory()==before,"Foreign receiver ownership prevents partial removal");endpoint.unregisterView(78);
 const auto nextBeforeForeign=native.next();
 auto foreignPopup=reinterpret_cast<gpointer>(uintptr_t(78));
 check(!warlock_preview_bootstrap_delivery(bootstrap,foreignPopup,&error) && error,"Wrong popup cannot borrow journal");g_clear_error(&error);
 preview::uri::Endpoint foreign({256,8,2,4096},4,2,[](uint64_t)->std::optional<preview::uri::NativeTime>{return {};});
 foreign.native([&](auto& broker){check(broker.enroll(1,originalScope,4096),"Synthetic foreign endpoint has independent scope");});
 check(foreign.registerView(77,native.binding(),{1}),"Foreign endpoint receiver");ReceiptDelivery wrong(foreign,native.binding(),77);
 gboolean removed=FALSE;char* fact=nullptr;
 check(!warlock_imported_clients_retire_native(owner,&wrong,popup,"family:21",&removed,&fact,&error) && !removed && !fact && error,"Wrong endpoint journal rejected before native query");g_clear_error(&error);
 check(native.next()==nextBeforeForeign+1,"Foreign capability attempts never query native");
 retire(21,true);settledInventory(1,2);
 check(endpoint.native([&](auto& broker){auto retained=broker.inspect();return retained.size()==1 && retained[0].job==neighbor && broker.requestFloor(2)==1 && broker.charge()==4096;}),"Live neighbor job/floor/charge untouched");
 check(!endpoint.native([&](auto& broker){return broker.enroll(1,originalScope,4096);}),"Old absent Broker serial can never be reenrolled");
 const auto afterRetirement=native.next();
 check(!warlock_imported_clients_retirement_state(owner,"family:21",&fact,&error) && !fact && error,"Old retired C identity refused");g_clear_error(&error);
 check(!warlock_imported_clients_command(owner,"family:21","{}",&fact,&error) && !fact && error,"Old command refused before native query");g_clear_error(&error);
 check(native.next()==afterRetirement+1,"Old controls cannot query native or resurrect actor");
 const auto afterBeforeClosed=inventory();WarlockImportedAdmission deniedAdmission=WARLOCK_IMPORTED_INVALID;
 check(!warlock_imported_clients_enroll(owner,popup,21,1,1,&deniedAdmission,&events,&error) && !events && error,"Closed native subject denied actual scope");g_clear_error(&error);
 check(inventory()==afterBeforeClosed,"Scope denial consumes no C membership, serial or capacity");
 const uint64_t last=mode=="turnover"?300:23;
 for(uint64_t subject=23;subject<=last;++subject) {
  enroll(subject);const uint64_t entry=subject-20;settledInventory(2,entry);
  retiredThrough(subject);auto proof=terminal(entry);retire(subject,false);ack(proof);retire(subject,true);settledInventory(1,entry);
  check(endpoint.native([&](auto& broker){auto retained=broker.inspect();return retained.size()==1 && retained[0].job==neighbor && broker.requestFloor(2)==1;}),"Turnover retains exact original neighbor and floor");
  check(endpoint.registeredView(uintptr_t(popup))->epoch==epoch,"Turnover never replaces original receiver epoch");
 }
 ack(terminal(2));retiredThrough(last);

 check(!deferredAck.empty() && retirementPending()!="[]","Final unacknowledged completion remains after all physical jobs drain");
 const bool emptyBeforeConfirmation=warlock_imported_clients_empty(owner);
 const bool closeRefused=!warlock_imported_clients_close(owner,&error);
 if(!closeRefused) {
  owner=nullptr;g_clear_error(&error);warlock_preview_bootstrap_free(bootstrap);server.finish();
  check(false,"UnconfirmedRetirementCompletionMustPreventNativeOwnerClose");
 }
 check(error && !emptyBeforeConfirmation,"Empty predicate includes retained retirement delivery");g_clear_error(&error);
 char* confirmation=nullptr;const auto lastIdentity="family:"+std::to_string(lastSubject);
 check(warlock_imported_clients_retirement_control(owner,journal,popup,lastIdentity.c_str(),deferredAck.c_str(),&confirmation,&error) && confirmation && !error,"Original final acknowledgment completes retained close barrier");g_free(confirmation);
 check(warlock_imported_clients_empty(owner) && retirementPending()=="[]" && warlock_imported_clients_close(owner,&error) && !error,"Actual original C drain and confirmed delivery close");warlock_preview_bootstrap_free(bootstrap);server.finish();

 std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"mode\":\""<<mode<<"\",\"sequentialSubjects\":"<<last-20<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 2;}}
