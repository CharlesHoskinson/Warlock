#include "../candidate/ReachableAxis.hpp"
#include "/home/hoskinson/omarchy-windows-parity/implementation/elm-geometry-coordinate-policy-v402/candidate/ProspectiveGeometry.hpp"
#include <iostream>
#include <random>
#include <vector>
using namespace Elm::ExperimentalReachableAxis;
namespace P=Elm::ProspectiveGeometry;
int main(){
 std::mt19937_64 rng(176179);int checked=0;
 for(int trial=0;trial<20000;++trial){
  int64_t start=trial%2?1+rng()%1000:int64_t(INT_MAX)-40-rng()%1000;
  double reserve=trial%3==0?1e-8:(trial%3==1?double(rng()%100)/4.:std::max(0.,double(start)-double(rng()%30)/4.));
  double center=double(start+16)-reserve;
  double lower=std::max(0.,center-double(rng()%20)/4.);
  double upper=std::max(lower+.25,center+double(rng()%20)/4.);
  double rawMin=double(rng()%2?std::max(0.,std::floor(center)-double(rng()%6)):0.);
  double rawMax=rng()%2?std::max(rawMin+1.,std::floor(center)+double(rng()%6)):0.;
  bool restore=trial%5==0;Input in{start,start+31,restore?0.:reserve,rawMin,rawMax,lower,upper};
  std::vector<int64_t> ns;std::vector<double> cs;
  for(int64_t n=in.first;n<=in.last;++n){
   P::Input p{restore?P::Operation::RestoreOrdinary:P::Operation::Maximize,P::CBox{0.,0.,double(n),300.},P::CBox{},
    P::SBoxExtents{P::Vector2D{reserve,0.},P::Vector2D{0.,0.}},P::Vector2D{0.,0.},1.,
    P::Bounds{P::Vector2D{rawMin,0.},P::Vector2D{rawMax,0.}},P::Bounds{P::Vector2D{lower,0.},P::Vector2D{upper,1000.}}};
   auto r=P::project(p);if(r){ns.push_back(n);cs.push_back(r->configure.x);}
  }
  auto r=solve(in);
  if(bool(r)!=!ns.empty()||(r&&(r->first!=ns.front()||r->last!=ns.back()||r->firstConfigure!=cs.front()||r->lastConfigure!=cs.back()))){std::cerr<<"mismatch seed176179 trial"<<trial<<" domain "<<start<<" reserve "<<reserve<<" bounds "<<rawMin<<','<<rawMax<<','<<lower<<','<<upper<<" restore "<<restore<<" found "<<bool(r)<<" enum "<<ns.size()<<'\n';return 1;}
  ++checked;
 }
 auto cancellation=solve({268435456,268435457,1e-8,0.,0.,0.,double(INT_MAX)});
 if(!cancellation||cancellation->firstConfigure!=268435456)return 2;
 std::cout<<"PASS "<<checked+1<<" deterministic precision/search cases, seed176179; no native acceptance\n";
}
