#pragma once
#include "private_runtime.hpp"
#include <fstream>
#include <regex>
#include <sys/resource.h>
#include <sys/socket.h>
#include <sys/random.h>
#include <cerrno>
#include <stdexcept>
namespace ProductionRuntime {
inline bool scopeAllowed(const std::string& cgroup) {
 return std::regex_search(cgroup,std::regex("/qa-harness\\.slice/qa-harness-[A-Za-z0-9_-]+\\.scope(\\n|$)"));
}
inline bool allowed(const char* runtime,const char* privateFlag,uid_t uid=getuid()) {
 if(!runtime)return false;
 const std::string canonical="/run/user/"+std::to_string(uid);
 struct stat row{};
 if(!privateFlag)return std::string(runtime)==canonical&&!lstat(runtime,&row)&&PrivateRuntime::directoryAllowed(row,uid);
 if(std::string(privateFlag)!="1"||!PrivateRuntime::allowed(runtime,uid))return false;
 std::ifstream stream("/proc/self/cgroup");std::string cgroup((std::istreambuf_iterator<char>(stream)),{});
 struct rlimit limit{};
 return scopeAllowed(cgroup)&&!getrlimit(RLIMIT_CORE,&limit)&&limit.rlim_cur==1&&limit.rlim_max==1;
}
inline bool busAddressAllowed(const std::string& configured,const std::string& expected) {
 if(configured==expected)return true;
 const auto prefix=expected+",guid=";
 return configured.starts_with(prefix)&&configured.size()==prefix.size()+32&&std::all_of(configured.begin()+prefix.size(),configured.end(),[](char c){return(c>='0'&&c<='9')||(c>='a'&&c<='f');});
}
inline bool peerUID(int fd,uid_t uid=getuid()) {struct ucred peer{};socklen_t size=sizeof(peer);return !getsockopt(fd,SOL_SOCKET,SO_PEERCRED,&peer,&size)&&size==sizeof(peer)&&peer.uid==uid;}
inline std::string nonce() {
 unsigned char bytes[32];size_t done=0;
 while(done<sizeof(bytes)){const auto count=getrandom(bytes+done,sizeof(bytes)-done,0);if(count<0&&errno==EINTR)continue;if(count<=0)throw std::runtime_error("incarnation randomness unavailable");done+=count;}
 const char* alphabet="0123456789abcdef";std::string result;result.reserve(64);for(auto b:bytes){result+=alphabet[b>>4];result+=alphabet[b&15];}return result;
}
}
