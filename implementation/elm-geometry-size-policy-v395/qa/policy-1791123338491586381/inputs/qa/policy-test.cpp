#include "../candidate/SizeBounds.hpp"
#include <iostream>
#include <string>
#include <vector>
using namespace Elm::SizeBounds;
static int checks=0;
static void check(const std::string& name,bool value){++checks;if(!value)throw std::runtime_error(name);}
int main(){try {
 const double inf=std::numeric_limits<double>::infinity(),nan=std::numeric_limits<double>::quiet_NaN(),top=std::numeric_limits<double>::max();
 auto ordinary=derive({{128,64},{0,0}},{});check("GTK minimum-only feasible workarea",ordinary && ordinary->admits({800,552}));
 check("minimum above workarea refused",!ordinary->admits({100,552}));
 for(double upper:{799.,800.,900.}) {auto b=derive({{128,64},{upper,0}},{});check("finite client maximum boundary",b && b->admits({800,552})==(upper>=800));}
 auto raw=derive({{128,64},{900,700}},{Size{150,70},Size{600,600}});check("client and layout lower intersect",raw && raw->horizontal.minimum==150 && raw->vertical.minimum==70);check("client and layout upper intersect",raw && raw->horizontal.maximum==600 && raw->vertical.maximum==600);check("layout cannot bypass client maximum",!raw->admits({800,552}));
 auto contradictory=derive({{500,64},{900,0}},{std::nullopt,Size{400,top}});check("raw minimum versus layout maximum contradiction",!contradictory);
 for(bool horizontal:{false,true}){auto b=derive({{128,64},horizontal?Size{128,0}:Size{0,64}},{});check("one fixed axis refuses resizing",b && !b->resizable() && !b->admits({128,64}));}
 auto changed=derive({{400,64},{0,0}},{});check("new bounds admit workarea but refuse exact original",changed && changed->admits({800,552}) && !changed->admits({320,180}));
 for(double bad:{-1.,inf,nan}) {
  check("invalid raw minimum",!derive({{bad,64},{0,0}},{}));check("invalid raw maximum",!derive({{0,0},{bad,0}},{}));
  check("invalid layout minimum",!derive({{0,0},{0,0}},{Size{0,bad},std::nullopt}));check("invalid layout maximum",!derive({{0,0},{0,0}},{std::nullopt,Size{top,bad}}));
 }
 check("zero effective layout maximum refuses",!derive({{0,0},{0,0}},{std::nullopt,Size{0,top}}));
 auto unlimited=derive({{0,0},{0,0}},{std::nullopt,Size{top,top}});check("unbounded raw zero/layout sentinel",unlimited && !unlimited->horizontal.maximum && unlimited->admits({800,552}));
 check("zero target refused",!unlimited->admits({0,552}));check("nonfinite target refused",!unlimited->admits({inf,552}));
 for(double clientMin:{0.,1.,64.,500.})for(double clientMax:{0.,1.,64.,600.})for(double ruleMin:{0.,2.,100.})for(double ruleMax:{1.,64.,300.,top})for(double target:{1.,64.,128.,552.}){
  auto b=derive({{clientMin,0},{clientMax,0}},{Size{ruleMin,0},Size{ruleMax,top}});
  const double lower=std::max(clientMin,ruleMin);const double upper=std::min(clientMax==0?top:clientMax,ruleMax);
  const bool expected=lower<=target && target<=upper && !(lower>0 && lower==upper);
  check("bounded independent target intersection grid",(b && b->admits({target,180}))==expected);
 }
 std::cout<<"size-policy-checks: "<<checks<<"\n";
}catch(const std::exception& error){std::cerr<<error.what()<<"\n";return 1;}}
