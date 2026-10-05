#pragma once
#include "preview_fd.hpp"
#include <json-glib/json-glib.h>
#include <atomic>
#include <charconv>
#include <fstream>
#include <sstream>

namespace preview::bridge {
inline void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
inline uint64_t decimal(std::string_view text) {
    uint64_t value=0;auto result=std::from_chars(text.data(),text.data()+text.size(),value);
    require(!text.empty() && text.front()!='0' && result.ec==std::errc{} && result.ptr==text.data()+text.size() && value,"Canonical positive native counter");return value;
}
struct Json {
    JsonParser* parser;
    explicit Json(std::string_view text):parser(json_parser_new()) {
        if(text.size()>65536 || !json_parser_load_from_data(parser,text.data(),text.size(),nullptr) || !JSON_NODE_HOLDS_OBJECT(json_parser_get_root(parser))) {
            g_object_unref(parser);throw std::runtime_error("Native JSON reply");
        }
    }
    ~Json(){if(parser)g_object_unref(parser);}
    Json(const Json&)=delete;Json& operator=(const Json&)=delete;
    Json(Json&& value):parser(std::exchange(value.parser,nullptr)){}
    JsonObject* object() const{return json_node_get_object(json_parser_get_root(parser));}
    static const char* text(JsonObject* object,const char* name) {
        auto node=json_object_get_member(object,name);require(node && JSON_NODE_HOLDS_VALUE(node) && json_node_get_value_type(node)==G_TYPE_STRING,"Native string field");return json_node_get_string(node);
    }
    uint64_t counter(const char* name) const{return decimal(text(object(),name));}
};
class Native {
    pid_t pid_;uint64_t start_;std::string runtime_,instance_;struct stat executable_{};
    std::atomic_uint64_t request_{1};
    std::string fdAddress_;
    uint64_t lifetime_{},session_{},frontend_{};
    uint64_t startTime() const {
        std::ifstream file("/proc/"+std::to_string(pid_)+"/stat");std::string line;std::getline(file,line);auto close=line.rfind(')');require(close!=line.npos,"Native process stat");std::istringstream fields(line.substr(close+1));std::string word;for(unsigned i=0;i<20;++i)require(bool(fields>>word),"Native start ticks");return decimal(word);
    }
    void current() const {
        struct stat actual{};require(startTime()==start_ && ::stat(("/proc/"+std::to_string(pid_)+"/exe").c_str(),&actual)==0,"Native process still current");
        require(actual.st_dev==executable_.st_dev && actual.st_ino==executable_.st_ino && actual.st_size==executable_.st_size && actual.st_mtim.tv_sec==executable_.st_mtim.tv_sec && actual.st_mtim.tv_nsec==executable_.st_mtim.tv_nsec,"Native executable identity unchanged");
    }
    fd::Owned connect(const sockaddr_un& address,socklen_t length,int type) const {
        current();fd::Owned socket(::socket(AF_UNIX,type|SOCK_CLOEXEC,0));require(bool(socket),"Native connection socket");timeval timeout{3,0};
        require(setsockopt(socket.get(),SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout))==0 && setsockopt(socket.get(),SOL_SOCKET,SO_SNDTIMEO,&timeout,sizeof(timeout))==0,"Original three-second IPC timeout");
        require(::connect(socket.get(),reinterpret_cast<const sockaddr*>(&address),length)==0,"Native socket connects");ucred peer{};socklen_t size=sizeof(peer);
        require(getsockopt(socket.get(),SOL_SOCKET,SO_PEERCRED,&peer,&size)==0 && size==sizeof(peer) && peer.pid==pid_ && peer.uid==getuid(),"Exact native socket peer");current();return socket;
    }
public:
    Native(pid_t pid,uint64_t start,std::string runtime,std::string instance,std::string expectedSHA):pid_(pid),start_(start),runtime_(std::move(runtime)),instance_(std::move(instance)) {
        require(pid>0 && start>0 && expectedSHA.size()==64,"Native launch enrollment");
        fd::Owned image(::open(("/proc/"+std::to_string(pid_)+"/exe").c_str(),O_RDONLY|O_CLOEXEC));require(image && fstat(image.get(),&executable_)==0 && S_ISREG(executable_.st_mode),"Actual native executable");
        auto digest=g_checksum_new(G_CHECKSUM_SHA256);std::array<uint8_t,8192> bytes{};
        for(;;){const auto n=read(image.get(),bytes.data(),bytes.size());if(n<0 && errno==EINTR)continue;require(n>=0,"Native executable hash read");if(!n)break;g_checksum_update(digest,bytes.data(),n);}
        const bool matches=expectedSHA==g_checksum_get_string(digest);g_checksum_free(digest);require(matches,"Exact owning core hash");current();
        auto hello=control("{\"protocolVersion\":3,\"kind\":\"hello\"}");require(std::string_view(Json::text(hello.object(),"kind"))=="attached","Native grant attached");
        auto binding=json_object_get_object_member(hello.object(),"binding");require(binding!=nullptr,"Native grant binding");lifetime_=decimal(Json::text(binding,"lifetime"));session_=decimal(Json::text(binding,"session"));frontend_=decimal(Json::text(binding,"frontend"));fdAddress_=Json::text(hello.object(),"previewFdAddress");
        auto compositor=json_object_get_object_member(hello.object(),"compositor");require(compositor && json_object_get_int_member(compositor,"pid")==pid_ && std::string_view(Json::text(compositor,"instance"))==instance_,"Native hello owning instance");
    }
    Binding binding() const{return {{lifetime_},{session_},{frontend_}};}
    uint64_t next(){auto value=request_.load();for(;;){require(value>0 && value<UINT64_MAX,"Native request counter not exhausted");if(request_.compare_exchange_weak(value,value+1))return value;}}
    std::string bindingJSON() const {return "{\"lifetime\":\""+std::to_string(lifetime_)+"\",\"session\":\""+std::to_string(session_)+"\",\"frontend\":\""+std::to_string(frontend_)+"\"}";}
    Json control(const std::string& body) const {
        const auto path=runtime_+"/hypr/"+instance_+"/.socket.sock";require(path.size()<sizeof(sockaddr_un::sun_path),"Native control path bound");
        struct stat before{};require(lstat(path.c_str(),&before)==0 && S_ISSOCK(before.st_mode) && before.st_uid==getuid(),"Native control socket identity");
        sockaddr_un address{};address.sun_family=AF_UNIX;memcpy(address.sun_path,path.c_str(),path.size()+1);auto socket=connect(address,static_cast<socklen_t>(offsetof(sockaddr_un,sun_path)+path.size()+1),SOCK_STREAM);
        const std::string wire="elm_observe "+body;size_t offset=0;while(offset<wire.size()){const auto n=send(socket.get(),wire.data()+offset,wire.size()-offset,MSG_NOSIGNAL);if(n<0 && errno==EINTR)continue;require(n>0,"Native control write");offset+=n;}
        std::string text;std::array<char,4096> bytes{};for(;;){const auto n=recv(socket.get(),bytes.data(),bytes.size(),0);if(n<0 && errno==EINTR)continue;require(n>=0,"Native control receive");if(!n)break;require(text.size()+n<=65536,"Native metadata reply bound");text.append(bytes.data(),n);}
        struct stat after{};require(lstat(path.c_str(),&after)==0 && before.st_dev==after.st_dev && before.st_ino==after.st_ino,"Native control socket not replaced");current();return Json(text);
    }
    Json request(const char* kind,const std::string& fields="") {return control("{\"protocolVersion\":3,\"kind\":\""+std::string(kind)+"\",\"binding\":"+bindingJSON()+",\"requestId\":\""+std::to_string(next())+"\""+fields+"}");}
    std::optional<fd::Received<fd::Count>> query(fd::Operation op,uint64_t capture,uint64_t subject,uint64_t transfer=0) {
        const auto [address,length]=fd::address(fdAddress_);auto socket=connect(address,length,SOCK_SEQPACKET);
        fd::Query query{fd::MAGIC,1,op,lifetime_,session_,frontend_,next(),capture,subject,transfer};require(fd::send(socket.get(),query),"Native image request send");
        auto reply=fd::receive<fd::Count>(socket.get(),op==fd::Get?1:0);current();
        if(!reply || !fd::matches(reply->words,query))return {};
        return reply;
    }
    std::optional<uri::NativeTime> time(const fd::Header& frame) noexcept {
        try {
            auto observed=query(fd::Observe,frame[fd::Capture],frame[fd::Subject],frame[fd::Transfer]);if(!observed)return {};
            const auto& h=observed->words;
            if(!fd::imageHeader(h) || !(h[fd::Flags]&fd::Present) || h[fd::Lifetime]!=frame[fd::Lifetime] || h[fd::Output]!=frame[fd::Output] || h[fd::Privacy]!=frame[fd::Privacy] || h[fd::Rendering]!=frame[fd::Rendering] || h[fd::Now]<frame[fd::Now] || h[fd::Now]>=frame[fd::Expires])return {};
            return uri::NativeTime{{h[fd::Lifetime]},h[fd::Now]};
        }catch(...){return {};}
    }
};
}
