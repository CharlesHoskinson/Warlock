#include "preview_retirement.hpp"
#include "capture-resources.hpp"
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
    std::string text="{\"protocolVersion\":3,\"kind\":\"attached\",\"binding\":{\"lifetime\":\"18446744073709551615\",\"session\":\""+std::to_string(peer)+"\",\"frontend\":\""+std::to_string(frontend)+"\"},\"previewFdAddress\":\"fixture_preview_"+std::to_string(core)+"\",\"compositor\":{\"pid\":"+std::to_string(core)+",\"instance\":\"fixture\",\"coreHash\":\"fixture-ABI\"},\"capabilities\":{\"observe\":true,\"effects\":true,\"minimizedState\":true,\"effectProtocol\":1,\"operations\":[\"minimize\",\"restore\",\"activate\"],\"canonicalScene\":false,\"taskbarProjectionProtocol\":1,\"effectInvalidationProtocol\":1}}";
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

struct ResourceImage {uint64_t charge()const{return 4096;}};
struct ResourceReservation {uint64_t bytes()const{return 4096;}};
struct ResourceExport {
    fd::Owned file{fd::seal(std::array<uint8_t,8>{137,80,78,71,13,10,26,10})};
    ResourceReservation reservation;uint64_t transfer{9007199254740995ULL};
};
struct ResourceProbe {
    uint64_t session{},frontend{},incarnation{},request{};
    bool client{true},popup{},family{},crop{},styled{},backdrop{};
    std::unique_ptr<ResourceImage> image{std::make_unique<ResourceImage>()};
    std::unique_ptr<ResourceExport> exported{std::make_unique<ResourceExport>()};
};

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
                bool running=true;std::map<pid_t,uint64_t> frontends;std::map<pid_t,ResourceProbe> captures;uint64_t resourceSequence=0;bool lostRelease=false,lostRetire=false;
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
                    else if(kind=="preview-client-scoped-request") {
                        auto object=envelope.object();Json::fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation","deadlineNs","context"});
                        const auto id=decimal(Json::text(object,"requestId")),subject=decimal(Json::text(object,"subjectIncarnation")),deadline=decimal(Json::text(object,"deadlineNs"));
                        const auto context=decodeContext(Json::child(object,"context"));const preview::Binding binding{{UINT64_MAX},{uint64_t(peer.pid)},{frontend}};
                        require(decodeBinding(Json::child(object,"binding"))==binding && context.incarnation.value==subject,"Original capture fixture grant and subject");
                        uint64_t count=0;std::ifstream(root/"capture-count")>>count;std::ofstream(root/"capture-count")<<count+1;
                        std::ofstream(root/"capture-wire.json")<<request.substr(14);
                        if(mode!="capture-refused") {
                            ResourceProbe probe;probe.session=peer.pid;probe.frontend=frontend;probe.incarnation=subject;probe.request=id;
                            captures.insert_or_assign(peer.pid,std::move(probe));
                            std::ofstream(root/"producer-count")<<1;std::ofstream(root/"export-count")<<1;
                        }
                        if(mode=="capture-refused")text="{\"protocolVersion\":3,\"kind\":\"refused\",\"reason\":\"fixture-capture-refused\"}";
                        else text=Wire().integer("protocolVersion",3).text("kind","preview-client-owned").begin("binding").binding(binding).end()
                            .counter("requestId",id).counter("subjectIncarnation",subject).counter("captureRequest",id).counter("outputGeneration",context.output.value)
                            .counter("completedNs",mode=="capture-malformed"?deadline:deadline-1).integer("width",1).integer("height",1)
                            .counter("encodedBytes",16).counter("ownedBytes",4096).text("crc32","0").text("encoding","PNG-RGBA8-straight")
                            .text("planeSpace","client-logical-unqualified").boolean("previewEligible",false).finish();
                    }
                    else if(kind=="preview-client-resource-state-request" || kind=="preview-client-resource-release-request" || kind=="preview-client-resource-retire-request") {
                        auto object=envelope.object();Json::fields(object,{"protocolVersion","kind","binding","requestId","captureRequest","subjectIncarnation","transfer"});
                        const preview::Binding binding{{UINT64_MAX},{uint64_t(peer.pid)},{frontend}};
                        require(Json::integer(object,"protocolVersion")==3 && decodeBinding(Json::child(object,"binding"))==binding,"Actual kernel peer and original resource fixture grant");
                        const auto id=decimal(Json::text(object,"requestId")),capture=decimal(Json::text(object,"captureRequest")),subject=decimal(Json::text(object,"subjectIncarnation"));
                        const std::string_view raw=Json::text(object,"transfer");const auto transfer=raw=="0"?0:decimal(raw);
                        const auto action=kind=="preview-client-resource-state-request"?preview::resources::Operation::Observe:
                            kind=="preview-client-resource-release-request"?preview::resources::Operation::ReleaseExport:preview::resources::Operation::RetireProducer;
                        const bool locked=fs::exists(root/"locked");
                        text=preview::resources::execute(captures,peer.pid,preview::resources::Binding{UINT64_MAX,uint64_t(peer.pid),frontend},
                            preview::resources::Target{capture,subject},id,9007199254740993ULL+id*1000000ULL,locked,action,transfer,resourceSequence,preview::resources::wire);
                        auto current=captures.find(peer.pid);std::ofstream(root/"producer-count")<<(current!=captures.end());
                        std::ofstream(root/"export-count")<<(current!=captures.end() && bool(current->second.exported));
                        uint64_t count=0;std::ifstream(root/"resource-count")>>count;std::ofstream(root/"resource-count")<<count+1;
                        if(mode=="resource-lost-release" && action==preview::resources::Operation::ReleaseExport && !lostRelease) {lostRelease=true;text="{";}
                        if(mode=="resource-lost-retire" && action==preview::resources::Operation::RetireProducer && !locked && !lostRetire) {lostRetire=true;text="{";}
                        if(fs::exists(root/"bad-resource-reply"))replace(text,"\"subjectIncarnation\":\""+std::to_string(subject)+"\"","\"subjectIncarnation\":\"1\"");
                    }
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
