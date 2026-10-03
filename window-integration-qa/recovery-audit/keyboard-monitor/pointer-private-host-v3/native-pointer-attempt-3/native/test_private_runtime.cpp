#include "private_runtime.hpp"
#include <cassert>
int main() {
    assert(PrivateRuntime::pathAllowed("/run/user/1000/wqa/1a2b",1000));
    for(auto path:{"/run/user/1000","/tmp/kbn-safe","/run/user/1001/wqa/1a2b","/run/user/1000/wqa/1A2b","/run/user/1000/wqa/qa-1a2b","/run/user/1000/wqa/1a2b/x","/run/user/1000/wqa/123","/run/user/1000/wqa/12345"})assert(!PrivateRuntime::pathAllowed(path,1000));
    assert(!PrivateRuntime::pathAllowed(nullptr,1000));
    struct stat row{};row.st_uid=1000;row.st_mode=S_IFDIR|0700;
    assert(PrivateRuntime::directoryAllowed(row,1000));
    row.st_uid=1001;assert(!PrivateRuntime::directoryAllowed(row,1000));
    row.st_uid=1000;row.st_mode=S_IFLNK|0700;assert(!PrivateRuntime::directoryAllowed(row,1000));
    row.st_mode=S_IFDIR|0755;assert(!PrivateRuntime::directoryAllowed(row,1000));
    assert(!PrivateRuntime::allowed("/run/user/1000",1000));
}
