#pragma once
#include <cstdint>
#include <limits>
#include <map>
#include <algorithm>
// Strong/Weak are the compositor's public window owner types. No raw-owner recovery.
template<class Strong,class Weak>class PinLifetime {
 struct Entry {Weak owner;uint64_t generation;bool retired;};
 std::map<void*,Entry> entries_;
 uint64_t next_=0;
 void prune(){std::erase_if(entries_,[](const auto&pair){return !pair.second.owner.lock();});}
 uint64_t fresh(const Strong&owner){
  if(next_==std::numeric_limits<uint64_t>::max())return 0;
  const auto value=++next_;entries_[owner.get()]={owner,value,false};return value;
 }
 public:
 explicit PinLifetime(uint64_t initial=0):next_(initial){}
 uint64_t query(const Strong&owner,bool mapped,bool create){
  if(!owner||!mapped)return 0;
  prune();const auto found=entries_.find(owner.get());
  if(found!=entries_.end()&&found->second.owner.lock()==owner)return found->second.retired?0:found->second.generation;
  return create?fresh(owner):0;
 }
 uint64_t opened(const Strong&owner,bool mapped){
  if(!owner||!mapped)return 0;
  prune();const auto found=entries_.find(owner.get());
  if(found!=entries_.end()&&found->second.owner.lock()==owner&&!found->second.retired)return found->second.generation;
  return fresh(owner);
 }
 void closed(const Strong&owner){
  if(!owner)return;
  prune();const auto found=entries_.find(owner.get());
  if(found!=entries_.end()&&found->second.owner.lock()==owner)found->second.retired=true;
  else entries_[owner.get()]={owner,0,true};
 }
 void clear(){entries_.clear();next_=0;}
};
