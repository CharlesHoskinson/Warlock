#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <functional>
#include <map>
#include <set>
#include <string>
#include <vector>

// Bottom-to-top snapshot policy. No recovered owner, focus action, pin-bit
// mutation or layout action belongs here. The adapter retains strong owners.
namespace PinStacking {
using Key=uintptr_t;
struct Node {
 Key key=0,parent=0,workspace=0,monitor=0;
 uint64_t stable=0,generation=0;
 int pid=0;
 bool eligible=false,pinned=false,floating=false,modal=false,x11=false,fullscreen=false;
 bool nativeAdmission=false,restoreOrigin=false,coreProtected=false;
 int internalMode=0,clientMode=0;
 std::array<double,4> geometry{};
 bool operator==(const Node&)const=default;
};
struct Snapshot {
 uint64_t epoch=0;Key focus=0,coreSurface=0,keyboardSurface=0,keyboardResource=0,pointerSurface=0;
 std::vector<Node> nodes;
 bool operator==(const Snapshot&)const=default;
};
struct Plan {bool ok=false;std::string reason;std::vector<Key> order;std::set<Key> protectedKeys;};
inline bool contextSame(const Snapshot&a,const Snapshot&b){
 if(a.epoch!=b.epoch||a.focus!=b.focus||a.coreSurface!=b.coreSurface||a.keyboardSurface!=b.keyboardSurface||a.keyboardResource!=b.keyboardResource||a.pointerSurface!=b.pointerSurface||a.nodes.size()!=b.nodes.size())return false;
 std::map<Key,Node> x,y;
 for(const auto&n:a.nodes)if(!x.emplace(n.key,n).second)return false;
 for(const auto&n:b.nodes)if(!y.emplace(n.key,n).second)return false;
 return x==y;
}
inline Plan makePlan(const Snapshot&s){
 Plan p;
 if(!s.epoch||s.nodes.size()>512){p.reason="Unavailable epoch or bounded window count exceeded";return p;}
 std::map<Key,Node> nodes;std::map<Key,size_t> rank;
 for(size_t i=0;i<s.nodes.size();++i){const auto&n=s.nodes[i];
  if(!n.key||!n.generation||n.pid<=0||!nodes.emplace(n.key,n).second){p.reason="Missing/duplicate exact native lifetime";return p;}
  rank[n.key]=i;
 }
 // A true parent cycle is invalid even if a cycle currently has no pin bit.
 for(const auto&[key,_]:nodes){std::set<Key> visited;auto k=key;
  while(nodes.contains(k)){if(!visited.insert(k).second){p.reason="Native parent cycle";return p;}k=nodes.at(k).parent;}
 }
 auto attached=[&](const Node&n){
  if(!n.eligible||!nodes.contains(n.parent))return false;
  const auto&parent=nodes.at(n.parent);
  return parent.eligible&&parent.workspace==n.workspace&&parent.monitor==n.monitor&&(n.modal||(n.x11&&parent.x11));
 };
 for(const auto&[key,n]:nodes)if(n.eligible&&((n.pinned&&n.floating&&!n.fullscreen)||(n.pinned&&n.nativeAdmission&&n.clientMode<=1&&n.internalMode<=1)||n.coreProtected))p.protectedKeys.insert(key);
 for(size_t pass=0;pass<s.nodes.size();++pass){bool change=false;
  for(const auto&[key,n]:nodes)if(!p.protectedKeys.contains(key)&&attached(n)&&p.protectedKeys.contains(n.parent)){p.protectedKeys.insert(key);change=true;}
  if(!change)break;
 }
 std::map<Key,std::vector<Key>> children;std::vector<Key> roots;
 for(Key key:p.protectedKeys){const auto&n=nodes.at(key);
  if(attached(n)&&p.protectedKeys.contains(n.parent))children[n.parent].push_back(key);else roots.push_back(key);
 }
 std::function<size_t(Key)> topRank=[&](Key key){size_t r=rank.at(key);for(Key c:children[key])r=std::max(r,topRank(c));return r;};
 auto byTop=[&](Key a,Key b){return topRank(a)<topRank(b);};
 std::sort(roots.begin(),roots.end(),byTop);
 std::function<void(Key)> append=[&](Key key){p.order.push_back(key);auto list=children[key];std::sort(list.begin(),list.end(),byTop);for(Key c:list)append(c);};
 for(Key root:roots)append(root);
 p.ok=true;return p;
}
inline bool satisfied(const Snapshot&s,const Plan&p){
 if(!p.ok)return false;
 std::vector<Key> protectedOrder;bool sawProtected=false;
 for(const auto&n:s.nodes){if(!n.eligible)continue;
  if(p.protectedKeys.contains(n.key)){sawProtected=true;protectedOrder.push_back(n.key);}
  else if(sawProtected)return false;
 }
 return protectedOrder==p.order;
}
struct Report {bool ok=false,actionsInvoked=false;size_t calls=0;std::string reason;Plan plan;};
template<class Adapter>Report enforce(Adapter&a){
 Report r;const auto captured=a.snapshot();r.plan=makePlan(captured);
 if(!r.plan.ok){r.reason=r.plan.reason;return r;}
 if(satisfied(captured,r.plan)){r.ok=true;return r;}
 for(Key key:r.plan.order){
  if(!contextSame(captured,a.snapshot())){r.reason="Native lifetime/state/focus changed during stacking pass";return r;}
  r.actionsInvoked=true;++r.calls;
  if(!a.raise(key)){r.reason="Owning core raise refused";return r;}
  if(!contextSame(captured,a.snapshot())){r.reason="Native lifetime/state/focus changed in raise callback";return r;}
 }
 const auto after=a.snapshot();
 r.ok=contextSame(captured,after)&&satisfied(after,r.plan);
 if(!r.ok)r.reason="Bounded stacking pass did not preserve exact protected order";
 return r;
}
}
