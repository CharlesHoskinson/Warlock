#include "preview_client.hpp"
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
                    Json envelope(request.substr(14));require(std::string_view(Json::text(envelope.object(),"kind"))=="hello","Fixture strict hello");
                    auto& frontend=frontends[peer.pid];frontend=frontend?frontend+1:9007199254740993ULL;auto text=reply(getpid(),peer.pid,mode,frontend);
                    fd::Owned replacement;
                    if(mode=="replace-socket") {require(unlink(path.c_str())==0,"Fixture socket unlink");replacement=fd::Owned(::socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0));require(bind(replacement.get(),reinterpret_cast<sockaddr*>(&address),sizeof(address))==0,"Fixture replacement socket");}
                    if(mode=="replace-directory") {fs::rename(root/"hypr/fixture",root/"hypr/old");fs::create_directory(root/"hypr/fixture");chmod((root/"hypr/fixture").c_str(),0700);replacement=fd::Owned(::socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0));require(bind(replacement.get(),reinterpret_cast<sockaddr*>(&address),sizeof(address))==0,"Fixture replacement directory socket");}
                    if(mode=="slow") {
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
            auto child=fork();require(child>=0,"Inherited grant fork");if(!child)_exit(denied([&]{native->bindingJSON();})?0:2);int status=0;require(waitpid(child,&status,0)==child,"Inherited child wait");check(WIFEXITED(status) && !WEXITSTATUS(status),"Inherited grant rejected in child process");
            int pipefd[2];require(pipe2(pipefd,O_CLOEXEC)==0,"Backend fixture pipe");child=fork();require(child>=0,"Backend child fork");if(!child){close(pipefd[0]);try{auto own=server.open();auto session=own->binding().session.value;write(pipefd[1],&session,sizeof(session));_exit(0);}catch(...){_exit(2);}}close(pipefd[1]);uint64_t backend{};fd::Owned pipe(pipefd[0]);require(read(pipe.get(),&backend,sizeof(backend))==sizeof(backend) && waitpid(child,&status,0)==child && WIFEXITED(status) && !WEXITSTATUS(status),"Backend own grant child normal exit");check(backend==uint64_t(child) && backend!=binding.session.value,"Provider grant separate from backend process grant");
            check(denied([&]{Native wrong(server.pid,processStart(server.pid)+1,server.root.string(),"fixture",digest());}),"Wrong process start refused");
            check(denied([&]{Native wrong(server.pid,processStart(server.pid),server.root.string(),"fixture",std::string(64,'0'));}),"Wrong executable hash refused");
            check(denied([&]{Native wrong(getpid(),processStart(getpid()),server.root.string(),"fixture",digest());}),"Different actual socket peer refused");
            check(denied([&]{native->control(std::string(4097,'x'));}),"Outgoing request bounded before transport");
            auto config=server.config();GError* error=nullptr;auto owner=warlock_preview_bootstrap_open(config.c_str(),&error);check(owner && !error,"Actual C bootstrap owns native grant");char* json=nullptr;check(warlock_preview_bootstrap_binding(owner,&json,&error) && json && !error,"C bootstrap returns owned binding");{Json actual(json);check(decimal(Json::text(actual.object(),"session"))==uint64_t(getpid()) && decimal(Json::text(actual.object(),"frontend"))==binding.frontend.value+1,"C bootstrap has fresh own process frontend epoch");}g_free(json);warlock_preview_bootstrap_free(owner);
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
        std::cout<<"CHECKS "<<passed<<"\n";return 0;
    }catch(const std::exception& e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}
}
