#include "../candidate/ProspectiveGeometry.hpp"
#include <iostream>
using namespace Elm::ProspectiveGeometry;
int checks=0,failed=0;
void check(const char* name,bool ok){checks++;std::cout<<(ok?"PASS ":"FAIL ")<<name<<'\n';if(!ok)failed++;}
Input plain(double width=128.0,double height=100.0){
 const double unbounded=std::numeric_limits<double>::max();
 return {Operation::Maximize,{0,0,width,height},{},{{0,0},{0,0}},{0,0},1,
         {{0,0},{0,0}},{{1,1},{unbounded,unbounded}}};
}
int main(){
 auto x=plain();x.raw.minimum.x=128;x.layout.maximum.x=128;
 check("SB004 cross-source rawlower/layoutupper singleton width rejected",!project(x));
 x=plain();x.raw.maximum.x=128;x.layout.minimum.x=128;
 check("SB004 reverse-source layoutlower/rawupper singleton width rejected",!project(x));
 x=plain();x.raw.minimum.y=100;x.layout.maximum.y=100;
 check("either-axis cross-source fixed height rejected",!project(x));
 x=plain();x.raw.maximum.y=100;x.layout.minimum.y=100;
 check("reverse-source fixed height rejected",!project(x));
 x=plain();x.raw.minimum.x=129;x.layout.maximum.x=128;
 check("cross-source empty interval rejected",!project(x));
 x=plain();x.raw.minimum.x=127;x.layout.maximum.x=128;
 check("two-value127..128 interval retains width128",project(x).has_value());
 x=plain();x.raw.maximum.x=129;x.layout.minimum.x=128;
 check("reverse two-value128..129 interval retains width128",project(x).has_value());
 x=plain(131);x.reserved.topLeft.x=1.25;x.raw.maximum.x=129;x.layout.minimum.x=128.9;
 auto p=project(x);
 check("fractional layoutlower real129.75/configure129 fits128..129",p&&p->real.w==129.75&&p->configure.x==129);
 check("raw upper129 must not constrain real129.75 directly",p&&p->real.w>x.raw.maximum.x);
 x=plain(131);x.reserved.topLeft.x=1.25;x.raw.minimum.x=128;x.layout.maximum.x=129.9;
 check("fractional layoutupper real129.75 permits128..129",project(x).has_value());
 x.layout.maximum.x=129.5;check("real dimension still independently respects layoutupper",!project(x));
 x=plain();x.raw.minimum.x=128.1;x.layout.maximum.x=129;
 check("ceil fractional rawlower129 creates singleton with layoutupper129",!project(x));
 x=plain();x.raw.maximum.x=129.9;x.layout.minimum.x=129;
 check("floor fractional rawupper129 creates singleton with layoutlower129",!project(x));
 x=plain(1);x.raw.maximum.x=1;check("tiny rawmax1/default configuremin1 is fixed",!project(x));
 x=plain(2);x.raw.maximum.x=2;check("tiny rawmax2/default configuremin1 remains variable",project(x).has_value());
 x=plain(3);x.raw.maximum.x=3;check("tiny rawmax3 remains bounded variable",project(x).has_value());
 x=plain(4);x.raw.maximum.x=4;check("tiny rawmax4 remains bounded variable",project(x).has_value());
 x=plain();x.raw.minimum.x=128;x.raw.maximum.x=128;check("raw source fixed exclusion retained",!project(x));
 x=plain();x.layout.minimum.x=128;x.layout.maximum.x=128;check("layout source fixed exclusion retained",!project(x));
 for(double bad:{-1.0,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}){
  x=plain();x.raw.minimum.x=bad;check("invalid raw source exclusion retained",!project(x));
  x=plain();x.layout.maximum.y=bad;check("invalid layout source exclusion retained",!project(x));
 }
 x=plain(108,42);x.raw.minimum={108,42};check("GTK108x42 lowerbound/unlimited keeps variable future intervals",project(x).has_value());
 x=plain(800,552);x.reserved={{4,6},{8,10}};x.raw.minimum={108,42};x.raw.maximum={790,540};
 p=project(x);check("decorated MAX unchanged real788x536 fits retained separate limits",p&&p->real==CBox{4,6,788,536}&&p->configure==Vector2D{788,536});
 x.operation=Operation::RestoreOrdinary;x.logical={83,61,320,180};
 p=project(x);check("ordinary restore does not repeat MAX reserve subtraction",p&&p->real==CBox{83,61,320,180}&&p->configure==Vector2D{320,180});
 x.raw.minimum.x=320;x.layout.maximum.x=320;check("restore also rejects cross-source fixed axis",!project(x));
 x=plain(static_cast<double>(INT_MAX));x.raw.minimum.x=INT_MAX-1;x.layout.maximum.x=INT_MAX;
 check("signed-int boundary with two values remains representable",project(x).has_value());
 x.raw.minimum.x=INT_MAX;check("signed-int ceiling singleton rejected",!project(x));
 x=plain();x.raw.minimum.x=std::numeric_limits<double>::max();check("huge finite lower rejected without integer conversion overflow",!project(x));
 x=plain();x.layout.maximum.x=1.9;check("fractional layoutupper with configureonly1 is fixed",!project(x));
 x=plain(2);x.layout.maximum.x=2.1;check("fractional layoutupper allows configure1and2",project(x).has_value());
 std::cout<<"TOTAL "<<checks<<" FAILED "<<failed<<'\n';return failed?1:0;
}
