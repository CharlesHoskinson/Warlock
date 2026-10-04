#include "../candidate/ReachableAxis.hpp"
#include "/home/hoskinson/omarchy-windows-parity/implementation/elm-geometry-coordinate-policy-v402/candidate/ProspectiveGeometry.hpp"
#include <iostream>
#include <vector>
using namespace Elm::ExperimentalReachableAxis;
namespace P=Elm::ProspectiveGeometry;
int main(){
 int checks=0;
 for(double reserved:{0.,.25,1.,1.25,7.9})for(double lower:{0.,1.,12.9,128.9})for(double upper:{13.1,129.1,200.})for(double rawMin:{0.,1.,12.,128.})for(double rawMax:{0.,2.,129.,200.})for(bool restore:{false,true})for(bool vertical:{false,true}){
  Input in{1,220,restore?0.:reserved,rawMin,rawMax,lower,upper};
  std::vector<int64_t> ns;std::vector<double> cs;
  for(int64_t n=in.first;n<=in.last;++n){
   P::Input p{restore?P::Operation::RestoreOrdinary:P::Operation::Maximize,
    P::CBox{0.,0.,vertical?300.:double(n),vertical?double(n):300.},P::CBox{},
    P::SBoxExtents{P::Vector2D{vertical?0.:reserved,vertical?reserved:0.},P::Vector2D{0.,0.}},
    P::Vector2D{0.,0.},1.,
    P::Bounds{P::Vector2D{vertical?0.:rawMin,vertical?rawMin:0.},P::Vector2D{vertical?0.:rawMax,vertical?rawMax:0.}},
    P::Bounds{P::Vector2D{vertical?0.:lower,vertical?lower:0.},P::Vector2D{vertical?1000.:upper,vertical?upper:1000.}}};
   auto r=P::project(p);if(r){ns.push_back(n);cs.push_back(vertical?r->configure.y:r->configure.x);}
  }
  auto result=solve(in);
  if(bool(result)!=!ns.empty()||(result&&(result->first!=ns.front()||result->last!=ns.back()||result->firstConfigure!=cs.front()||result->lastConfigure!=cs.back()))){std::cerr<<"enumeration mismatch "<<reserved<<' '<<lower<<' '<<upper<<' '<<rawMin<<' '<<rawMax<<' '<<restore<<'\n';return 1;}
  ++checks;
 }
 auto singleton=solve({1,220,0.,0.,0.,128.9,129.1});
 if(!singleton||singleton->variable()||singleton->first!=129||singleton->last!=129)return 2;
 ++checks;
 auto cancellation=solve({268435456,268435457,1e-8,0.,0.,0.,double(INT_MAX)});
 if(!cancellation||cancellation->firstConfigure!=268435456||double(268435456)-std::ceil(1e-8)==cancellation->firstConfigure)return 3;
 ++checks;
 auto edge=solve({int64_t(INT_MAX),int64_t(INT_MAX)+1,1.,0.,0.,0.,double(INT_MAX)});
 if(!edge||edge->last!=int64_t(INT_MAX)+1||edge->lastConfigure!=INT_MAX)return 4;
 ++checks;
 for(auto x:{Input{0,10,0.,0.,0.,0.,10.},Input{1,10,-1.,0.,0.,0.,10.},Input{1,10,0.,2.,2.,0.,10.},Input{1,10,0.,0.,0.,5.,5.}}){if(solve(x))return 5;++checks;}
 std::cout<<"PASS "<<checks<<" checks; actual owning project enumeration; no native acceptance\n";
}
