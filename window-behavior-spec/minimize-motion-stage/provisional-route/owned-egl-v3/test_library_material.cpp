#include "LibraryMaterial.hpp"
#include <cassert>
#include <iostream>
#include <sys/mman.h>
using namespace OwnedRoute;
int main(){int count=0;auto check=[&](bool x){assert(x);++count;};char path[]="/tmp/egl-material-XXXXXX";
 int fd=mkstemp(path);assert(fd>=0);assert(write(fd,"provenance",10)==10);
 const auto digest=QCryptographicHash::hash(QByteArray("provenance"),QCryptographicHash::Sha256).toHex().toStdString();
 check(!mappedMaterialMatches(path,digest)); // Right file, not mapped.
 void* mapped=mmap(nullptr,10,PROT_READ,MAP_PRIVATE,fd,0);assert(mapped!=MAP_FAILED);
 check(mappedMaterialMatches(path,digest));
 check(!mappedMaterialMatches(path,std::string(64,'0')));
 std::string alias=std::string(path)+"-link";assert(symlink(path,alias.c_str())==0);
 check(mappedMaterialMatches(alias,digest));
 std::string old=std::string(path)+"-old";assert(rename(path,old.c_str())==0);
 int replacement=open(path,O_CREAT|O_EXCL|O_WRONLY,0600);assert(replacement>=0);assert(write(replacement,"provenance",10)==10);close(replacement);
 check(!mappedMaterialMatches(path,digest)); // Same bytes/path, wrong mapped inode.
 check(mappedMaterialMatches(old,digest));
 assert(unlink(old.c_str())==0);check(!mappedMaterialMatches(old,digest));
 check(!mappedMaterialMatches("/tmp/does-not-exist-owned-egl-material",digest));
 munmap(mapped,10);close(fd);unlink(path);unlink(alias.c_str());
 std::cout<<count<<" mapped material identity/hash checks PASS\n";
}
