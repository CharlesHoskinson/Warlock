#pragma once
#include <algorithm>
#include <cctype>
#include <string>
namespace OwnedRoute {
inline bool reviewedGPUBackend(const std::string& vendor,const std::string& version,std::string renderer) {
    std::transform(renderer.begin(),renderer.end(),renderer.begin(),[](unsigned char c){return std::tolower(c);});
    const std::string release="Mesa 26.2.2";
    const auto at=version.find(release);
    if(vendor.find("Mesa")==std::string::npos || at==std::string::npos || renderer.empty())return false;
    const auto end=at+release.size();
    // Only the audited release token; suffix/development releases are distinct.
    if((at && !std::isspace(static_cast<unsigned char>(version[at-1]))) ||
       (end<version.size() && !std::isspace(static_cast<unsigned char>(version[end]))))return false;
    for(const char* unsupported:{"zink","llvmpipe","softpipe","swrast","software","swr "})
        if(renderer.find(unsupported)!=std::string::npos)return false;
    return true;
}
}
