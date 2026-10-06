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
int main(int argc,char** argv){try{
 const std::string mode=argc>1?argv[1]:"normal";Server server(mode);GError* error=nullptr;auto bootstrap=warlock_preview_bootstrap_open(server.config().c_str(),&error);check(bootstrap && !error,"Own resume native C bootstrap");
 auto transport=warlock_preview_bootstrap_native_transport(bootstrap,&error);auto popup=reinterpret_cast<gpointer>(uintptr_t(77));char* events=nullptr;void* raw=nullptr;
 auto owner=warlock_imported_clients_open_dynamic(transport,popup,21,1,1,&events,&raw,&error);check(owner && events && raw && !error,"Original resume C source");g_free(events);events=nullptr;
 auto& endpoint=*static_cast<preview::uri::Endpoint*>(raw);WarlockImportedAdmission admission;
 auto enroll=[&](uint64_t subject){check(warlock_imported_clients_enroll(owner,popup,subject,1,1,&admission,&events,&error) && admission==WARLOCK_IMPORTED_STARTED && !error,"Own unrelated C reservation");g_free(events);events=nullptr;};
 enroll(22);check(warlock_preview_bootstrap_attach_delivery(bootstrap,raw,popup,&error) && !error,"Original C resume journal");
 auto getJob=[&](uint64_t entry){return endpoint.native([&](auto& b){for(const auto& row:b.inspect())if(row.entry==entry)return row.job;throw std::runtime_error("Owned original job");});};
 auto settle=[&](uint64_t entry){auto job=getJob(entry);auto proof=endpoint.native([&](auto& b){return b.producerRefused(entry,job);});Wire ack;auto message=ack.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",proof.receipts.back().sequence.value).finish();auto identity="family:"+std::to_string(job.context.incarnation.value);check(warlock_preview_bootstrap_acknowledge(bootstrap,popup,identity.c_str(),message.c_str(),&error) && !error,"Actual original final proof and exact C ACK");};
 const auto prior=getJob(1);
 check(warlock_imported_clients_resume_at(owner,"family:21",2,2,&admission,&events,&error) && admission==WARLOCK_IMPORTED_INVALID && std::string_view(events)=="[]" && !error,"Existing actual record prevents resume and intent");g_free(events);events=nullptr;
 settle(1);enroll(23);check(warlock_preview_bootstrap_extend_delivery(bootstrap,popup,&error) && !error,"Explicit same journal membership extension");
 if(mode=="replace-receiver"){
  auto view=*endpoint.registeredView(77);endpoint.unregisterView(77);check(endpoint.registerView(77,view.binding,view.entries),"Receiver replacement epoch");
  auto* native=static_cast<Native*>(transport);const auto before=native->clientScope({21});
  check(!warlock_imported_clients_resume_at(owner,"family:21",2,2,&admission,&events,&error) && error && !events,"Replaced receiver refuses typed C resume");g_clear_error(&error);
  const auto after=native->clientScope({21});check(after.request==before.request+1,"Receiver refusal occurs before any native scope query");
  check(endpoint.native([](auto& b){return b.requestFloor(1)==1 && b.recordCount()==2 && b.charge()==8192;}),"Receiver loss retains other actual jobs and own floor");
  // Original UI receipt receiver is intentionally gone. Owned physical cleanup
  // and exact native ACK remain possible; no record reset or invented UI ACK.
  endpoint.native([](auto& b){for(const auto& row:b.inspect()){auto proof=b.producerRefused(row.entry,row.job);require(b.acknowledge(row.entry,row.job.binding,row.job,proof.receipts.back().sequence),"Owned stale receiver native settlement");}});
 }else{
  bool foreignAccepted=true;std::thread foreign([&]{GError* deniedError=nullptr;char* ignored=nullptr;WarlockImportedAdmission deniedAdmission;foreignAccepted=warlock_imported_clients_resume_at(owner,"family:21",2,2,&deniedAdmission,&ignored,&deniedError);check(!foreignAccepted && deniedError && !ignored,"Foreign thread cannot admit resume");g_clear_error(&deniedError);});foreign.join();check(!foreignAccepted,"Creator thread guard retained");
  check(warlock_imported_clients_resume_at(owner,"family:21",2,2,&admission,&events,&error) && admission==WARLOCK_IMPORTED_CAPACITY && std::string_view(events)=="[]" && !error,"Actual resume Capacity has no issued job or proof");g_free(events);events=nullptr;
  check(warlock_imported_clients_status(owner,&events,&error) && !error,"Retained resume intent status");std::string snapshot(events);g_free(events);events=nullptr;
  auto marker=snapshot.find("\"resumeDeadline\":\"");check(marker!=snapshot.npos,"Original cutoff discoverable without fake job");marker+=18;auto end=snapshot.find('"',marker);auto deadline=decimal(std::string_view(snapshot).substr(marker,end-marker));
  check(endpoint.native([](auto& b){return b.requestFloor(1)==1 && b.recordCount()==2 && b.nextProofSequence()==2;}),"Local Capacity does not advance floor or terminal sequence");
  if(mode!="resume-expire"){
   check(warlock_imported_clients_resume_at(owner,"family:21",3,2,&admission,&events,&error) && admission==WARLOCK_IMPORTED_CONFLICT && std::string_view(events)=="[]" && !error,"Changed pending publication conflicts");g_free(events);events=nullptr;
  }
  settle(3);
  if(mode=="reject")check(endpoint.native([](auto& b){auto incoherent=b.nativeScope(1);incoherent.context.privacy={1};return !b.observe(1,incoherent,4096);}),"Actual retained Broker incoherence");
  check(warlock_imported_clients_resume_at(owner,"family:21",2,2,&admission,&events,&error) && !error,"Actual typed resume retry");
  if(mode=="resume-expire"){
   check(admission==WARLOCK_IMPORTED_EXPIRED && std::string_view(events)=="[]" && endpoint.native([](auto& b){return b.requestFloor(1)==1 && b.recordCount()==1;}),"Capacity returning after original cutoff cannot revive intent");g_free(events);events=nullptr;
  }else{
   check(admission==(mode=="reject"?WARLOCK_IMPORTED_NATIVE_REJECTED:WARLOCK_IMPORTED_STARTED) && std::string_view(events)!="[]","Real issued resume job registers before any proof");std::string registration(events);g_free(events);events=nullptr;
   const auto job=getJob(1);check(job.deadline==deadline && job.request.value==2 && prior.request.value==1 && job.binding==prior.binding,"Exact resumed job keeps original cutoff and monotonic identity");
   if(mode=="reject"){
    check(warlock_preview_bootstrap_pending(bootstrap,popup,&events,&error) && !error,"Actual resumed rejection proof discoverable");std::string receipts(events);g_free(events);events=nullptr;Wire w;
    std::cout<<"{\"registration\":"<<registration<<",\"receipts\":"<<receipts<<",\"job\":"<<w.job(job).finish()<<",\"identity\":\"family:21\",\"nativeAcceptance\":false,\"fullReleaseAccepted\":false}"<<std::endl;
    std::string request;bool acquired=false,settled=false;
    while(std::getline(std::cin,request)){
     Json value(request);auto kind=std::string_view(Json::text(value.object(),"kind"));bool accepted=false;std::string emitted="[]";
     if(kind=="acquire"){check(!acquired && !settled,"One actual Elm resume acquire");acquired=true;accepted=warlock_imported_clients_command(owner,"family:21",request.c_str(),&events,&error);check(accepted && !error && std::string_view(events)=="[]","Rejected resume suppresses capture");emitted=events;g_free(events);events=nullptr;}
     else{require(kind=="acknowledge","Exact actual Elm ACK");accepted=warlock_preview_bootstrap_acknowledge(bootstrap,popup,"family:21",request.c_str(),&error);check(!error,"Own resume terminal result");if(accepted)settled=true;}
     const auto counters=endpoint.native([](auto& b){return std::pair{b.recordCount(),b.requestFloor(1)};});check(counters.second==2,"Resume floor never reset");
     std::cout<<"{\"accepted\":"<<(accepted?"true":"false")<<",\"events\":"<<emitted<<",\"records\":"<<counters.first<<",\"floor\":"<<counters.second<<"}"<<std::endl;
    }
    check(acquired && settled,"Actual optimized Elm resume job settled");
   }else settle(1);
  }
  settle(2);
 }
 check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"Exact original cleanup and C close");warlock_preview_bootstrap_free(bootstrap);server.finish();
 if(mode!="reject")std::cout<<"{\"passed\":true,\"checks\":"<<passed<<",\"nativeAcceptance\":false,\"mode\":\""<<mode<<"\"}"<<std::endl;
 return 0;
}catch(const std::exception& exception){std::cerr<<exception.what()<<'\n';return 1;}}
