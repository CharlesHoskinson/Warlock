#pragma once
#include "preview_fd.hpp"
#include "family_style_crop_fd.hpp"
#include "generated_backdrop_fd.hpp"
#include <json-glib/json-glib.h>
#include <atomic>
#include <charconv>
#include <fstream>
#include <sstream>
#include <chrono>
#include <poll.h>
#include <set>

namespace preview::bridge {
inline void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
inline uint64_t decimal(std::string_view text) {
    uint64_t value=0;auto result=std::from_chars(text.data(),text.data()+text.size(),value);
    require(!text.empty() && text.front()!='0' && result.ec==std::errc{} && result.ptr==text.data()+text.size() && value,"Canonical positive native counter");return value;
}
struct Json {
    JsonParser* parser;
    struct Admission {std::set<std::pair<JsonObject*,std::string>> members;bool duplicate{};};
    static void member(JsonParser*,JsonObject* object,const char* key,gpointer data) {
        auto& admission=*static_cast<Admission*>(data);
        if(!admission.members.emplace(object,key).second)admission.duplicate=true;
    }
    static bool nul(std::string_view text) {
        for(size_t i=0;i<text.size();++i) {
            if(!text[i])return true;
            if(text[i]=='\\') {
                if(text.substr(i,6)=="\\u0000")return true;
                ++i; // Skip the escaped character, including a literal backslash.
            }
        }
        return false;
    }
    explicit Json(std::string_view text):parser(json_parser_new()) {
        Admission admission;auto signal=g_signal_connect(parser,"object-member",G_CALLBACK(member),&admission);
        const bool valid=!text.empty() && text.size()<=65536 && !nul(text) && json_parser_load_from_data(parser,text.data(),text.size(),nullptr);
        g_signal_handler_disconnect(parser,signal);
        if(!valid || admission.duplicate || !JSON_NODE_HOLDS_OBJECT(json_parser_get_root(parser))) {
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
    static JsonObject* child(JsonObject* object,const char* name) {
        auto node=json_object_get_member(object,name);require(node && JSON_NODE_HOLDS_OBJECT(node),"Native object field");return json_node_get_object(node);
    }
    static int64_t integer(JsonObject* object,const char* name) {
        auto node=json_object_get_member(object,name);require(node && JSON_NODE_HOLDS_VALUE(node) && json_node_get_value_type(node)==G_TYPE_INT64,"Native integer field");return json_node_get_int(node);
    }
    static bool boolean(JsonObject* object,const char* name) {
        auto node=json_object_get_member(object,name);require(node && JSON_NODE_HOLDS_VALUE(node) && json_node_get_value_type(node)==G_TYPE_BOOLEAN,"Native boolean field");return json_node_get_boolean(node);
    }
    static void fields(JsonObject* object,std::initializer_list<const char*> names) {
        require(json_object_get_size(object)==names.size(),"Native exact field count");for(auto name:names)require(json_object_has_member(object,name),"Native exact field names");
    }
    uint64_t counter(const char* name) const{return decimal(text(object(),name));}
};
inline uint64_t processStart(pid_t pid) {
    std::ifstream file("/proc/"+std::to_string(pid)+"/stat");std::string line;std::getline(file,line);auto close=line.rfind(')');require(close!=line.npos,"Native process stat");std::istringstream fields(line.substr(close+1));std::string word;for(unsigned i=0;i<20;++i)require(bool(fields>>word),"Native start ticks");return decimal(word);
}
inline fd::Owned directory(std::string_view path) {
    require(path.size()>1 && path.size()<=4096 && path.front()=='/' && path.find('\0')==path.npos,"Absolute native directory");
    fd::Owned current(::open("/",O_DIRECTORY|O_CLOEXEC));require(bool(current),"Native root directory");
    size_t offset=1;
    while(offset<=path.size()) {
        const auto end=path.find('/',offset);auto part=path.substr(offset,end==path.npos?path.size()-offset:end-offset);
        require(!part.empty() && part!="." && part!="..","Canonical native directory components");
        current=fd::Owned(::openat(current.get(),std::string(part).c_str(),O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));require(bool(current),"Native directory without symlinks");
        if(end==path.npos)break;
        offset=end+1;
    }
    return current;
}
inline bool same(const struct stat& a,const struct stat& b) {return a.st_dev==b.st_dev && a.st_ino==b.st_ino && a.st_uid==b.st_uid && a.st_mode==b.st_mode;}
class Deadline {
    std::chrono::steady_clock::time_point until_=std::chrono::steady_clock::now()+std::chrono::seconds(3);
public:
    void check() const {require(std::chrono::steady_clock::now()<until_,"Original absolute three-second IPC deadline");}
    void ready(int socket,short events) const {
        for(;;) {
            check();auto left=std::chrono::duration_cast<std::chrono::milliseconds>(until_-std::chrono::steady_clock::now()).count();
            pollfd item{socket,events,0};int result=::poll(&item,1,static_cast<int>(std::max<int64_t>(1,left)));
            if(result<0 && errno==EINTR)continue;
            check();require(result>0 && !(item.revents&POLLNVAL),"Native transport readiness");return;
        }
    }
};
struct Enrollment {
    Binding binding;
    pid_t providerPID,compositorPID;
    uint64_t providerStart,compositorStart;
    std::string executableSHA256,coreABIMetadata,instance,fdAddress;
    // Strict constructor admission already validates these exact capabilities.
    bool observe{true},effects{true},minimizedState{true},canonicalScene{false};
    int effectProtocol{1},taskbarProjectionProtocol{1},effectInvalidationProtocol{1};
    std::array<std::string,3> operations{"minimize","restore","activate"};
};
struct SourceObservation {
    Scope scope;
    uint64_t observation,maximumTransferBytes,request;
    enum class Kind { UnqualifiedRootMonitorPlane, UnqualifiedClientMain } kind;
    bool previewEligible{false};
};
enum class SourceDenial {Locked,SourceUnavailable,OutputUnavailable,LayoutUnsupported};
inline const char* denialName(SourceDenial reason) {
    switch(reason) {
        case SourceDenial::Locked:return "locked";
        case SourceDenial::SourceUnavailable:return "source-unavailable";
        case SourceDenial::OutputUnavailable:return "output-unavailable";
        case SourceDenial::LayoutUnsupported:return "layout-unsupported";
    }
    throw std::logic_error("Typed source denial");
}
// Called only after controlWithin authenticated the exact native response
// channel. A denial has no current scope, native clock or completion proof.
inline std::optional<SourceDenial> decodeSourceDenial(const Json& reply) {
    auto o=reply.object();
    if(std::string_view(Json::text(o,"kind"))!="refused")return {};
    Json::fields(o,{"protocolVersion","kind","reason"});require(Json::integer(o,"protocolVersion")==3,"Native refusal protocol");
    const std::string_view reason=Json::text(o,"reason");
    if(reason=="preview-client-locked")return SourceDenial::Locked;
    if(reason=="preview-client-scope-source-unavailable")return SourceDenial::SourceUnavailable;
    if(reason=="preview-client-scope-output-unavailable")return SourceDenial::OutputUnavailable;
    if(reason=="preview-client-layout-unsupported")return SourceDenial::LayoutUnsupported;
    return {};
}
struct ScopeDenied final:std::runtime_error {
    Binding binding;Id<Incarnation> subject;uint64_t request;SourceDenial reason;
    ScopeDenied(Binding binding,Id<Incarnation> subject,uint64_t request,SourceDenial reason):
        std::runtime_error(denialName(reason)),binding(binding),subject(subject),request(request),reason(reason){}
};
class Native {
    pid_t pid_;uint64_t start_;std::string runtime_,instance_;struct stat executable_{};
    pid_t owner_=getpid();uint64_t ownerStart_=processStart(owner_);
    std::array<struct stat,3> directories_{};
    std::string expectedSHA_,coreABIMetadata_;
    std::atomic_uint64_t request_{1};
    static constexpr uint64_t controlledPreviewBit_=uint64_t{1}<<63;
    std::atomic_uint64_t previewNamespaces_{0};
    // Receiver identity belongs to this original transport, not a replaceable
    // Endpoint. Failed construction consumes an epoch; controlled mode persists.
    std::atomic_uint64_t previewRealmThrough_{0};
    std::string fdAddress_;
    uint64_t lifetime_{},session_{},frontend_{};
    void current() const {
        require(getpid()==owner_ && processStart(owner_)==ownerStart_,"Grant belongs to this native provider process");
        struct stat actual{};require(processStart(pid_)==start_ && ::stat(("/proc/"+std::to_string(pid_)+"/exe").c_str(),&actual)==0,"Native process still current");
        require(actual.st_dev==executable_.st_dev && actual.st_ino==executable_.st_ino && actual.st_size==executable_.st_size && actual.st_mtim.tv_sec==executable_.st_mtim.tv_sec && actual.st_mtim.tv_nsec==executable_.st_mtim.tv_nsec,"Native executable identity unchanged");
    }
    struct stat paths(bool enroll=false) {
        std::array<std::string,3> paths{runtime_,runtime_+"/hypr",runtime_+"/hypr/"+instance_};
        struct stat socket{};
        for(size_t i=0;i<paths.size();++i) {
            auto dir=directory(paths[i]);struct stat info{};require(fstat(dir.get(),&info)==0 && info.st_uid==getuid() && !(info.st_mode&0022),"Native directory owner and permissions");
            if(!i)require((info.st_mode&0777)==0700,"Private native runtime");
            if(enroll)directories_[i]=info;else require(same(info,directories_[i]),"Native directory identity unchanged");
            if(i==2)require(fstatat(dir.get(),".socket.sock",&socket,AT_SYMLINK_NOFOLLOW)==0 && S_ISSOCK(socket.st_mode) && socket.st_uid==getuid(),"Native control socket identity");
        }
        return socket;
    }
    fd::Owned connect(const sockaddr_un& address,socklen_t length,int type,const Deadline& deadline) const {
        deadline.check();current();fd::Owned socket(::socket(AF_UNIX,type|SOCK_CLOEXEC|SOCK_NONBLOCK,0));require(bool(socket),"Native connection socket");
        if(::connect(socket.get(),reinterpret_cast<const sockaddr*>(&address),length)<0) {
            require(errno==EINPROGRESS || errno==EAGAIN,"Native socket connects");deadline.ready(socket.get(),POLLOUT);int error=0;socklen_t length=sizeof(error);
            require(getsockopt(socket.get(),SOL_SOCKET,SO_ERROR,&error,&length)==0 && length==sizeof(error) && !error,"Native socket connected");
        }
        ucred peer{};socklen_t size=sizeof(peer);
        require(getsockopt(socket.get(),SOL_SOCKET,SO_PEERCRED,&peer,&size)==0 && size==sizeof(peer) && peer.pid==pid_ && peer.uid==getuid(),"Exact native socket peer");current();deadline.check();return socket;
    }
public:
    Native(pid_t pid,uint64_t start,std::string runtime,std::string instance,std::string expectedSHA):pid_(pid),start_(start),runtime_(std::move(runtime)),instance_(std::move(instance)) {
        require(pid>0 && start>0 && expectedSHA.size()==64 && std::all_of(expectedSHA.begin(),expectedSHA.end(),[](char c){return (c>='0' && c<='9') || (c>='a' && c<='f');}),"Native launch enrollment");
        require(!instance_.empty() && instance_.size()<=255 && std::all_of(instance_.begin(),instance_.end(),[](char c){return (c>='a' && c<='z') || (c>='A' && c<='Z') || (c>='0' && c<='9') || c=='_';}),"Native instance identifier");
        paths(true);expectedSHA_=expectedSHA;
        fd::Owned image(::open(("/proc/"+std::to_string(pid_)+"/exe").c_str(),O_RDONLY|O_CLOEXEC));require(image && fstat(image.get(),&executable_)==0 && S_ISREG(executable_.st_mode),"Actual native executable");
        auto digest=g_checksum_new(G_CHECKSUM_SHA256);std::array<uint8_t,8192> bytes{};
        for(;;){const auto n=read(image.get(),bytes.data(),bytes.size());if(n<0 && errno==EINTR)continue;require(n>=0,"Native executable hash read");if(!n)break;g_checksum_update(digest,bytes.data(),n);}
        const bool matches=expectedSHA==g_checksum_get_string(digest);g_checksum_free(digest);require(matches,"Exact owning core hash");current();
        auto hello=control("{\"protocolVersion\":3,\"kind\":\"hello\"}");Json::fields(hello.object(),{"protocolVersion","kind","binding","previewFdAddress","compositor","capabilities"});
        require(std::string_view(Json::text(hello.object(),"kind"))=="attached","Native grant attached");
        auto binding=Json::child(hello.object(),"binding");Json::fields(binding,{"lifetime","session","frontend"});lifetime_=decimal(Json::text(binding,"lifetime"));session_=decimal(Json::text(binding,"session"));frontend_=decimal(Json::text(binding,"frontend"));fdAddress_=Json::text(hello.object(),"previewFdAddress");(void)fd::address(fdAddress_);
        auto compositor=Json::child(hello.object(),"compositor");Json::fields(compositor,{"pid","instance","coreHash"});
        require(Json::integer(compositor,"pid")==pid_ && std::string_view(Json::text(compositor,"instance"))==instance_,"Native hello owning instance");
        std::string_view coreHash=Json::text(compositor,"coreHash");require(!coreHash.empty() && coreHash.size()<=256 && std::all_of(coreHash.begin(),coreHash.end(),[](unsigned char c){return c>=32 && c<127;}),"Native ABI hash metadata bound");
        coreABIMetadata_=std::string(coreHash);
        auto caps=Json::child(hello.object(),"capabilities");Json::fields(caps,{"observe","effects","minimizedState","effectProtocol","operations","canonicalScene","taskbarProjectionProtocol","effectInvalidationProtocol"});
        require(Json::boolean(caps,"observe") && Json::boolean(caps,"effects") && Json::boolean(caps,"minimizedState") && !Json::boolean(caps,"canonicalScene") && Json::integer(caps,"effectProtocol")==1 && Json::integer(caps,"taskbarProjectionProtocol")==1 && Json::integer(caps,"effectInvalidationProtocol")==1,"Exact owning authority492 capabilities");
        auto operations=json_object_get_member(caps,"operations");require(operations && JSON_NODE_HOLDS_ARRAY(operations),"Native operation list");auto array=json_node_get_array(operations);require(json_array_get_length(array)==3,"Native operation count");
        const std::array<const char*,3> names{"minimize","restore","activate"};for(guint i=0;i<3;++i){auto node=json_array_get_element(array,i);require(JSON_NODE_HOLDS_VALUE(node) && json_node_get_value_type(node)==G_TYPE_STRING && std::string_view(json_node_get_string(node))==names[i],"Native operation names");}
    }
    Enrollment enrollment() {
        current();paths();
        return {binding(),owner_,pid_,ownerStart_,start_,expectedSHA_,coreABIMetadata_,instance_,fdAddress_};
    }
    SourceObservation scope(Id<Incarnation> subject) {return observeScope(subject,SourceObservation::Kind::UnqualifiedRootMonitorPlane);}
    SourceObservation clientScope(Id<Incarnation> subject) {return observeScope(subject,SourceObservation::Kind::UnqualifiedClientMain);}
private:
    SourceObservation observeScope(Id<Incarnation> subject,SourceObservation::Kind source) {
        Deadline deadline;require(subject.value>0,"Positive native scope subject");
        const bool client=source==SourceObservation::Kind::UnqualifiedClientMain;
        const std::string kind=client?"preview-client-scope":"preview-capture-probe-scope";
        const std::string sourceKind=client?"isolated-root-client-unqualified":"root-surface-commit-monitor-plane-unqualified";
        const auto requestId=next();
        auto reply=controlWithin("{\"protocolVersion\":3,\"kind\":\""+kind+"-request\",\"binding\":"+bindingJSON()+",\"requestId\":\""+std::to_string(requestId)+"\",\"subjectIncarnation\":\""+std::to_string(subject.value)+"\"}",deadline);
        if(client) {if(const auto denied=decodeSourceDenial(reply))throw ScopeDenied(binding(),subject,requestId,*denied);}
        auto object=reply.object();Json::fields(object,{"protocolVersion","kind","binding","requestId","scope","maximumTransferBytes","previewEligible","scopeKind"});
        require(std::string_view(Json::text(object,"kind"))==kind && reply.counter("requestId")==requestId,"Native scope reply correlation");
        auto parseBinding=[](JsonObject* fields) {
            Json::fields(fields,{"lifetime","session","frontend"});return Binding{{decimal(Json::text(fields,"lifetime"))},{decimal(Json::text(fields,"session"))},{decimal(Json::text(fields,"frontend"))}};
        };
        const auto owner=binding();require(parseBinding(Json::child(object,"binding"))==owner,"Native scope envelope own binding");
        auto raw=Json::child(object,"scope");Json::fields(raw,{"binding","context","observation","clock","now","present","sourceLive","locked","gpuReady"});
        require(parseBinding(Json::child(raw,"binding"))==owner,"Native scope own binding");
        auto c=Json::child(raw,"context");Json::fields(c,{"lifetime","incarnation","output","privacy","rendering","scene","content"});
        Context context{{decimal(Json::text(c,"lifetime"))},{decimal(Json::text(c,"incarnation"))},{decimal(Json::text(c,"output"))},{decimal(Json::text(c,"privacy"))},{decimal(Json::text(c,"rendering"))},{decimal(Json::text(c,"scene"))},{decimal(Json::text(c,"content"))}};
        Scope scope{owner,context,{decimal(Json::text(raw,"clock"))},decimal(Json::text(raw,"now")),Json::boolean(raw,"present"),Json::boolean(raw,"sourceLive"),Json::boolean(raw,"locked"),Json::boolean(raw,"gpuReady")};
        require(context.lifetime==owner.lifetime && context.incarnation==subject && scope.clock.value==owner.lifetime.value,"Native scope lifetime/subject/clock correlation");
        require(!Json::boolean(object,"previewEligible") && std::string_view(Json::text(object,"scopeKind"))==sourceKind,"Native492 probe is unqualified and cannot authorize preview capture");
        SourceObservation observed{scope,decimal(Json::text(raw,"observation")),reply.counter("maximumTransferBytes"),requestId,source,false};
        require(observed.maximumTransferBytes%4096==0,"Native transfer plan page alignment");current();deadline.check();return observed;
    }
    void releasePreviewControl(uint64_t realm) {
        // Physical/proof closure was checked by the owning C transaction. Core
        // death does not prevent releasing that already settled local claim.
        require(getpid()==owner_ && processStart(owner_)==ownerStart_,"Original native preview realm process");
        require(realm && previewRealmThrough_.load(std::memory_order_acquire)==realm,"Exact current native preview realm");
        uint64_t expected=controlledPreviewBit_;
        require(previewNamespaces_.compare_exchange_strong(expected,0,std::memory_order_acq_rel),"Original active preview realm release");
    }
public:
    Binding binding() const{current();return {{lifetime_},{session_},{frontend_}};}
    bool previewControlClaimed()const noexcept{return (previewNamespaces_.load(std::memory_order_acquire)&controlledPreviewBit_)!=0;}
    uint64_t claimPreviewControl() {
        current();uint64_t expected=0;
        require(previewNamespaces_.compare_exchange_strong(expected,controlledPreviewBit_,std::memory_order_acq_rel),
            "One controlled preview namespace with no live legacy provider on original transport grant");
        try {
            auto previous=previewRealmThrough_.load(std::memory_order_acquire);
            require(previous<UINT64_MAX,"Native preview realm counter not exhausted");
            const auto realm=previous+1;previewRealmThrough_.store(realm,std::memory_order_release);return realm;
        }catch(...) {
            previewNamespaces_.store(0,std::memory_order_release);throw;
        }
    }
    class PreviewControlClaim {
        Native* owner_;
        const uint64_t realm_;
        bool published_{};
    public:
        explicit PreviewControlClaim(Native& owner):owner_(&owner),realm_(owner.claimPreviewControl()){}
        ~PreviewControlClaim(){if(owner_ && !published_)try{owner_->releasePreviewControl(realm_);}catch(...){}}
        PreviewControlClaim(const PreviewControlClaim&)=delete;PreviewControlClaim& operator=(const PreviewControlClaim&)=delete;
        PreviewControlClaim(PreviewControlClaim&& other)noexcept:owner_(std::exchange(other.owner_,nullptr)),realm_(other.realm_),published_(other.published_){}
        PreviewControlClaim& operator=(PreviewControlClaim&&)=delete;
        uint64_t epoch()const noexcept{return realm_;}
        void publish()noexcept{published_=true;}
        // This is namespace bookkeeping, never a physical cleanup authority.
        // Only the original validated C close path completes a published claim.
        void complete(){require(owner_ && published_,"Published original preview realm completion");owner_->releasePreviewControl(realm_);owner_=nullptr;}
    };
    class LegacyPreviewClaim {
        Native* owner_;
    public:
        explicit LegacyPreviewClaim(Native& owner):owner_(&owner) {
            owner.current();auto count=owner.previewNamespaces_.load(std::memory_order_acquire);
            for(;;) {
                require(!owner.previewRealmThrough_.load(std::memory_order_acquire) && !(count&controlledPreviewBit_) && count<controlledPreviewBit_-1,
                    "Legacy preview cannot borrow a controlled original transport grant");
                if(owner.previewNamespaces_.compare_exchange_weak(count,count+1,std::memory_order_acq_rel))break;
            }
        }
        ~LegacyPreviewClaim(){if(owner_)owner_->previewNamespaces_.fetch_sub(1,std::memory_order_acq_rel);}
        LegacyPreviewClaim(const LegacyPreviewClaim&)=delete;
        LegacyPreviewClaim& operator=(const LegacyPreviewClaim&)=delete;
        LegacyPreviewClaim(LegacyPreviewClaim&& other)noexcept:owner_(std::exchange(other.owner_,nullptr)){}
        LegacyPreviewClaim& operator=(LegacyPreviewClaim&&)=delete;
    };
    uint64_t next(){current();auto value=request_.load();for(;;){require(value>0 && value<UINT64_MAX,"Native request counter not exhausted");if(request_.compare_exchange_weak(value,value+1))return value;}}
    std::string bindingJSON() const {current();return "{\"lifetime\":\""+std::to_string(lifetime_)+"\",\"session\":\""+std::to_string(session_)+"\",\"frontend\":\""+std::to_string(frontend_)+"\"}";}
    Json control(const std::string& body) {Deadline deadline;return controlWithin(body,deadline);}
    Json controlWithin(const std::string& body,const Deadline& deadline) {
        deadline.check();require(body.size()<=4096,"Native request byte bound");Json outgoing(body);require(Json::integer(outgoing.object(),"protocolVersion")==3,"Native request version");
        const auto path=runtime_+"/hypr/"+instance_+"/.socket.sock";require(path.size()<sizeof(sockaddr_un::sun_path),"Native control path bound");
        auto before=paths();sockaddr_un address{};address.sun_family=AF_UNIX;memcpy(address.sun_path,path.c_str(),path.size()+1);auto socket=connect(address,static_cast<socklen_t>(offsetof(sockaddr_un,sun_path)+path.size()+1),SOCK_STREAM,deadline);
        const std::string wire="j/elm_observe "+body;size_t offset=0;while(offset<wire.size()){deadline.ready(socket.get(),POLLOUT);const auto n=send(socket.get(),wire.data()+offset,wire.size()-offset,MSG_NOSIGNAL);if(n<0 && (errno==EINTR || errno==EAGAIN))continue;require(n>0,"Native control write");offset+=n;}
        deadline.check();require(shutdown(socket.get(),SHUT_WR)==0,"Native request half-close");
        std::string text;std::array<char,4096> bytes{};for(;;){deadline.ready(socket.get(),POLLIN);const auto n=recv(socket.get(),bytes.data(),bytes.size(),0);if(n<0 && (errno==EINTR || errno==EAGAIN))continue;require(n>=0,"Native control receive");if(!n)break;require(text.size()+static_cast<size_t>(n)<=65536,"Native metadata reply bound");text.append(bytes.data(),n);}
        auto after=paths();require(same(before,after) && before.st_ctim.tv_sec==after.st_ctim.tv_sec && before.st_ctim.tv_nsec==after.st_ctim.tv_nsec,"Native control socket not replaced");current();deadline.check();Json result(text);require(Json::integer(result.object(),"protocolVersion")==3,"Native reply version");deadline.check();return result;
    }
    Json request(const char* kind,const std::string& fields="") {return control("{\"protocolVersion\":3,\"kind\":\""+std::string(kind)+"\",\"binding\":"+bindingJSON()+",\"requestId\":\""+std::to_string(next())+"\""+fields+"}");}
    std::optional<fd::Received<fd::Count>> query(fd::Operation op,uint64_t capture,uint64_t subject,uint64_t transfer=0) {
        Deadline deadline;const auto [address,length]=fd::address(fdAddress_);auto socket=connect(address,length,SOCK_SEQPACKET,deadline);
        fd::Query query{fd::MAGIC,1,op,lifetime_,session_,frontend_,next(),capture,subject,transfer};require(fd::send(socket.get(),query),"Native image request send");
        deadline.ready(socket.get(),POLLIN);auto reply=fd::receive<fd::Count>(socket.get(),op==fd::Get?1:0);current();deadline.check();
        if(!reply || !fd::matches(reply->words,query))return {};
        return reply;
    }
    std::optional<fd::Received<stylecropfd::Count>> familyQuery(fd::Operation op,uint64_t capture,uint64_t subject,uint64_t transfer=0) {
        Deadline deadline;const auto [address,length]=fd::address(fdAddress_);auto socket=connect(address,length,SOCK_SEQPACKET,deadline);
        fd::Query query{fd::MAGIC,3,op,lifetime_,session_,frontend_,next(),capture,subject,transfer};require(fd::send(socket.get(),query),"Native style family image request send");
        deadline.ready(socket.get(),POLLIN);auto reply=fd::receive<stylecropfd::Count>(socket.get(),op==fd::Get?1:0);current();deadline.check();
        if(!reply || !stylecropfd::matches(reply->words,query))return {};
        return reply;
    }
    std::optional<fd::Received<backdropfd::Count>> backdropQuery(fd::Operation op,uint64_t capture,uint64_t subject,uint64_t transfer=0) {
        Deadline deadline;const auto [address,length]=fd::address(fdAddress_);auto socket=connect(address,length,SOCK_SEQPACKET,deadline);
        fd::Query query{fd::MAGIC,4,op,lifetime_,session_,frontend_,next(),capture,subject,transfer};require(fd::send(socket.get(),query),"Native generated backdrop image request send");
        deadline.ready(socket.get(),POLLIN);auto reply=fd::receive<backdropfd::Count>(socket.get(),op==fd::Get?1:0);current();deadline.check();
        if(!reply || !backdropfd::matches(reply->words,query))return {};
        return reply;
    }
    std::optional<uri::NativeTime> time(const fd::Header& frame) noexcept {
        try {
            auto observed=query(fd::Observe,frame[fd::Capture],frame[fd::Subject],frame[fd::Transfer]);if(!observed)return {};
            const auto& h=observed->words;
            const auto source=(frame[fd::Flags]&uint64_t{8})?fd::SourcePlane::ClientMain:fd::SourcePlane::Monitor;
            if(!fd::imageHeaderFor(frame,source) || !fd::imageHeaderFor(h,source) || (h[fd::Flags]&uint64_t{12})!=(frame[fd::Flags]&uint64_t{12}) || !(h[fd::Flags]&fd::Present) || h[fd::Lifetime]!=frame[fd::Lifetime] || h[fd::Output]!=frame[fd::Output] || h[fd::Privacy]!=frame[fd::Privacy] || h[fd::Rendering]!=frame[fd::Rendering] || h[fd::Now]<frame[fd::Now] || h[fd::Now]>=frame[fd::Expires])return {};
            return uri::NativeTime{{h[fd::Lifetime]},h[fd::Now]};
        }catch(...){return {};}
    }
};
}
