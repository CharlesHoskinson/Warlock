#include "preview_delivery.hpp"
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
    Wire out;out.integer("protocolVersion",3).text("kind",kind).begin("binding").binding(binding).end().counter("requestId",id).begin("scope").begin("binding").binding(binding).end().begin("context").context(context).end().counter("observation",UINT64_MAX).counter("clock",UINT64_MAX).counter("now",9007199254740993ULL).boolean("present",true).boolean("sourceLive",true).boolean("locked",false).boolean("gpuReady",true).end().counter("maximumTransferBytes",4096).boolean("previewEligible",false).text("scopeKind",source);
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
int main() {
    try {
        {Json json("{\"a\":{\"x\":1},\"b\":{\"x\":2},\"literal\":\"\\\\u0000\"}");check(std::string_view(Json::text(json.object(),"literal"))=="\\u0000","Valid repeated member names in distinct objects and escaped literal preserved");}
        check(denied([]{Json json("{\"a\":1,\"a\":2}");}),"Duplicate JSON refused");
        {Server server;auto native=server.open();auto binding=native->binding();check(binding.lifetime.value==UINT64_MAX && binding.frontend.value==9007199254740993ULL && binding.session.value==uint64_t(getpid()),"Lossless own process binding through actual socket, prefix and half-close");
            const auto enrolled=native->enrollment();check(enrolled.binding==binding && enrolled.providerPID==getpid() && enrolled.providerStart==processStart(getpid()) && enrolled.compositorPID==server.pid && enrolled.compositorStart==processStart(server.pid) && enrolled.executableSHA256==digest() && enrolled.coreABIMetadata=="fixture-ABI" && enrolled.operations[2]=="activate" && !enrolled.canonicalScene,"Typed enrollment retains verified owner, executable and admitted metadata");
            const auto observed=native->scope({UINT64_MAX});check(observed.scope.binding==binding && observed.scope.context.incarnation.value==UINT64_MAX && observed.scope.context.output.value==9007199254740993ULL && observed.observation==UINT64_MAX && observed.scope.now==9007199254740993ULL && observed.request==1 && observed.maximumTransferBytes==4096 && !observed.previewEligible,"Typed actual-socket scope preserves lossless counters and ineligible source");
            check(native->scope({UINT64_MAX}).request==2,"Native scope requests retain monotonically increasing correlation");
            auto client=native->clientScope({UINT64_MAX});check(client.request==3 && client.kind==SourceObservation::Kind::UnqualifiedClientMain && !client.previewEligible && client.scope.binding==binding && client.scope.context.incarnation.value==UINT64_MAX,"Client scope uses same own grant and explicit ineligible source type");
            check(denied([&]{native->scope({0});}),"Zero subject fails before native transport");
            auto child=fork();require(child>=0,"Inherited grant fork");if(!child)_exit(denied([&]{native->bindingJSON();}) && denied([&]{native->enrollment();}) && denied([&]{native->scope({UINT64_MAX});})?0:2);int status=0;require(waitpid(child,&status,0)==child,"Inherited child wait");check(WIFEXITED(status) && !WEXITSTATUS(status),"Inherited grant rejected in child process");
            int pipefd[2];require(pipe2(pipefd,O_CLOEXEC)==0,"Backend fixture pipe");child=fork();require(child>=0,"Backend child fork");if(!child){close(pipefd[0]);try{auto own=server.open();auto session=own->binding().session.value;write(pipefd[1],&session,sizeof(session));_exit(0);}catch(...){_exit(2);}}close(pipefd[1]);uint64_t backend{};fd::Owned pipe(pipefd[0]);require(read(pipe.get(),&backend,sizeof(backend))==sizeof(backend) && waitpid(child,&status,0)==child && WIFEXITED(status) && !WEXITSTATUS(status),"Backend own grant child normal exit");check(backend==uint64_t(child) && backend!=binding.session.value,"Provider grant separate from backend process grant");
            check(denied([&]{Native wrong(server.pid,processStart(server.pid)+1,server.root.string(),"fixture",digest());}),"Wrong process start refused");
            check(denied([&]{Native wrong(server.pid,processStart(server.pid),server.root.string(),"fixture",std::string(64,'0'));}),"Wrong executable hash refused");
            check(denied([&]{Native wrong(getpid(),processStart(getpid()),server.root.string(),"fixture",digest());}),"Different actual socket peer refused");
            check(denied([&]{native->control(std::string(4097,'x'));}),"Outgoing request bounded before transport");
            auto config=server.config();GError* error=nullptr;auto owner=warlock_preview_bootstrap_open(config.c_str(),&error);check(owner && !error,"Actual C bootstrap owns native grant");char* json=nullptr;check(warlock_preview_bootstrap_binding(owner,&json,&error) && json && !error,"C bootstrap returns owned binding");{Json actual(json);check(decimal(Json::text(actual.object(),"session"))==uint64_t(getpid()) && decimal(Json::text(actual.object(),"frontend"))==binding.frontend.value+1,"C bootstrap has fresh own process frontend epoch");}g_free(json);json=nullptr;
            auto transport=static_cast<Native*>(warlock_preview_bootstrap_native_transport(owner,&error));check(transport && !error && transport->binding().frontend.value==binding.frontend.value+1,"Borrowed native transport retains bootstrap grant without second hello");
            check(warlock_preview_bootstrap_enrollment(owner,&json,&error) && json && !error,"Actual C typed enrollment serializes admitted native facts");{Json actual(json);auto root=actual.object();auto provider=Json::child(root,"provider");auto core=Json::child(root,"compositor");check(Json::integer(provider,"pid")==getpid() && decimal(Json::text(provider,"start"))==processStart(getpid()) && std::string_view(Json::text(core,"executableSHA256"))==digest() && !Json::boolean(root,"loadedPluginAttested"),"C enrollment preserves provider owner and distinguishes core hash from plugin attestation");}g_free(json);json=nullptr;
            check(warlock_preview_bootstrap_scope(owner,UINT64_MAX,&json,&error) && json && !error,"Actual C scope fetch succeeds");{Json actual(json);check(!Json::boolean(actual.object(),"previewEligible") && decimal(Json::text(Json::child(Json::child(actual.object(),"scope"),"context"),"incarnation"))==UINT64_MAX,"C scope never upgrades unqualified pixels and preserves uint64 subject");}g_free(json);json=nullptr;
            check(warlock_preview_bootstrap_client_scope(owner,UINT64_MAX,&json,&error) && json && !error,"Actual C client scope fetch succeeds");{Json actual(json);check(std::string_view(Json::text(actual.object(),"kind"))=="preview-client-scope" && std::string_view(Json::text(actual.object(),"scopeKind"))=="isolated-root-client-unqualified" && !Json::boolean(actual.object(),"previewEligible"),"C client observation remains separate from monitor and ineligible");}g_free(json);json=nullptr;
            child=fork();require(child>=0,"C grant inherited fork");if(!child){GError* inherited=nullptr;char* bytes=nullptr;const auto refused=!warlock_preview_bootstrap_enrollment(owner,&bytes,&inherited) && inherited && !bytes;g_clear_error(&inherited);_exit(refused?0:2);}require(waitpid(child,&status,0)==child,"C inherited wait");check(WIFEXITED(status) && !WEXITSTATUS(status),"C typed enrollment rejects inherited foreign process");
            // Synthetic native CPU subject only: the observed monitor probe is
            // never enrolled as eligible capture source by this fixture.
            preview::Binding own;{char* bytes=nullptr;require(warlock_preview_bootstrap_binding(owner,&bytes,&error),"C delivery owner binding");Json parsed(bytes);own=decodeBinding(parsed.object());g_free(bytes);}
            preview::Scope subject{own,{{own.lifetime.value},{UINT64_MAX},{1},{2},{3},{4},{5}},own.lifetime.value?preview::Id<preview::Clock>{own.lifetime.value}:preview::Id<preview::Clock>{1},1,true,true,false,true};
            preview::uri::Endpoint endpoint({2,4,1,32},1,1,[&](uint64_t)->std::optional<preview::uri::NativeTime>{return preview::uri::NativeTime{subject.clock,subject.now};});
            preview::Job job{own,subject.context,{1},{2},subject.clock,20};auto popup=reinterpret_cast<gpointer>(uintptr_t(77));
            endpoint.native([&](auto& b){require(b.enroll(1,subject,32),"C fixture subject");require(b.acquire(1,own,job).status==preview::Result::Status::Admitted,"C fixture acquisition");});require(endpoint.registerView(77,own,{1}),"C fixture native receiver");
            check(!warlock_preview_bootstrap_attach_delivery(owner,&endpoint,reinterpret_cast<gpointer>(uintptr_t(88)),&error) && error,"C delivery refuses unenrolled native popup");g_clear_error(&error);
            check(warlock_preview_bootstrap_attach_delivery(owner,&endpoint,popup,&error) && !error,"C bootstrap attaches actual Broker journal delivery");
            check(!warlock_preview_bootstrap_attach_delivery(owner,&endpoint,popup,&error) && error,"C delivery enrollment cannot be replaced");g_clear_error(&error);
            check(warlock_preview_bootstrap_pending(owner,popup,&json,&error) && !error && std::string_view(json)=="[]","C delivery cannot invent proof for active capture");g_free(json);json=nullptr;
            auto terminal=endpoint.native([&](auto& b){return b.producerRefused(1,job);});
            check(warlock_preview_bootstrap_pending(owner,popup,&json,&error) && !error && std::string_view(json)!="[]" && endpoint.native([](auto& b){return b.recordCount();})==1,"C delivery leaves actual terminal journal retained");g_free(json);json=nullptr;
            Wire command;auto encoded=command.text("kind","acknowledge").begin("job").job(job).end().counter("sequence",terminal.receipts.back().sequence.value).finish();
            check(!warlock_preview_bootstrap_acknowledge(owner,popup,"family:1",encoded.c_str(),&error) && error,"C wrong family acknowledgement refused");g_clear_error(&error);
            check(warlock_preview_bootstrap_acknowledge(owner,popup,"family:18446744073709551615",encoded.c_str(),&error) && !error && endpoint.native([](auto& b){return b.recordCount();})==0,"C exact final acknowledgement reclaims physical Broker journal");
            auto additional=subject;additional.context.incarnation={UINT64_MAX-1};preview::Job added{own,additional.context,{1},{2},additional.clock,20};
            endpoint.native([&](auto& b){require(b.enroll(2,additional,32),"Additional C native subject");require(b.acquire(2,own,added).status==preview::Result::Status::Admitted,"Additional original C job");});
            check(endpoint.extendView(77,own,{2}),"C receiver pixel membership grows");auto addedTerminal=endpoint.native([&](auto& b){return b.producerRefused(2,added);});
            Wire addedCommand;auto addedEncoded=addedCommand.text("kind","acknowledge").begin("job").job(added).end().counter("sequence",addedTerminal.receipts.back().sequence.value).finish();
            check(warlock_preview_bootstrap_pending(owner,popup,&json,&error) && !error && std::string_view(json)=="[]","C view growth cannot silently enroll terminal subjects");g_free(json);json=nullptr;
            check(!warlock_preview_bootstrap_acknowledge(owner,popup,"family:18446744073709551614",addedEncoded.c_str(),&error) && !error,"C new ACK waits for explicit native journal extension");
            check(!warlock_preview_bootstrap_extend_delivery(owner,reinterpret_cast<gpointer>(uintptr_t(88)),&error) && error,"C foreign receiver cannot extend journal subjects");g_clear_error(&error);
            check(warlock_preview_bootstrap_extend_delivery(owner,popup,&error) && !error,"C explicit own native journal membership extension");
            check(warlock_preview_bootstrap_pending(owner,popup,&json,&error) && !error && std::string_view(json)!="[]" && endpoint.native([](auto& b){return b.recordCount();})==1,"C extension delivers retained original new terminal proof");g_free(json);json=nullptr;
            check(warlock_preview_bootstrap_acknowledge(owner,popup,"family:18446744073709551614",addedEncoded.c_str(),&error) && !error && endpoint.native([](auto& b){return b.recordCount();})==0,"C exact new final ACK uses original retained journal");
            child=fork();require(child>=0,"C extension inherited fork");if(!child){GError* inherited=nullptr;const auto refused=!warlock_preview_bootstrap_extend_delivery(owner,popup,&inherited) && inherited;g_clear_error(&inherited);_exit(refused?0:2);}require(waitpid(child,&status,0)==child,"C extension inherited wait");check(WIFEXITED(status) && !WEXITSTATUS(status),"C journal extension rejects inherited foreign process");
            warlock_preview_bootstrap_free(owner);
            chmod(config.c_str(),0644);owner=warlock_preview_bootstrap_open(config.c_str(),&error);check(!owner && error,"Public enrollment file refused");g_clear_error(&error);chmod(config.c_str(),0600);
            fs::create_symlink(config,server.root/"config-link");owner=warlock_preview_bootstrap_open((server.root/"config-link").c_str(),&error);check(!owner && error,"Symlink enrollment file refused");g_clear_error(&error);
            fs::create_hard_link(config,server.root/"hard-link");owner=warlock_preview_bootstrap_open(config.c_str(),&error);check(!owner && error,"Multiply linked enrollment file refused");g_clear_error(&error);fs::remove(server.root/"hard-link");
            std::ifstream file(config);std::string bytes((std::istreambuf_iterator<char>(file)),{});bytes.insert(1,"\"pid\":1,");server.config(bytes);owner=warlock_preview_bootstrap_open(config.c_str(),&error);check(!owner && error,"Duplicate config field refused");g_clear_error(&error);
            server.config();chmod(server.root.c_str(),0755);check(denied([&]{server.open();}),"Nonprivate runtime refused");chmod(server.root.c_str(),0700);
            fs::create_directory_symlink(server.root,server.root/"alias");check(denied([&]{Native wrong(server.pid,processStart(server.pid),(server.root/"alias").string(),"fixture",digest());}),"Symlink directory ancestor refused");
            check(denied([&]{Native wrong(server.pid,processStart(server.pid),server.root.string()+"/..", "fixture",digest());}),"Parent directory component refused");
            check(denied([&]{Native wrong(server.pid,processStart(server.pid),server.root.string(),"../fixture",digest());}),"Noncanonical instance refused");server.finish();}
        for(const std::string mode:{"version","bool-version","float-version","duplicate","escaped-duplicate","nested-duplicate","nul","zero","leading-zero","overflow","numeric-counter","wrong-pid","float-pid","wrong-instance","extra","wrong-caps","wrong-operations","bad-fd","oversized","raw-nul","replace-socket","replace-directory"}) {Server server(mode);check(denied([&]{server.open();}),mode.c_str());server.finish();}
        {Server server("slow");auto before=std::chrono::steady_clock::now();bool stopped=denied([&]{server.open();});double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-before).count();check(stopped && seconds>=2.8 && seconds<4.5,"Dripping reply cannot restart original absolute three-second deadline");server.finish();}
        for(const std::string mode:{"scope-kind","scope-request","scope-binding","scope-inner-binding","scope-subject","scope-lifetime","scope-clock","scope-zero","scope-float","scope-numeric","scope-bool","scope-extra","scope-context-extra","scope-duplicate","scope-eligible","scope-source-kind","scope-cost"}) {Server server(mode);auto native=server.open();check(denied([&]{native->scope({UINT64_MAX});}),mode.c_str());server.finish();}
        for(const std::string mode:{"scope-kind","scope-request","scope-binding","scope-inner-binding","scope-subject","scope-lifetime","scope-clock","scope-zero","scope-float","scope-numeric","scope-bool","scope-extra","scope-context-extra","scope-duplicate","scope-eligible","scope-source-kind","scope-cost"}) {Server server(mode);auto native=server.open();check(denied([&]{native->clientScope({UINT64_MAX});}),("client-"+mode).c_str());server.finish();}
        {Server server("scope-slow");auto native=server.open();auto before=std::chrono::steady_clock::now();const bool stopped=denied([&]{native->scope({UINT64_MAX});});const auto seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-before).count();check(stopped && seconds>=2.8 && seconds<4.5,"Scope drip cannot reset original three-second transport budget");server.finish();}
        {Server server("quoted-abi");GError* error=nullptr;auto owner=warlock_preview_bootstrap_open(server.config().c_str(),&error);char* json=nullptr;check(owner && !error && warlock_preview_bootstrap_enrollment(owner,&json,&error),"Quoted ABI native metadata admitted through C API");{Json actual(json);check(std::string_view(Json::text(Json::child(actual.object(),"compositor"),"coreABIMetadata"))=="fixture-ABI\"\\tail","C enrollment correctly escapes quote and backslash metadata");}g_free(json);warlock_preview_bootstrap_free(owner);server.finish();}
        std::cout<<"CHECKS "<<passed<<"\n";return 0;
    }catch(const std::exception& e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}
}
