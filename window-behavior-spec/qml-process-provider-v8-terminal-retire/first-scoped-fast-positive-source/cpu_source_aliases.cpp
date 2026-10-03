#include "SourceAliases.hpp"
#include <iostream>
using namespace Lifetime;
int main(){int n=0;auto yes=[&](bool b){if(!b)throw Refused("Actual graph assertion");++n;};auto no=[&](auto f){bool caught=false;try{f();}catch(const Refused&){caught=true;}yes(caught);};using Names=std::set<QString>;
 SourceAliases a({{"/lib","usr/lib"},{"/usr/lib/a.so","a.so.1"},{"/usr/lib/a.so.1","a.so.2"},{"/headers/core","core-v2"}},{});yes(a.select({"/usr/lib/a.so.2"})==Names{"/lib","/usr/lib/a.so","/usr/lib/a.so.1"});
 SourceAliases b({{"/alias","/usr/lib"}},{"/alias/../image"});yes(b.select({})==Names{"/alias"});
 SourceAliases c({{"/usr/bin/python3","python3.14"},{"/headers/only","v3"}},{"/usr/bin/python3"});yes(c.select({"/usr/lib/libc.so.6"})==Names{"/usr/bin/python3"});
 SourceAliases d({{"/usr/lib/a.so","a.so.1"},{"/usr/lib/b.so","b.so.1"}},{});yes(d.select({"/usr/lib/a.so.1"})==Names{"/usr/lib/a.so"});yes(d.select({"/usr/lib/a.so.1","/usr/lib/b.so.1"})==Names{"/usr/lib/a.so","/usr/lib/b.so"});
 no([&]{d.select({"/usr/lib/a.so"});});no([]{SourceAliases x({{"/entry","next"},{"/next","entry"}},{});});no([]{SourceAliases x({{"/entry","../out"}},{});});no([]{SourceAliases x({{"/entry",""}},{});});
 std::map<QString,QString>declared{{"/entry","actual"}};SourceAliases immutable(declared,{"/entry"});declared["/entry"]="changed";yes(immutable.target("/entry")=="actual"&&immutable.select({})==Names{"/entry"});
 SourceAliases unrelated({{"/headers/qobject.h","../qt/qobject.h"}},{});yes(unrelated.select({"/usr/bin/python3.14"}).empty());std::cout<<"{\"result\":\"pass\",\"actualCPPChecks\":"<<n<<",\"GUI\":false}"<<std::endl;
}
