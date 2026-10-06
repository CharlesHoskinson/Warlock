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
static void check(bool value,const char* name) {require(value,name);++passed;std::cout<<"PASS "<<name<<'\n';}
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
    Wire out;out.integer("protocolVersion",3).text("kind",kind).begin("binding").binding(binding).end().counter("requestId",id).begin("scope").begin("binding").binding(binding).end().begin("context").context(context).end().counter("observation",UINT64_MAX).counter("clock",UINT64_MAX).counter("now",9007199254740993ULL+id*1000000ULL+(mode=="expire-wait" && id>=4?3000000000ULL:0)).boolean("present",true).boolean("sourceLive",true).boolean("locked",false).boolean("gpuReady",true).end().counter("maximumTransferBytes",4096).boolean("previewEligible",false).text("scopeKind",source);
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
                    else {require((kind=="preview-capture-probe-scope-request" || kind=="preview-client-scope-request") && frontend,"Fixture known enrolled scope request");text=scopeReply(peer.pid,frontend,envelope.object(),mode);}
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
int main(){try{
 Server server;GError* error=nullptr;auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);
 check(bootstrap && !error,"Same actual own process C bootstrap grant");
 auto native=static_cast<Native*>(warlock_preview_bootstrap_native_transport(bootstrap,&error));
 auto popup=reinterpret_cast<gpointer>(uintptr_t(77));char* events=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open_dynamic(native,popup,11,1,1,&events,&raw,&error);
 check(owner && raw && events && !error,"Actual dynamic C bridge opens original first native job");g_free(events);events=nullptr;
 auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);const auto view=*endpoint.registeredView(77);
 check(view.entries==std::set<uint64_t>{1} && endpoint.native([](auto& b){return b.limits().entries==256 && b.limits().items==2 && b.limits().bytes==128ULL*1024*1024 && b.recordCount()==1;}),"Dynamic actors retain original shared physical limits");
 check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Journal attached to same owning bootstrap and native endpoint");
 WarlockImportedAdmission result=WARLOCK_IMPORTED_INVALID;
 check(warlock_imported_clients_enroll(owner,popup,12,1,1,&result,&events,&error) && result==WARLOCK_IMPORTED_STARTED && events && std::string_view(events)!="[]" && !error,"Second own native subject gets actual typed job and Elm seed/request");g_free(events);events=nullptr;
 check(endpoint.registeredView(77)->epoch==view.epoch && endpoint.registeredView(77)->entries==std::set<uint64_t>{1,2},"Atomic enrollment retains receiver epoch and original membership");
 check(warlock_imported_clients_enroll(owner,popup,13,1,1,&result,&events,&error) && result==WARLOCK_IMPORTED_CAPACITY && events && std::string_view(events)=="[]" && !error,"Third subject has typed Capacity without invented job or receipt");g_free(events);events=nullptr;
 check(endpoint.native([](auto& b){return b.recordCount()==2 && b.charge()==8192 && b.requestFloor(3)==0;}) && endpoint.registeredView(77)->entries==std::set<uint64_t>{1,2,3},"Waiting native subject joins pixel view without evicting original ownership");
 char* status=nullptr;check(warlock_imported_clients_status(owner,&status,&error) && status && std::string_view(status).find("originalDeadline")!=std::string_view::npos && !error,"C status exposes unissued original intent deadline");
 const auto initialStatus=std::string(status);g_free(status);status=nullptr;
 check(warlock_imported_clients_enroll(owner,popup,13,2,1,&result,&events,&error) && result==WARLOCK_IMPORTED_CONFLICT && std::string_view(events)=="[]" && !error,"Changed publication cannot renew waiting intent");g_free(events);events=nullptr;
 check(warlock_imported_clients_enroll(owner,popup,13,1,1,&result,&events,&error) && result==WARLOCK_IMPORTED_CAPACITY && std::string_view(events)=="[]" && !error,"Same waiting intent retries without a fresh job");g_free(events);events=nullptr;
 check(warlock_imported_clients_status(owner,&status,&error) && initialStatus==status && !error,"New native query cannot change original deadline or job history");g_free(status);status=nullptr;
 auto second=endpoint.native([](auto& b){for(const auto& row:b.inspect())if(row.entry==2)return row.job;throw std::runtime_error("Actual second job");});
 auto proof=endpoint.native([&](auto& b){return b.producerRefused(2,second);});
 check(warlock_preview_bootstrap_pending(bootstrap,popup,&events,&error) && std::string_view(events)=="[]" && !error,"Pixel enrollment alone does not admit new terminal delivery subjects");g_free(events);events=nullptr;
 check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error) && !error,"Explicit C journal extension uses original own native receiver");
 check(warlock_preview_bootstrap_pending(bootstrap,popup,&events,&error) && std::string_view(events)!="[]" && !error,"Original new terminal proof becomes discoverable after explicit admission");g_free(events);events=nullptr;
 Wire command;auto encoded=command.text("kind","acknowledge").begin("job").job(second).end().counter("sequence",proof.receipts.back().sequence.value).finish();
 check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,"family:12",encoded.c_str(),&error) && !error && endpoint.native([](auto& b){return b.recordCount()==1 && b.charge()==4096;}),"Exact native terminal ACK returns original capacity");
 check(warlock_imported_clients_enroll(owner,popup,13,1,1,&result,&events,&error) && result==WARLOCK_IMPORTED_STARTED && std::string_view(events)!="[]" && !error,"Waiting actor starts only after original capacity returns");g_free(events);events=nullptr;
 auto third=endpoint.native([](auto& b){for(const auto& row:b.inspect())if(row.entry==3)return row.job;throw std::runtime_error("Actual third job");});
 check(third.request.value==1 && third.context.incarnation.value==13 && initialStatus.find(std::to_string(third.deadline))!=std::string::npos,"New job retains original native incarnation request domain and deadline");
 check(warlock_imported_clients_enroll(owner,popup,13,1,1,&result,&events,&error) && result==WARLOCK_IMPORTED_RETAINED && std::string_view(events)=="[]" && !error && endpoint.native([](auto& b){return b.requestFloor(3)==1 && b.recordCount()==2;}),"Duplicate enrollment cannot replay capture or job reservation");g_free(events);events=nullptr;
 auto child=fork();require(child>=0,"C dynamic inherited fork");if(!child){GError* inherited=nullptr;char* bytes=nullptr;WarlockImportedAdmission value;auto refused=!warlock_imported_clients_enroll(owner,popup,14,1,1,&value,&bytes,&inherited) && inherited && !bytes;g_clear_error(&inherited);_exit(refused?0:2);}int exit=0;require(waitpid(child,&exit,0)==child,"C dynamic inherited wait");check(WIFEXITED(exit) && !WEXITSTATUS(exit),"Inherited process cannot enroll under the original native grant");
 check(!warlock_imported_clients_close(owner,&error) && error && !warlock_imported_clients_empty(owner),"C close retains outstanding original physical or journal ownership");g_clear_error(&error);
 auto rows=endpoint.native([](auto& b){return b.inspect();});for(const auto& row:rows){auto terminal=endpoint.native([&](auto& b){return b.producerRefused(row.entry,row.job);});Wire ack;auto message=ack.text("kind","acknowledge").begin("job").job(row.job).end().counter("sequence",terminal.receipts.back().sequence.value).finish();auto identity="family:"+std::to_string(row.job.context.incarnation.value);require(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity.c_str(),message.c_str(),&error) && !error,"Each exact original terminal ACK");}
 check(warlock_imported_clients_empty(owner) && endpoint.native([](auto& b){return b.requestFloor(1)==1 && b.requestFloor(2)==1 && b.requestFloor(3)==1;}),"Actual reservations drain with original historical request floors retained");
 const auto old=*endpoint.registeredView(77);endpoint.unregisterView(77);check(endpoint.registerView(77,old.binding,old.entries) && endpoint.registeredView(77)->epoch!=old.epoch,"Reused popup acquires distinct actual receiver epoch");
 check(!warlock_imported_clients_enroll(owner,popup,14,1,1,&result,&events,&error) && result==WARLOCK_IMPORTED_INVALID && !events && error && denied([&]{endpoint.native([](auto& b){return b.nativeScope(4);});}),"Reused receiver refuses before native actor job or intent admission");g_clear_error(&error);
 check(warlock_imported_clients_close(owner,&error) && !error,"Dynamic C owner closes only after exact original settlement");warlock_preview_bootstrap_free(bootstrap);server.finish();
 {
 Server expired("expire-wait");auto bootstrap=warlock_preview_bootstrap_open(expired.config().c_str(),&error);check(bootstrap && !error,"Own bootstrap for expired capacity intent");
 auto native=warlock_preview_bootstrap_native_transport(bootstrap,&error);auto owner=warlock_imported_clients_open_dynamic(native,popup,21,1,1,&events,&raw,&error);check(owner && events && !error,"Own first expired-fixture reservation");g_free(events);events=nullptr;
 auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Same original expired-fixture journal");
 check(warlock_imported_clients_enroll(owner,popup,22,1,1,&result,&events,&error) && result==WARLOCK_IMPORTED_STARTED && !error,"Own second expired-fixture reservation");g_free(events);events=nullptr;
 check(warlock_imported_clients_enroll(owner,popup,23,1,1,&result,&events,&error) && result==WARLOCK_IMPORTED_CAPACITY && std::string_view(events)=="[]" && !error,"Expired-fixture original waiting intent has no job");g_free(events);events=nullptr;
 check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error) && !error,"Explicit original expired-fixture subjects");
 auto second=endpoint.native([](auto& b){for(const auto& row:b.inspect())if(row.entry==2)return row.job;throw std::runtime_error("Actual expired-fixture second job");});auto proof=endpoint.native([&](auto& b){return b.producerRefused(2,second);});Wire ack;auto command=ack.text("kind","acknowledge").begin("job").job(second).end().counter("sequence",proof.receipts.back().sequence.value).finish();check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,"family:22",command.c_str(),&error) && !error,"Original producer proof and ACK return actual expired-fixture capacity");
 check(warlock_imported_clients_enroll(owner,popup,23,1,1,&result,&events,&error) && result==WARLOCK_IMPORTED_EXPIRED && std::string_view(events)=="[]" && !error && endpoint.native([](auto& b){return b.requestFloor(3)==0 && b.recordCount()==1 && b.charge()==4096;}),"Real C retry after original two-second cutoff cannot issue when capacity returns");g_free(events);events=nullptr;
 auto rows=endpoint.native([](auto& b){return b.inspect();});for(const auto& row:rows){auto proof=endpoint.native([&](auto& b){return b.producerRefused(row.entry,row.job);});Wire ack;auto command=ack.text("kind","acknowledge").begin("job").job(row.job).end().counter("sequence",proof.receipts.back().sequence.value).finish();auto identity="family:"+std::to_string(row.job.context.incarnation.value);require(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity.c_str(),command.c_str(),&error) && !error,"Original expired-fixture cleanup");}
 check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"Expired C fixture drains exact original jobs without inventing third ownership");warlock_preview_bootstrap_free(bootstrap);expired.finish();
 }
 std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false,\"scope\":\"Actual C bridge and socket bootstrap; synthetic owning server scope, reserved jobs, original journal proof and ACK. No capture pixels, GIO retirement, compositor or ordinary eligible source acceptance.\"}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
