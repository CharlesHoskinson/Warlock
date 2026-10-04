#include "binding-registration.hpp"
#include <cassert>
#include <iostream>
#include <limits>
#include <map>
struct Session {uint64_t id,frontend;};
int main() {
    using Elm::Registration::contains;
    std::map<int,Session> rows;
    auto check=[](const char* name,bool value){assert(value);std::cout<<name<<"\n";};
    check("emptyTable",!contains(rows,10,1));
    rows.emplace(100,Session{10,1});
    check("exactTuple",contains(rows,10,1));
    check("wrongFrontend",!contains(rows,10,2));
    check("wrongSession",!contains(rows,11,1));
    rows.emplace(200,Session{20,7});
    check("otherPeerGrantStillRegistered",contains(rows,20,7));
    check("crossTupleRefused",!contains(rows,10,7));
    check("absentAfterFullScan",!contains(rows,30,1));
    const auto max=std::numeric_limits<uint64_t>::max();
    rows.emplace(300,Session{max,max});
    check("maxUInt64Registered",contains(rows,max,max));
    check("maxUInt64WrongFrontend",!contains(rows,max,max-1));
    rows.erase(200);
    check("removedExactRecordAbsent",!contains(rows,20,7));
}
