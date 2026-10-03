#pragma once
#include <algorithm>
#include <cctype>
#include <string>
namespace OwnedRoute {
inline bool reviewedGPUBackend(const std::string& vendor,const std::string& version,std::string renderer) {
    std::transform(renderer.begin(),renderer.end(),renderer.begin(),[](unsigned char c){return std::tolower(c);});
    if(vendor.find("Mesa")==std::string::npos || renderer.empty())return false;
    bool releaseMatches=false;
    for(const char* release:{"Mesa 26.2.2","Mesa 26.2.2-arch1.1"}) {
        const std::string exact=release;const auto at=version.find(exact);
        if(at==std::string::npos)continue;const auto end=at+exact.size();
        if((!at||std::isspace(static_cast<unsigned char>(version[at-1]))) &&
           (end==version.size()||std::isspace(static_cast<unsigned char>(version[end]))))releaseMatches=true;
    }
    if(!releaseMatches)return false;
    for(const char* unsupported:{"zink","llvmpipe","softpipe","swrast","software","swr "})
        if(renderer.find(unsupported)!=std::string::npos)return false;
    return true;
}
}
