#include "style_revision.hpp"
#include <iostream>
#include <limits>
int main(){size_t checks=0;try{
    using namespace preview;
    auto check=[&](bool ok){if(!ok)throw std::runtime_error("style control "+std::to_string(checks));++checks;};
    WindowStyle value{};value.id=1;StyleRevision revision;
    check(revision.observe(1,1,{value}));check(revision.value()==2);check(revision.observe(1,1,{value}) && revision.value()==2);
    for(size_t i=0;i<StyleChannelCount;++i){auto old=revision.value();value.channels[i]=.3;check(revision.observe(1,1,{value}) && revision.value()>old);old=revision.value();check(revision.observe(1,1,{value}) && revision.value()==old);}
    for(size_t i=0;i<12;++i){auto old=revision.value();value.flags^=uint64_t{1}<<i;check(revision.observe(1,1,{value}) && revision.value()>old);}
    for(size_t i=0;i<6;++i){auto& g=value.gradients[i];auto old=revision.value();g.rgba.push_back({.1,.2,.3,1});g.shader={.1,.2,.3,1};check(revision.observe(1,1,{value}) && revision.value()>old);old=revision.value();g.angle=.2;check(revision.observe(1,1,{value}) && revision.value()>old);old=revision.value();g.shader[0]=.4;check(revision.observe(1,1,{value}) && revision.value()>old);old=revision.value();g.rgba[0][0]=.5;check(revision.observe(1,1,{value}) && revision.value()>old);}
    auto before=revision.value();check(revision.observe(1,2,{value}) && revision.value()>before);
    auto bad=value;bad.channels[DimPercent]=std::numeric_limits<double>::quiet_NaN();check(!revision.observe(1,2,{bad}) && revision.value()==0);check(!revision.observe(1,2,{bad}) && revision.value()==0);check(revision.observe(1,2,{value}) && revision.value()>before);
    for(size_t i=0;i<6;++i){bad=value;bad.gradients[i].angle=std::numeric_limits<double>::infinity();check(!revision.observe(1,2,{bad}) && revision.value()==0);check(revision.observe(1,2,{value}));bad=value;bad.gradients[i].shader.clear();check(!revision.observe(1,2,{bad}));check(revision.observe(1,2,{value}));bad=value;bad.gradients[i].rgba[0][0]=std::numeric_limits<double>::quiet_NaN();check(!revision.observe(1,2,{bad}));check(revision.observe(1,2,{value}));bad=value;bad.gradients[i].shader[0]=std::numeric_limits<double>::infinity();check(!revision.observe(1,2,{bad}));check(revision.observe(1,2,{value}));}
    check(!revision.observe(1,2,{}));check(!revision.observe(1,2,{value,value}));check(!revision.observe(2,2,{value}));check(!revision.observe(1,0,{value}));
    std::vector<WindowStyle> many;
    for(size_t i=0;i<256;++i){auto v=value;v.id=i+1;many.push_back(v);}
    check(revision.observe(1,2,many));auto extra=value;extra.id=257;many.push_back(extra);check(!revision.observe(1,2,many) && revision.value()==0);check(revision.observe(1,2,{value}));
    StyleRevision exhausted(UINT64_MAX);check(!exhausted.observe(1,1,{value}) && exhausted.value()==0);check(!exhausted.observe(1,1,{value}) && exhausted.value()==0);exhausted.unavailable();check(!exhausted.observe(1,1,{value}) && exhausted.value()==0);
    StyleRevision last(UINT64_MAX-1);check(last.observe(1,1,{value}) && last.value()==UINT64_MAX);check(last.observe(1,1,{value}) && last.value()==UINT64_MAX);check(!last.observe(1,2,{value}) && last.value()==0);
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
