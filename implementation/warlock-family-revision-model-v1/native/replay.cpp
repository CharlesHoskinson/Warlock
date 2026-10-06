#include "family_revision.hpp"
#include <fstream>
#include <iostream>
int main(int argc,char** argv) {
    if(argc!=2)return 2;
    std::ifstream input(argv[1]);if(!input)return 2;
    preview::FamilyRevision actual;uint64_t id,content,epoch;int64_t x,y;int linked,modal,invalid;size_t states=0;
    while(input>>id>>content>>x>>y>>linked>>modal>>invalid>>epoch) {
        std::vector<preview::FamilyNode> nodes{{1,0,1,0,0,{0,0,320,240,0,0,320,240},{1,0,2}}};
        if(id && linked)nodes.push_back({id,invalid==1?id:1,content,1,modal?64ULL:0ULL,{double(x),double(y),96,64,double(x),double(y),96,64},{1,0,2}});
        if(invalid==2)for(uint64_t i=3;i<=257;++i)nodes.push_back({i,1,1,i-1,0,{0,0,1,1,0,0,1,1},{1,0,2}});
        const bool available=actual.observe(1,std::move(nodes));
        if(available!=(invalid==0) || actual.value()!=(invalid?0:epoch)) {
            std::cerr<<"Projection mismatch at state "<<states<<" actual "<<actual.value()<<" expected "<<(invalid?0:epoch)<<'\n';return 1;
        }
        ++states;
    }
    if(!input.eof() || !states)return 2;
    std::cout<<"{\"passed\":true,\"states\":"<<states<<"}\n";return 0;
}
