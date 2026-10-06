#pragma once
#include "source_epoch.hpp"
#include <array>
#include <cmath>
#include <map>
#include <set>
#include <vector>
namespace preview {
struct FamilyNode {
    uint64_t id=0,parent=0,content=0,order=0,flags=0;
    std::array<double,8> geometry{};
    std::array<double,3> appearance{};
    bool operator==(const FamilyNode&)const=default;
};
// Native membership/content/geometry projection only. This does not represent
// every decoration/shader/animation input and must not authorize those claims.
class FamilyRevision {
    SourceEpoch epoch_;std::vector<FamilyNode> nodes_;uint64_t root_=0;bool complete_=false;
public:
    bool observe(uint64_t root,std::vector<FamilyNode> nodes,bool complete=true) {
        if(!root || nodes.empty() || nodes.size()>256){nodes.clear();complete=false;}
        std::map<uint64_t,uint64_t> parents;size_t roots=0;
        for(const auto& node:nodes) {
            if(!node.id || !node.content || node.order>255 || !parents.emplace(node.id,node.parent).second)complete=false;
            if(!node.parent){++roots;if(node.id!=root)complete=false;}
            for(double value:node.geometry)if(!std::isfinite(value) || std::abs(value)>INT32_MAX)complete=false;
            if(node.geometry[2]<=0 || node.geometry[3]<=0 || node.geometry[6]<=0 || node.geometry[7]<=0)complete=false;
            for(double value:node.appearance)if(!std::isfinite(value))complete=false;
        }
        if(roots!=1 || !parents.contains(root))complete=false;
        for(const auto& node:nodes) {
            std::set<uint64_t> seen;uint64_t current=node.id;
            while(current && current!=root) {
                const auto found=parents.find(current);
                if(found==parents.end() || !seen.insert(current).second || seen.size()>256){complete=false;break;}
                current=found->second;
            }
            if(current!=root)complete=false;
        }
        if(root!=root_ || nodes!=nodes_ || complete!=complete_){epoch_.commit();root_=root;nodes_=std::move(nodes);complete_=complete;}
        return complete_ && epoch_.available();
    }
    uint64_t value()const noexcept{return complete_ && epoch_.available()?epoch_.value():0;}
    void unavailable(){observe(root_,{},false);}
};
}
