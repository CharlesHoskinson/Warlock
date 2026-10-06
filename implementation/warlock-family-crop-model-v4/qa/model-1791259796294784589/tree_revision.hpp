#pragma once
#include "source_epoch.hpp"
#include <vector>
#include <set>
namespace preview {
struct TreeNode {
    uint64_t id=0,parent=0,applied=0;int64_t x=0,y=0,z=0;uint64_t order=0;bool sampled=false,sync=false;
    bool operator==(const TreeNode&)const=default;
};
class TreeRevision {
    SourceEpoch epoch_;std::vector<TreeNode> nodes_;bool complete_=false;
public:
    bool observe(std::vector<TreeNode> nodes,bool complete=true) {
        if(nodes.empty() || nodes.size()>256)complete=false;
        std::set<uint64_t> seen;
        for(size_t i=0;i<nodes.size();++i){const auto& n=nodes[i];if(!n.id || (n.sampled && !n.applied) || seen.contains(n.id) || (i==0?n.parent!=0:!seen.contains(n.parent)))complete=false;seen.insert(n.id);}
        if(complete!=complete_ || nodes!=nodes_){epoch_.commit();nodes_=std::move(nodes);complete_=complete;}
        return available();
    }
    bool available()const noexcept{return complete_ && epoch_.available();}
    uint64_t value()const noexcept{return available()?epoch_.value():0;}
};
}
