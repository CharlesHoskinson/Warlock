
#include "EffectBarrier.hpp"
#include <cstdio>
#include <set>
#include <utility>
using Elm::Geometry::Target;
using Elm::Geometry::Barriers;
unsigned checks=0;
bool check(bool value,const char*name){++checks;if(!value)std::fprintf(stderr,"FAIL %s\n",name);return value;}
#define REQUIRE(v,n) if(!check((v),(n)))return 1
int main(){
 Barriers b;
 REQUIRE(!b.begin({0,1})&&!b.begin({1,0})&&!b.begin({0,0}),"zero identities refuse without capacity use");
 REQUIRE(b.begin({7,11})&&b.blocked({7,11}),"reservation blocks exact native target");
 REQUIRE(!b.begin({7,11}),"duplicate operation cannot reserve again");
 REQUIRE(!b.blocked({8,11})&&!b.blocked({7,12}),"native lifetime/incarnation isolated");
 // No peer, frontend or effect version exists in the production key. A new
 // transport caller sees the same unresolved target and cannot reacquire it.
 REQUIRE(!b.begin({7,11}),"new caller cannot bypass unresolved target");
 b.definitive({8,11});b.retire({7,12});
 REQUIRE(b.blocked({7,11}),"unrelated receipts/retirements cannot clear Unknown");
 b.definitive({7,11});REQUIRE(!b.blocked({7,11})&&b.begin({7,11}),"definitive readback permits new reservation");
 b.retire({7,11});REQUIRE(!b.blocked({7,11}),"exact native retirement releases target");
 for(unsigned i=1;i<=256;++i)REQUIRE(b.begin({9,i}),"all256 slots usable");
 REQUIRE(!b.begin({9,257}),"full capacity refuses without eviction");
 for(unsigned i=1;i<=256;++i)REQUIRE(b.blocked({9,i}),"full refusal preserves prior unresolved targets");
 b.retire({9,128});REQUIRE(b.begin({9,257})&&!b.blocked({9,128}),"exact retirement permits one slot reuse");
 for(unsigned i=1;i<=257;++i)b.retire({9,i});
 // A fixed deterministic production replay against an independent mathematical
 // set. This is CPU evidence, not compositor reentrancy/retirement qualification.
 std::set<std::pair<unsigned long long,unsigned long long>> oracle;
 unsigned long long state=0x8d8bd43a74638a91ULL;
 for(unsigned i=0;i<50000;++i){state=state*6364136223846793005ULL+1442695040888963407ULL;
  Target target{(state>>48)%4,(state>>16)%340};auto key=std::make_pair(target.lifetime,target.incarnation);
  switch(state%4){
   case 0:{bool expected=target.lifetime&&target.incarnation&&!oracle.contains(key)&&oracle.size()<256;
    bool actual=b.begin(target);REQUIRE(actual==expected,"random begin matches independent set/capacity oracle");if(expected)oracle.insert(key);break;}
   case 1:b.definitive(target);oracle.erase(key);break;
   case 2:b.retire(target);oracle.erase(key);break;
   case 3:REQUIRE(b.blocked(target)==oracle.contains(key),"random lookup matches independent oracle");break;
  }
  for(const auto& entry:oracle)REQUIRE(b.blocked({entry.first,entry.second}),"remaining reservations never evicted");
 }
 std::printf("checks %u\n",checks);return 0;
}
