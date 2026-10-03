#pragma once
#include <QByteArray>
#include <QCryptographicHash>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>
namespace OwnedRoute {
// Check the actual mapped object, not just a same-named replacement on disk.
inline bool mappedMaterialMatches(const std::string& path,const std::string& expected) {
    char* resolved=realpath(path.c_str(),nullptr);if(!resolved)return false;
    std::string canonical=resolved;free(resolved);
    int fd=open(canonical.c_str(),O_RDONLY|O_CLOEXEC|O_NOFOLLOW);if(fd<0)return false;
    struct Close{int fd;~Close(){close(fd);}}guard{fd};struct stat st{};
    if(fstat(fd,&st)||!S_ISREG(st.st_mode)||st.st_size<=0||st.st_size>134217728)return false;
    QCryptographicHash hash(QCryptographicHash::Sha256);char buffer[65536];ssize_t n=0;
    while((n=read(fd,buffer,sizeof(buffer)))>0)hash.addData(QByteArrayView(buffer,n));
    if(n<0||hash.result().toHex().toStdString()!=expected)return false;
    std::ifstream maps("/proc/self/maps");std::string line;
    while(std::getline(maps,line)) {
        std::istringstream fields(line);std::string address,permissions,offset,device,inode,name;
        if(!(fields>>address>>permissions>>offset>>device>>inode))continue;
        std::getline(fields,name);name.erase(0,name.find_first_not_of(' '));
        if(name!=canonical)continue;unsigned devMajor=0,devMinor=0;
        if(std::sscanf(device.c_str(),"%x:%x",&devMajor,&devMinor)!=2)continue;
        try{if(std::stoull(inode)==static_cast<unsigned long long>(st.st_ino) && devMajor==major(st.st_dev) && devMinor==minor(st.st_dev))return true;}catch(...) {return false;}
    }
    return false;
}
inline bool reviewedInstalledMesaMaterial() {
    return mappedMaterialMatches("/usr/lib/libgallium-26.2.2-arch1.1.so","d7d313070226982467fd8984d943d84c7adeaf290b1705de7bf227fca3b392da") &&
           mappedMaterialMatches("/usr/lib/libEGL_mesa.so.0","15c06ccfe5054c95059f2526a284b8fb2d10c9000bbec20c531eb9d6815abc6d");
}
}
