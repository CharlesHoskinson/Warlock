#pragma once
#include <algorithm>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
namespace PrivateRuntime {
inline bool pathAllowed(const char* path,uid_t uid) {
    if(!path)return false;
    const auto prefix=std::string("/run/user/")+std::to_string(uid)+"/wqa/";
    const std::string value(path);
    if(!value.starts_with(prefix)||value.size()!=prefix.size()+4)return false;
    return std::all_of(value.begin()+prefix.size(),value.end(),[](char c){return(c>='0'&&c<='9')||(c>='a'&&c<='f');});
}
inline bool directoryAllowed(const struct stat& row,uid_t uid) {
    return S_ISDIR(row.st_mode)&&row.st_uid==uid&&(row.st_mode&0777)==0700;
}
inline bool allowed(const char* path,uid_t uid=getuid()) {
    if(!pathAllowed(path,uid))return false;
    const auto user=std::string("/run/user/")+std::to_string(uid);
    struct stat runtime{},parent{},root{};
    return !lstat(path,&runtime)&&!lstat((user+"/wqa").c_str(),&parent)&&!lstat(user.c_str(),&root)
        &&directoryAllowed(runtime,uid)&&directoryAllowed(parent,uid)&&directoryAllowed(root,uid);
}
}
