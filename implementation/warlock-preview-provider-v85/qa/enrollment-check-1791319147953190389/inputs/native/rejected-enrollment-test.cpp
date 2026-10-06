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
 Server server;GError* error=nullptr;auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);check(bootstrap && !error,"Own native C bootstrap");
 auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);auto popup=reinterpret_cast<gpointer>(uintptr_t(77));char* events=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open_dynamic(transport,popup,21,1,1,&events,&raw,&error);check(owner && events && raw && !error,"Original C reservation");g_free(events);events=nullptr;
 auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);WarlockImportedAdmission admission;
 check(warlock_imported_clients_enroll(owner,popup,22,1,1,&admission,&events,&error) && admission==WARLOCK_IMPORTED_STARTED && !error,"Second actual reservation");g_free(events);events=nullptr;
 check(warlock_imported_clients_enroll(owner,popup,23,1,1,&admission,&events,&error) && admission==WARLOCK_IMPORTED_CAPACITY && std::string_view(events)=="[]" && !error,"Original waiting intent has no proof or job");g_free(events);events=nullptr;
 check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Explicit own original journal");
 auto second=endpoint.native([](auto& b){for(const auto& row:b.inspect())if(row.entry==2)return row.job;throw std::runtime_error("Second native job");});
 auto proof=endpoint.native([&](auto& b){return b.producerRefused(2,second);});Wire ack;auto message=ack.text("kind","acknowledge").begin("job").job(second).end().counter("sequence",proof.receipts.back().sequence.value).finish();check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,"family:22",message.c_str(),&error) && !error,"Actual original producer proof and ACK return capacity");
 // Controlled authenticated-observation fault: the real Broker retains its
 // incoherent-actor refusal even after a later correctly typed observation.
 // No terminal proof is fabricated by the test or local admission API.
 check(endpoint.native([](auto& b){auto wrong=b.nativeScope(3);wrong.context.privacy={1};return !b.observe(3,wrong,4096);}),"Actual incoherent native actor retained");
 check(warlock_imported_clients_enroll(owner,popup,23,1,1,&admission,&events,&error) && admission==WARLOCK_IMPORTED_NATIVE_REJECTED && events && std::string_view(events)!="[]" && !error,"Actual C reservation returns known rejected job registration");std::string registration(events);g_free(events);events=nullptr;
 auto job=endpoint.native([](auto& b){for(const auto& row:b.inspect())if(row.entry==3){require(row.terminal && !row.proofs.empty() && row.proofs.front().kind==preview::Receipt::Kind::Refused,"Actual retained native Refused proof");return row.job;}throw std::runtime_error("Actual refused C job");});
 check(warlock_preview_bootstrap_pending(bootstrap,popup,&events,&error) && events && std::string_view(events)!="[]" && !error,"Original actual C terminal proof discoverable");std::string receipts(events);g_free(events);events=nullptr;
 Wire w;auto jobJSON=w.job(job).finish();std::cout<<"{\"registration\":"<<registration<<",\"receipts\":"<<receipts<<",\"job\":"<<jobJSON<<",\"identity\":\"family:23\",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}"<<std::endl;
 std::string request;bool acquired=false,settled=false;
 while(std::getline(std::cin,request)) {
  Json value(request);auto kind=std::string_view(Json::text(value.object(),"kind"));bool accepted=false;std::string emitted="[]";
  if(kind=="acquire") {
   check(!acquired && !settled,"One actual Elm acquire for retained rejected job");acquired=true;
   accepted=warlock_imported_clients_command(owner,"family:23",request.c_str(),&events,&error);check(accepted && events && std::string_view(events)=="[]" && !error,"Rejected job cannot replay native capture");emitted=events;g_free(events);events=nullptr;
  }else {
   require(kind=="acknowledge","Actual Elm terminal ACK only");accepted=warlock_preview_bootstrap_acknowledge(bootstrap,popup,"family:23",request.c_str(),&error);check(!error,"Exact own C receipt result");if(accepted)settled=true;
  }
  const auto counters=endpoint.native([](auto& b){return std::pair{b.recordCount(),b.requestFloor(3)};});
  check(counters.second==1,"Rejected original request floor never resets");
  std::cout<<"{\"accepted\":"<<(accepted?"true":"false")<<",\"events\":"<<emitted<<",\"records\":"<<counters.first<<",\"floor\":"<<counters.second<<"}"<<std::endl;
 }
 check(acquired && settled,"Actual optimized Elm acquire and final ACK observed");
 const auto remaining=endpoint.native([](auto& b){return b.inspect();});check(remaining.size()==1 && remaining.front().entry==1,"Exact rejected ACK retains the original other job");
 for(const auto& row:remaining){auto proof=endpoint.native([&](auto& b){return b.producerRefused(row.entry,row.job);});Wire ack;auto command=ack.text("kind","acknowledge").begin("job").job(row.job).end().counter("sequence",proof.receipts.back().sequence.value).finish();auto identity="family:"+std::to_string(row.job.context.incarnation.value);check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity.c_str(),command.c_str(),&error) && !error,"Original other job final settlement");}
 check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"No physical or journal ownership forgotten");warlock_preview_bootstrap_free(bootstrap);server.finish();return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
