#include "style_revision.hpp"
#include <fstream>
#include <iostream>
int main(int argc,char** argv){try{
    if(argc!=2)return 2;std::ifstream input(argv[1]);preview::StyleRevision revision;uint64_t family,epoch;int tint,alpha,angle,color,count,complete;size_t states=0;
    while(input>>family>>tint>>alpha>>angle>>color>>count>>complete>>epoch){
        std::vector<preview::WindowStyle> members;
        for(int i=0;i<count;++i){preview::WindowStyle member{};member.id=i+1;member.channels[preview::DimPercent]=tint;member.channels[preview::ActiveAlpha]=alpha;member.gradients[0].angle=angle;member.gradients[0].rgba.push_back({double(color),0,0,1});member.gradients[0].shader={double(color),0,0,1};members.push_back(member);}
        const bool actual=revision.observe(complete?1:0,family,std::move(members),complete);
        if(actual!=bool(complete) || revision.value()!=(complete?epoch:0))throw std::runtime_error("Actual style revision differs from selected Quint state "+std::to_string(states));++states;
    }
    std::cout<<"{\"passed\":true,\"states\":"<<states<<"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
