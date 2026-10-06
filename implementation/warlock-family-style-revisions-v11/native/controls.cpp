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
    RenderConfiguration config;WindowStyle plain{};plain.id=1;StyleRevision configured;
    check(configured.observe(1,1,{plain},true,config));check(configured.value()==2);
    for(size_t i=0;i<RenderIntegerCount;++i){auto old=configured.value();config.integers[i]=INT64_MIN;check(configured.observe(1,1,{plain},true,config) && configured.value()>old);old=configured.value();check(configured.observe(1,1,{plain},true,config) && configured.value()==old);config.integers[i]=INT64_MAX;check(configured.observe(1,1,{plain},true,config) && configured.value()>old);}
    for(size_t i=0;i<RenderFloatingCount;++i){auto old=configured.value();config.floating[i]=.3;check(configured.observe(1,1,{plain},true,config) && configured.value()>old);old=configured.value();check(configured.observe(1,1,{plain},true,config) && configured.value()==old);auto invalid=config;invalid.floating[i]=std::numeric_limits<double>::quiet_NaN();check(!configured.observe(1,1,{plain},true,invalid) && configured.value()==0);check(!configured.observe(1,1,{plain},true,invalid) && configured.value()==0);check(configured.observe(1,1,{plain},true,config) && configured.value()>old);invalid.floating[i]=std::numeric_limits<double>::infinity();check(!configured.observe(1,1,{plain},true,invalid));check(configured.observe(1,1,{plain},true,config));}
    auto known=configured.value();auto original=config;config.integers[ShadowPower]--;check(configured.value()==known);check(configured.observe(1,1,{plain},true,original) && configured.value()==known);check(configured.observe(1,1,{plain},true,config) && configured.value()>known);
    known=configured.value();config.screenShader="/native/example.glsl";check(configured.observe(1,1,{plain},true,config) && configured.value()>known);known=configured.value();check(configured.observe(1,1,{plain},true,config) && configured.value()==known);auto copied=config;config.screenShader[1]='N';check(configured.value()==known);check(configured.observe(1,1,{plain},true,copied) && configured.value()==known);check(configured.observe(1,1,{plain},true,config) && configured.value()>known);
    for(size_t i=0;i<11;++i){known=configured.value();plain.effectFlags^=uint64_t{1}<<i;check(configured.observe(1,1,{plain},true,config) && configured.value()>known);known=configured.value();check(configured.observe(1,1,{plain},true,config) && configured.value()==known);}
    config.floating[BlurNoise]=0.0;check(configured.observe(1,1,{plain},true,config));known=configured.value();config.floating[BlurNoise]=-0.0;check(configured.observe(1,1,{plain},true,config) && configured.value()>known);
    StyleRevision configuredLast(UINT64_MAX-1);check(configuredLast.observe(1,1,{plain},true,config) && configuredLast.value()==UINT64_MAX);config.integers[GlowPower]--;check(!configuredLast.observe(1,1,{plain},true,config) && configuredLast.value()==0);check(!configuredLast.observe(1,1,{plain},true,config) && configuredLast.value()==0);
    WindowStyle background{};background.id=1;StyleRevision blur;
    check(blur.observe(1,1,{background}));auto blurEpoch=blur.value();background.effectFlags|=uint64_t{1}<<10;
    check(blur.observe(1,1,{background}) && blur.value()>blurEpoch);blurEpoch=blur.value();check(blur.observe(1,1,{background}) && blur.value()==blurEpoch);
    background.blurRegion.push_back({-20,0,100,240});check(blur.observe(1,1,{background}) && blur.value()>blurEpoch);blurEpoch=blur.value();check(blur.observe(1,1,{background}) && blur.value()==blurEpoch);
    auto retainedBackground=background;background.blurRegion[0][2]=120;check(blur.value()==blurEpoch);check(blur.observe(1,1,{retainedBackground}) && blur.value()==blurEpoch);check(blur.observe(1,1,{background}) && blur.value()>blurEpoch);
    for(size_t coordinate=0;coordinate<4;++coordinate){auto changed=background;changed.blurRegion[0][coordinate]+=1;blurEpoch=blur.value();check(blur.observe(1,1,{changed}) && blur.value()>blurEpoch);check(blur.observe(1,1,{background}) && blur.value()>blurEpoch);}
    for(auto invalid:std::vector<std::array<int32_t,4>>{{0,0,0,1},{0,0,1,0},{2,0,1,2},{0,2,2,1}}){auto malformed=background;malformed.blurRegion={invalid};blurEpoch=blur.value();check(!blur.observe(1,1,{malformed}) && blur.value()==0);check(!blur.observe(1,1,{malformed}) && blur.value()==0);check(blur.observe(1,1,{background}) && blur.value()>blurEpoch);}
    auto malformed=background;malformed.effectFlags&=~(uint64_t{1}<<10);check(!blur.observe(1,1,{malformed}) && blur.value()==0);check(blur.observe(1,1,{background}));
    auto bounded=background;bounded.blurRegion.assign(4096,{-20,0,100,240});check(blur.observe(1,1,{bounded}));auto overflowing=bounded;overflowing.blurRegion.push_back({0,0,1,1});check(!blur.observe(1,1,{overflowing}) && blur.value()==0);check(blur.observe(1,1,{bounded}));auto additional=background;additional.id=2;check(!blur.observe(1,1,{bounded,additional}) && blur.value()==0);check(blur.observe(1,1,{background}));
    background.blurRegion.clear();check(blur.observe(1,1,{background}));blurEpoch=blur.value();background.effectFlags&=~(uint64_t{1}<<10);check(blur.observe(1,1,{background}) && blur.value()>blurEpoch);
    WindowStyle nested{};nested.id=1;nested.surfaceEffects={{2,false,{}},{3,false,{}}};StyleRevision tree;
    check(tree.observe(1,1,{nested}));auto treeEpoch=tree.value();nested.surfaceEffects[0].hasEffect=true;check(tree.observe(1,1,{nested}) && tree.value()>treeEpoch);treeEpoch=tree.value();check(tree.observe(1,1,{nested}) && tree.value()==treeEpoch);
    nested.surfaceEffects[0].blurRegion={{0,0,100,200}};check(tree.observe(1,1,{nested}) && tree.value()>treeEpoch);treeEpoch=tree.value();auto retainedTree=nested;nested.surfaceEffects[0].blurRegion[0][2]++;check(tree.value()==treeEpoch);check(tree.observe(1,1,{retainedTree}) && tree.value()==treeEpoch);check(tree.observe(1,1,{nested}) && tree.value()>treeEpoch);
    treeEpoch=tree.value();nested.surfaceEffects[1].hasEffect=true;check(tree.observe(1,1,{nested}) && tree.value()>treeEpoch);treeEpoch=tree.value();nested.surfaceEffects[1].blurRegion={{10,20,110,220}};check(tree.observe(1,1,{nested}) && tree.value()>treeEpoch);treeEpoch=tree.value();check(tree.observe(1,1,{nested}) && tree.value()==treeEpoch);
    treeEpoch=tree.value();nested.surfaceEffects[0].id=4;check(tree.observe(1,1,{nested}) && tree.value()>treeEpoch);treeEpoch=tree.value();nested.rootSurfaceId=5;check(tree.observe(1,1,{nested}) && tree.value()>treeEpoch);
    for(uint64_t invalidID:{uint64_t{0},nested.rootSurfaceId,nested.surfaceEffects[1].id}){auto invalid=nested;invalid.surfaceEffects[0].id=invalidID;treeEpoch=tree.value();check(!tree.observe(1,1,{invalid}) && tree.value()==0);check(!tree.observe(1,1,{invalid}) && tree.value()==0);check(tree.observe(1,1,{nested}) && tree.value()>treeEpoch);}
    auto invalidTree=nested;invalidTree.rootSurfaceId=0;check(!tree.observe(1,1,{invalidTree}));check(tree.observe(1,1,{nested}));invalidTree=nested;invalidTree.surfaceEffects[0].hasEffect=false;check(!tree.observe(1,1,{invalidTree}));check(tree.observe(1,1,{nested}));invalidTree=nested;invalidTree.surfaceEffects[0].blurRegion={{1,1,1,2}};check(!tree.observe(1,1,{invalidTree}));check(tree.observe(1,1,{nested}));
    WindowStyle surfaceBound{};surfaceBound.id=1;for(size_t i=0;i<255;++i)surfaceBound.surfaceEffects.push_back({i+2,false,{}});check(tree.observe(1,1,{surfaceBound}));surfaceBound.surfaceEffects.push_back({257,false,{}});check(!tree.observe(1,1,{surfaceBound}));surfaceBound.surfaceEffects.pop_back();check(tree.observe(1,1,{surfaceBound}));auto secondSurfaceBound=surfaceBound;secondSurfaceBound.id=2;check(!tree.observe(1,1,{surfaceBound,secondSurfaceBound}));check(tree.observe(1,1,{nested}));
    auto regionBound=nested;regionBound.surfaceEffects[0].blurRegion.assign(4095,{0,0,100,200});check(tree.observe(1,1,{regionBound}));regionBound.surfaceEffects[0].blurRegion.push_back({0,0,100,200});check(!tree.observe(1,1,{regionBound}));check(tree.observe(1,1,{nested}));
    StyleRevision shaderRevision;WindowStyle shaderMember{};shaderMember.id=1;RenderConfiguration shaderConfig;
    check(shaderRevision.observe(1,1,{shaderMember},true,shaderConfig));auto shaderEpoch=shaderRevision.value();
    shaderConfig.appliedShader={true,true,false,"vertex A","fragment A"};
    check(shaderRevision.observe(1,1,{shaderMember},true,shaderConfig) && shaderRevision.value()>shaderEpoch);shaderEpoch=shaderRevision.value();
    check(shaderRevision.observe(1,1,{shaderMember},true,shaderConfig) && shaderRevision.value()==shaderEpoch);
    auto retainedShader=shaderConfig;shaderConfig.appliedShader.fragment.back()='B';check(shaderRevision.value()==shaderEpoch);
    check(shaderRevision.observe(1,1,{shaderMember},true,retainedShader) && shaderRevision.value()==shaderEpoch);
    check(shaderRevision.observe(1,1,{shaderMember},true,shaderConfig) && shaderRevision.value()>shaderEpoch);shaderEpoch=shaderRevision.value();
    shaderConfig.appliedShader.vertex.back()='B';check(shaderRevision.observe(1,1,{shaderMember},true,shaderConfig) && shaderRevision.value()>shaderEpoch);
    for(int shape=0;shape<6;++shape){auto invalidShader=shaderConfig;
        if(shape==0)invalidShader.appliedShader.complete=false;
        if(shape==1)invalidShader.appliedShader.contextualUniforms=true;
        if(shape==2)invalidShader.appliedShader.enabled=false;
        if(shape==3)invalidShader.appliedShader.vertex.clear();
        if(shape==4)invalidShader.appliedShader.fragment.clear();
        if(shape==5)invalidShader.appliedShader.fragment.assign(preview::shader::ScreenShaderSourceBudget,'x');
        shaderEpoch=shaderRevision.value();check(!shaderRevision.observe(1,1,{shaderMember},true,invalidShader) && shaderRevision.value()==0);
        check(!shaderRevision.observe(1,1,{shaderMember},true,invalidShader) && shaderRevision.value()==0);
        check(shaderRevision.observe(1,1,{shaderMember},true,shaderConfig) && shaderRevision.value()>shaderEpoch);
    }
    shaderConfig.appliedShader.vertex="v";shaderConfig.appliedShader.fragment.assign(preview::shader::ScreenShaderSourceBudget-1,'f');
    check(shaderRevision.observe(1,1,{shaderMember},true,shaderConfig));shaderEpoch=shaderRevision.value();
    check(shaderRevision.observe(1,1,{shaderMember},true,shaderConfig) && shaderRevision.value()==shaderEpoch);
    shaderConfig.appliedShader.fragment.push_back('f');check(!shaderRevision.observe(1,1,{shaderMember},true,shaderConfig));shaderConfig.appliedShader={};
    check(shaderRevision.observe(1,1,{shaderMember},true,shaderConfig) && shaderRevision.value()>shaderEpoch);shaderEpoch=shaderRevision.value();
    check(shaderRevision.observe(1,1,{shaderMember},true,shaderConfig) && shaderRevision.value()==shaderEpoch);
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
