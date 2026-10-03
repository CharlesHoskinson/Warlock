#include "ContinuousTrajectory.hpp"
#include <iostream>
#include <random>
using namespace ContinuousMotion;
static size_t checks=0;
void check(bool ok){++checks;if(!ok)throw std::runtime_error("numeric continuity requirement failed");}
bool near(double a,double b,double tolerance=1e-5){return std::abs(a-b)<=tolerance*std::max({1.0,std::abs(a),std::abs(b)});}
void derivative(const FamilyTrajectory& family,size_t index,double time){
    const double h=family.seconds()*1e-6;
    auto before=family.sample(index,time-h),after=family.sample(index,time+h),actual=family.sample(index,time);
    for(size_t k=0;k<4;++k)check(near((after.rectangle[k]-before.rectangle[k])/(2*h),actual.velocity[k],1e-4));
}
void test(const std::vector<Origin>& sources,double duration){
    FamilyTrajectory family(sources,duration);check(family.seconds()>0&&family.seconds()<=duration&&family.size()==sources.size());
    for(size_t i=0;i<sources.size();++i){
        const auto beginning=family.sample(i,0),end=family.sample(i,family.seconds());
        check(beginning.rectangle==sources[i].rectangle&&beginning.velocity==sources[i].velocity);
        check(end.rectangle==sources[i].target&&end.velocity==Vector{0,0,0,0});
        for(int sample=1;sample<100;++sample){
            const double time=family.seconds()*sample/100;auto state=family.sample(i,time);
            check(state.rectangle[2]>0&&state.rectangle[3]>0);
            derivative(family,i,time);
        }
        // Carry a genuinely sampled interior state into an opposite target.
        auto state=family.sample(i,family.seconds()*.41);
        FamilyTrajectory reversed({Origin{state.rectangle,state.velocity,sources[i].rectangle}},duration);
        auto boundary=reversed.sample(0,0);
        check(boundary.rectangle==state.rectangle&&boundary.velocity==state.velocity);
        const double h=reversed.seconds()*1e-7;auto right=reversed.sample(0,h);
        for(size_t k=0;k<4;++k)check(near((right.rectangle[k]-boundary.rectangle[k])/h,state.velocity[k],2e-3));
    }
}
template<class F>void refuses(F f){bool rejected=false;try{f();}catch(const std::invalid_argument&){rejected=true;}check(rejected);}
int main(){
    // Actual family-sized reversal material, including old shrinking velocity.
    test({{{85,184,405,286},{-225,-982,-2068,-1450},{93,219,474,338}},
          {{221,237,287,188},{-952,-1254,-1432,-905},{253,279,334,218}},
          {{281,271,219,154},{-1270,-1443,-1068,-723},{323,319,254,178}}},.220);
    test({{{0,0,1,1},{-1000,1000,-10000,-10000},{100,100,400,400}}},.220);
    test({{{0,0,20,20},{0,0,0,0},{0,0,20,20}}},.220);
    std::mt19937_64 random(20261001);std::uniform_real_distribution<double> coord(-2000,2000),size(5,1600),speed(-4000,4000),seconds(.03,.4);
    for(int sample=0;sample<2000;++sample){
        std::vector<Origin> sources;
        for(int index=0;index<1+sample%3;++index)sources.push_back({{coord(random),coord(random),size(random),size(random)},
            {speed(random),speed(random),speed(random),speed(random)},
            {coord(random),coord(random),size(random),size(random)}});
        test(sources,seconds(random));
    }
    const Origin good{{0,0,20,20},{0,0,0,0},{100,100,40,40}};
    refuses([&]{FamilyTrajectory({},.22);});
    refuses([&]{FamilyTrajectory({good},0);});
    refuses([&]{auto bad=good;bad.rectangle[2]=0;FamilyTrajectory({bad},.22);});
    refuses([&]{auto bad=good;bad.velocity[0]=NAN;FamilyTrajectory({bad},.22);});
    refuses([&]{auto bad=good;bad.velocity[3]=-1e9;bad.rectangle[3]=1e-12;FamilyTrajectory({bad},.22);});
    refuses([&]{FamilyTrajectory({good},.22).sample(1,0);});
    refuses([&]{FamilyTrajectory({good},.22).sample(0,-1);});
    std::cout<<"{\"result\":\"pass\",\"numericChecks\":"<<checks<<",\"randomFamilies\":2000,\"nativeAccepted\":false}\n";
}
