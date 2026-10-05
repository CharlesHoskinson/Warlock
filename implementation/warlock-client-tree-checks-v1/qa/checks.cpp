#include "tree_revision.hpp"
#include "AppliedSurfaceRevision.hpp"
#include <cassert>
#include <iostream>
#include <limits>
using preview::TreeNode;
using Nodes=std::vector<TreeNode>;
Nodes snapshot(int kind) {
    Nodes nodes{{1,0,1,0,0,0,0,true,false},{2,1,1,12,15,1,1,true,true}};
    switch(kind){
        case 0:break;
        case 1:nodes[0].applied=2;break;
        case 2:nodes[1].applied=2;break;
        case 3:nodes.pop_back();break;
        case 4:nodes[1].id=3;break;
        case 5:nodes[1].x=13;break;
        case 6:nodes[1].order=2;break;
        case 7:nodes[1].sync=false;break;
        case 8:nodes.push_back({3,2,1,14,18,1,1,true,true});break;
        case 9:nodes[1].applied=0;break;
        default:assert(false);
    }
    return nodes;
}
int main(int argc,char**) {
    if(argc>1){preview::TreeRevision tree;int kind;while(std::cin>>kind){bool complete=tree.observe(snapshot(kind));std::cout<<tree.value()<<' '<<complete<<'\n';}return 0;}
    unsigned checks=0;auto check=[&](bool value){assert(value);++checks;};
    Warlock::AppliedRevision applied;check(applied.value()==0);check(applied.apply());check(applied.value()==1);check(applied.apply());check(applied.value()==2);
    Warlock::AppliedRevision limit(std::numeric_limits<uint64_t>::max()-1);check(limit.apply());check(limit.value()==UINT64_MAX);check(!limit.apply());check(limit.value()==0);check(!limit.apply());check(limit.value()==0);
    preview::SourceEpoch epoch(UINT64_MAX);check(!epoch.commit());check(!epoch.available());check(!epoch.commit());
    preview::TreeRevision tree;check(tree.value()==0);check(tree.observe(snapshot(0)));auto first=tree.value();check(first==2);check(tree.observe(snapshot(0)));check(tree.value()==first);
    for(int kind=1;kind<=8;++kind){auto before=tree.value();check(tree.observe(snapshot(kind)));check(tree.value()>before);}
    auto last=tree.value();check(!tree.observe(snapshot(9)));check(tree.value()==0);check(!tree.observe(snapshot(9)));check(tree.observe(snapshot(0)));check(tree.value()>last+1);
    for(int mutation=0;mutation<6;++mutation){auto nodes=snapshot(0);switch(mutation){case 0:nodes[1].id=1;break;case 1:nodes[1].parent=7;break;case 2:nodes[0].parent=1;break;case 3:nodes[0].id=0;break;case 4:nodes.clear();break;case 5:for(uint64_t id=3;id<=257;++id)nodes.push_back({id,1,1,0,0,1,id,true,true});break;}check(!tree.observe(nodes));check(tree.value()==0);check(tree.observe(snapshot(0)));}
    auto unsampled=snapshot(0);unsampled[1].sampled=false;unsampled[1].applied=0;check(tree.observe(unsampled));
    auto same=tree.value();check(tree.observe(unsampled));check(tree.value()==same);check(!tree.observe(unsampled,false));check(tree.value()==0);check(tree.observe(unsampled));check(tree.value()>same);
    std::cout<<"{\"checks\":"<<checks<<"}\n";
}
