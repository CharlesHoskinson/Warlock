#include "shader_plane.hpp"
#include "/home/hoskinson/omarchy-windows-parity/implementation/warlock-family-style-crop-capture-v13/native/preview_png.hpp"
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
int main(int argc,char** argv){try{
 if(argc!=2)return 1;
 std::ifstream input(argv[1]);if(!input)throw std::runtime_error("trace input");
 double w,h,x,y,cw,ch;uint64_t encoded,limit,expectedPeak;int valid,admitted;size_t states=0;
 while(input>>w>>h>>x>>y>>cw>>ch>>encoded>>limit>>valid>>expectedPeak>>admitted){
  const auto p=warlock::shaderPlanePlan(w,h,x,y,cw,ch,encoded);
  if(bool(p)!=bool(valid) || (p && (p->width!=w || p->height!=h || p->peakBytes!=expectedPeak)))throw std::runtime_error("plan projection");
  preview::capture::Budget budget(limit,1);
  {auto reservation=p?budget.reserve(p->peakBytes):std::nullopt;
   if(bool(reservation)!=bool(admitted))throw std::runtime_error("native capacity admission");
   if(reservation && (budget.used()!=expectedPeak || reservation->bytes()!=expectedPeak || budget.items()!=1))throw std::runtime_error("reservation exact bytes");
   if(reservation && budget.reserve(1))throw std::runtime_error("item capacity");
  }
  if(budget.used()!=0 || budget.items()!=0)throw std::runtime_error("physical reservation retirement");
  ++states;
 }
 if(!input.eof() || !states)throw std::runtime_error("malformed trace");
 for(double bad:{std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),0.0,-1.0,4097.0,800.5}){
  if(warlock::shaderPlanePlan(bad,600,73,73,334,254,1018118))throw std::runtime_error("invalid output dimension");
 }
 if(warlock::shaderPlanePlan(800,600,73.5,73,334,254,1018118) || warlock::shaderPlanePlan(800,600,73,73,334.5,254,1018118))throw std::runtime_error("fractional native pixel geometry");
 std::cout<<"{\"passed\":true,\"states\":"<<states<<",\"nonIntegerControls\":8}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}}
