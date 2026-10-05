#pragma once
#include "preview_uri.hpp"
#include <cstring>
#include <utility>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <unistd.h>

namespace preview::fd {
class Owned {
    int fd_{-1};
public:
    explicit Owned(int value=-1):fd_(value){}
    ~Owned(){if(fd_>=0)::close(fd_);}
    Owned(const Owned&)=delete;Owned& operator=(const Owned&)=delete;
    Owned(Owned&& other) noexcept:fd_(std::exchange(other.fd_,-1)){}
    Owned& operator=(Owned&& other) noexcept {if(this!=&other){if(fd_>=0)::close(fd_);fd_=std::exchange(other.fd_,-1);}return *this;}
    int get() const noexcept {return fd_;}
    explicit operator bool() const {return fd_>=0;}
};
constexpr uint64_t MAGIC=0x454c4d5046443031ULL;
constexpr int SEALS=F_SEAL_WRITE|F_SEAL_GROW|F_SEAL_SHRINK|F_SEAL_SEAL;
enum RequestWord:size_t { RMagic,RVersion,ROp,RLifetime,RSession,RFrontend,RRequest,RCapture,RSubject,RTransfer,RCount };
enum ReplyWord:size_t { Magic,Version,Status,Lifetime,Session,Frontend,Request,Capture,Subject,Output,Completed,Now,Width,Height,Bytes,Charge,Transfer,CRC,Privacy,Rendering,Scene,Content,Flags,Deadline,Expires,Count };
enum Operation:uint64_t {Get=1,Release=2,Observe=3};
enum Flag:uint64_t {Present=1,SourceLive=2,FullMonitorPlane=4,IsolatedClientPlane=8};
using Query=std::array<uint64_t,RCount>;
using Header=std::array<uint64_t,Count>;
template<size_t N> std::array<uint8_t,N*8> encode(const std::array<uint64_t,N>& words) {
    std::array<uint8_t,N*8> bytes{};
    for(size_t i=0;i<N;++i)for(size_t b=0;b<8;++b)bytes[i*8+b]=static_cast<uint8_t>(words[i]>>(56-8*b));
    return bytes;
}
template<size_t N> std::array<uint64_t,N> decode(const std::array<uint8_t,N*8>& bytes) {
    std::array<uint64_t,N> words{};
    for(size_t i=0;i<N;++i)for(size_t b=0;b<8;++b)words[i]=(words[i]<<8)|bytes[i*8+b];
    return words;
}
inline std::pair<sockaddr_un,socklen_t> address(std::string_view name) {
    if(name.empty() || name.size()>sizeof(sockaddr_un::sun_path)-2 || name.find('\0')!=name.npos)throw std::invalid_argument("Abstract socket name");
    sockaddr_un value{};value.sun_family=AF_UNIX;std::memcpy(value.sun_path+1,name.data(),name.size());
    return {value,static_cast<socklen_t>(offsetof(sockaddr_un,sun_path)+1+name.size())};
}
inline Owned seal(std::span<const uint8_t> bytes) {
    if(bytes.empty() || bytes.size()>64ULL*1024*1024)throw std::invalid_argument("Sealed image bounds");
    Owned image(::memfd_create("elm-preview-image",MFD_CLOEXEC|MFD_ALLOW_SEALING));
    if(!image)throw std::runtime_error("Image memfd unavailable");
    size_t offset=0;
    while(offset<bytes.size()) {
        const auto written=::write(image.get(),bytes.data()+offset,bytes.size()-offset);
        if(written<0 && errno==EINTR)continue;
        if(written<=0)throw std::runtime_error("Image memfd write failed");
        offset+=static_cast<size_t>(written);
    }
    if(::fcntl(image.get(),F_ADD_SEALS,SEALS)!=0 || (::fcntl(image.get(),F_GET_SEALS)&SEALS)!=SEALS)throw std::runtime_error("Image sealing failed");
    return image;
}
template<size_t N> bool send(int socket,const std::array<uint64_t,N>& words,int image=-1) noexcept {
    auto bytes=encode(words);iovec io{bytes.data(),bytes.size()};msghdr message{};message.msg_iov=&io;message.msg_iovlen=1;
    alignas(cmsghdr) std::array<uint8_t,CMSG_SPACE(sizeof(int))> ancillary{};
    if(image>=0) {
        message.msg_control=ancillary.data();message.msg_controllen=ancillary.size();
        auto item=CMSG_FIRSTHDR(&message);item->cmsg_level=SOL_SOCKET;item->cmsg_type=SCM_RIGHTS;item->cmsg_len=CMSG_LEN(sizeof(int));std::memcpy(CMSG_DATA(item),&image,sizeof(image));
    }
    ssize_t sent;
    do{sent=::sendmsg(socket,&message,MSG_NOSIGNAL|MSG_DONTWAIT);}while(sent<0 && errno==EINTR);
    return sent==static_cast<ssize_t>(bytes.size());
}
template<size_t N> struct Received {std::array<uint64_t,N> words{};std::vector<Owned> rights;};
template<size_t N> std::optional<Received<N>> receive(int socket,size_t expectedRights) {
    std::array<uint8_t,N*8> bytes{};iovec io{bytes.data(),bytes.size()};msghdr message{};message.msg_iov=&io;message.msg_iovlen=1;
    alignas(cmsghdr) std::array<uint8_t,CMSG_SPACE(sizeof(int)*8)> ancillary{};message.msg_control=ancillary.data();message.msg_controllen=ancillary.size();
    ssize_t got;do{got=::recvmsg(socket,&message,MSG_CMSG_CLOEXEC);}while(got<0 && errno==EINTR);
    Received<N> result;bool malformed=false;
    for(auto item=CMSG_FIRSTHDR(&message);item;item=CMSG_NXTHDR(&message,item)) {
        if(item->cmsg_level!=SOL_SOCKET || item->cmsg_type!=SCM_RIGHTS || item->cmsg_len<CMSG_LEN(0)){malformed=true;continue;}
        const size_t size=item->cmsg_len-CMSG_LEN(0);if(size%sizeof(int)){malformed=true;continue;}
        for(size_t pos=0;pos<size;pos+=sizeof(int)) {int image=-1;std::memcpy(&image,CMSG_DATA(item)+pos,sizeof(image));result.rights.emplace_back(image);}
    }
    // Rights received before discovering a malformed envelope are owned here
    // and closed on every refusal, including ancillary/data truncation.
    if(got!=static_cast<ssize_t>(bytes.size()) || (message.msg_flags&(MSG_TRUNC|MSG_CTRUNC)) || malformed || result.rights.size()!=expectedRights)return {};
    result.words=decode<N>(bytes);return result;
}
inline bool matches(const Header& h,const Query& q) {
    return h[Magic]==MAGIC && h[Version]==1 && h[Status]==0 && h[Lifetime]==q[RLifetime] && h[Session]==q[RSession] && h[Frontend]==q[RFrontend] && h[Request]==q[RRequest] && h[Capture]==q[RCapture] && h[Subject]==q[RSubject] && h[Transfer] && (q[RTransfer]==0 || h[Transfer]==q[RTransfer]);
}
inline bool imageHeader(const Header& h) {
    return h[Lifetime] && h[Session] && h[Frontend] && h[Request] && h[Capture] && h[Subject] && h[Output] && h[Completed] && h[Now]>=h[Completed] && h[Width] && h[Height] && h[Width]<=4096 && h[Height]<=4096 && h[Bytes]>=8 && h[Bytes]<=64ULL*1024*1024 && h[Charge]>=h[Bytes] && h[Transfer] && h[CRC]<=UINT32_MAX && h[Privacy] && h[Rendering] && h[Scene] && h[Content] && h[Flags] && !(h[Flags]&~uint64_t{7}) && h[Deadline]>h[Completed] && h[Expires]>h[Completed];
}
// The caller must reserve before mapping. Seals make the backing immutable,
// including for senders that retain a writable descriptor after transfer.
enum class SourcePlane {RootMonitor,IsolatedClient};
inline bool clientImageHeader(Header h) {
    if(!(h[Flags]&IsolatedClientPlane) || (h[Flags]&~uint64_t{11}))return false;
    h[Flags]=(h[Flags]&uint64_t{3})|FullMonitorPlane;
    return imageHeader(h);
}
class Mapped final:public uri::Payload {
    Owned file_;
    void* memory_{MAP_FAILED};
    uint64_t bytes_,charge_;
public:
    Mapped(Owned&& file,const Header& h,uint64_t reserved,SourcePlane expected=SourcePlane::RootMonitor):file_(std::move(file)),bytes_(h[Bytes]),charge_(reserved) {
        struct stat info{};
        if(!(expected==SourcePlane::IsolatedClient?clientImageHeader(h):imageHeader(h)) || reserved<bytes_ || !file_ || ::fstat(file_.get(),&info) || !S_ISREG(info.st_mode) || info.st_uid!=getuid() || info.st_size<0 || uint64_t(info.st_size)!=bytes_ || (::fcntl(file_.get(),F_GET_SEALS)&SEALS)!=SEALS || (::fcntl(file_.get(),F_GETFD)&FD_CLOEXEC)==0)throw std::invalid_argument("Untrusted image descriptor");
        memory_=::mmap(nullptr,bytes_,PROT_READ,MAP_SHARED,file_.get(),0);
        if(memory_==MAP_FAILED)throw std::runtime_error("Image mmap failed");
        constexpr std::array<uint8_t,8> magic{137,80,78,71,13,10,26,10};
        if(!std::equal(magic.begin(),magic.end(),static_cast<const uint8_t*>(memory_))) {
            ::munmap(memory_,bytes_);memory_=MAP_FAILED;throw std::invalid_argument("Image signature");
        }
    }
    ~Mapped() override {if(memory_!=MAP_FAILED)::munmap(memory_,bytes_);}
    uint64_t charge() const noexcept override{return charge_;}
    std::span<const uint8_t> png() const noexcept override{return {static_cast<const uint8_t*>(memory_),static_cast<size_t>(bytes_)};}
};
}
