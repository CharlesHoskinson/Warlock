#include "tree_revision.hpp"
#include <fstream>
#include <iostream>
int main(int argc,char** argv) {
    if(argc!=2)return 2;
    std::ifstream input(argv[1]);if(!input)return 2;
    preview::TreeRevision actual;uint64_t identity,applied,epoch;int64_t x,y;int valid;size_t states=0;
    while(input>>identity>>applied>>x>>y>>valid>>epoch) {
        std::vector<preview::TreeNode> nodes{{1,0,1,0,0,0,0,true,false}};
        if(identity)nodes.push_back({identity,1,applied,x,y,1,1,true,false});
        if(!valid)nodes.push_back({1,0,1,0,0,0,0,true,false});
        const bool available=actual.observe(std::move(nodes));
        if(available!=bool(valid) || actual.value()!=(valid?epoch:0)) {
            std::cerr<<"Projection mismatch at state "<<states<<" actual "<<actual.value()<<" expected "<<(valid?epoch:0)<<'\n';return 1;
        }
        ++states;
    }
    if(!input.eof() || !states)return 2;
    std::cout<<"{\"passed\":true,\"states\":"<<states<<"}\n";return 0;
}
