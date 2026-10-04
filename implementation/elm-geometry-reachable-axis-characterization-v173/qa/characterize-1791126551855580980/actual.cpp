#include <hyprutils/math/Box.hpp>
#include <cmath>
#include <climits>
#include <limits>
#include <iostream>
#include <iomanip>
#include <set>
using Hyprutils::Math::CBox;using Hyprutils::Math::Vector2D;using Hyprutils::Math::SBoxExtents;
namespace Math {constexpr const Vector2D VECTOR2D_MAX={std::numeric_limits<double>::max(),std::numeric_limits<double>::max()};}
struct Goal{Vector2D value;Vector2D goal(){return value;}Vector2D* operator->(){return &value;}};
struct CWindow{bool m_isX11=false;Goal g;Goal* m_realSize=&g;CBox box;Vector2D configured;SBoxExtents reserved;
SBoxExtents getFullWindowReservedArea(){return reserved;}void setBox(CBox b){box=b;g.value=b.size();}void updateWindowDecos(){}void sendWindowSize(){configured=realToReportSize();}Vector2D realToReportSize();};
struct STargetBox{CBox logicalBox,visualBox;};
struct CWindowTarget{STargetBox m_box;CWindow* m_window;void setPositionGlobal(const STargetBox& box);void maximize(bool CONFIGURECLIENT);void ordinary(bool CONFIGURECLIENT);};
Vector2D CWindow::realToReportSize(){
    if (!m_isX11)
        return m_realSize->goal().clamp(Vector2D{0, 0}, Math::VECTOR2D_MAX);


 throw 1; // Uncharacterized X11 path is explicit refusal.
}
void CWindowTarget::setPositionGlobal(const STargetBox& box){
    m_box = box;
    m_box.logicalBox.round();
    m_box.visualBox.round();
}
void CWindowTarget::maximize(bool CONFIGURECLIENT){
            CBox nodeBox   = m_box.logicalBox;
            CBox visualBox = m_box.visualBox.empty() ? nodeBox : m_box.visualBox;
            nodeBox.round();
            visualBox.round();

            // Reserved area must be updated before this is called
            const auto RESERVED = m_window->getFullWindowReservedArea();

            m_window->setBox({visualBox.pos() + RESERVED.topLeft, visualBox.size() - (RESERVED.topLeft + RESERVED.bottomRight)});
        
 m_window->updateWindowDecos();if(CONFIGURECLIENT)m_window->sendWindowSize();
}
void CWindowTarget::ordinary(bool CONFIGURECLIENT){
        m_window->setBox(m_box.logicalBox);

        if (CONFIGURECLIENT)
            m_window->sendWindowSize();
        m_window->updateWindowDecos();

        return;
    }
int checks=0,failures=0;
void check(const char* name,bool value){++checks;std::cout<<(value?"PASS ":"FAIL ")<<name<<"\n";if(!value)++failures;}
struct Limits{double rawLo=0,rawHi=0,layoutLo=0,layoutHi=std::numeric_limits<double>::max();};
bool allowed(double real,double configure,Limits b){return std::isfinite(real)&&real>0&&configure>=1&&configure<=INT_MAX&&configure>=b.rawLo&&(b.rawHi==0||configure<=b.rawHi)&&real>=b.layoutLo&&real<=b.layoutHi;}
std::set<int> reachable(bool max,int axis,int low,int high,SBoxExtents reserve,Limits bounds){
 std::set<int> values;
 for(int n=low;n<=high;++n){CWindow w;w.reserved=reserve;CWindowTarget t;t.m_window=&w;t.setPositionGlobal({CBox{0,0,axis?200.:double(n),axis?double(n):200.},CBox{}});if(max)t.maximize(true);else t.ordinary(true);double real=axis?w.box.h:w.box.w,c=axis?w.configured.y:w.configured.x;if(allowed(real,c,bounds))values.insert(int(c));}
 return values;
}
int main(){
 for(int axis:{0,1}){
  check("zero reserve fractional layout lower reaches one integer",reachable(true,axis,120,140,{}, {0,0,128.9,129.1})==std::set<int>{129});
  check("three integral target values reachable",reachable(true,axis,120,140,{}, {0,0,129,131})==std::set<int>({129,130,131}));
  SBoxExtents r{};if(axis)r.topLeft.y=1.25;else r.topLeft.x=1.25;
  check("fractional reservation gives exact128129 configure set",reachable(true,axis,130,131,r,{})==std::set<int>({128,129}));
  check("raw max129 admits real12975 configure129",reachable(true,axis,131,131,r,{0,129,128.9,130})==std::set<int>{129});
  check("raw min129 rejects real12875 configure128",reachable(true,axis,130,130,r,{129,0,0,200}).empty());
  check("ordinary ignores MAX reservation",reachable(false,axis,130,131,r,{})==std::set<int>({130,131}));
  check("fractional layout min12975 possibleconfigure129",reachable(true,axis,125,135,r,{0,0,129.75,130.1})==std::set<int>{129});
  check("tiny max1 has one reachable configure",reachable(true,axis,1,5,{}, {0,1,0,10})==std::set<int>{1});
  check("tiny max2 has two reachable configure",reachable(true,axis,1,5,{}, {0,2,0,10})==std::set<int>({1,2}));
  check("infeasible cross bounds no reachable size",reachable(true,axis,1,200,{}, {150,0,0,149}).empty());
  check("positive equality has singleton domain before policy refusal",reachable(true,axis,120,140,{}, {128,0,0,128})==std::set<int>{128});
  SBoxExtents negative{};if(axis)negative.bottomRight.y=3.75;else negative.bottomRight.x=3.75;
  check("reservation makes nonpositive real unsupported",reachable(true,axis,1,3,negative,{}).empty());
 }
 {CWindow w;CWindowTarget t;t.m_window=&w;w.reserved={{1,2},{3,4}};t.setPositionGlobal({{-200,-100,900,700},{-10.25,20.25,100.25,80.25}});t.maximize(true);
 check("actual edge aware rounding visual then asymmetric reserve",w.box==CBox{-9,22,96,75});check("configure follows actual real both axes",w.configured==Vector2D{96,75});}
 {CWindow w;CWindowTarget t;t.m_window=&w;w.reserved={{1,2},{3,4}};t.setPositionGlobal({{83.25,61.25,320.25,180.25},{0,0,800,600}});t.ordinary(true);
 check("ordinary uses rounded logical regardless visual",w.box==CBox{83,61,321,181});check("ordinary configure comes from logical real box",w.configured==Vector2D{321,181});}
 {CWindow w;CWindowTarget t;t.m_window=&w;w.reserved={{1e-8,0.},{0,0}};t.setPositionGlobal({{0,0,268435456.,200},{}});t.maximize(true);
 check("IEEE cancellation rejects naive n minus ceil reserve formula",w.configured.x!=268435456.-std::ceil(1e-8));
 std::cout<<"CANCELLATION real="<<std::setprecision(17)<<w.box.w<<" configure="<<w.configured.x<<"\n";}
 {CWindow w;CWindowTarget t;t.m_window=&w;t.setPositionGlobal({{0,0,double(INT_MAX),200},{}});t.maximize(true);check("signed configure ceiling remains exact",w.configured.x==INT_MAX);}
 // Bounded actual conversion grid: one independent definition of membership,
 // not a production eligibility implementation or a proof over all doubles.
 for(int axis:{0,1})for(double reserve:{0.,.25,1.,1.25,2.75})for(double lo:{0.,3.,3.1,5.75})for(double hi:{6.,6.1,8.}){
  SBoxExtents r{};if(axis)r.topLeft.y=reserve;else r.topLeft.x=reserve;
  auto values=reachable(true,axis,1,12,r,{0,0,lo,hi});
  std::set<int> oracle;for(int n=1;n<=12;n++){double real=double(n)-reserve;if(real>0&&real>=lo&&real<=hi&&std::floor(real)>=1)oracle.insert(int(std::floor(real)));}
  check("bounded dyadic reserve axis grid actual library matches direct domain",values==oracle);
 }
 std::cout<<"TOTAL "<<checks<<" FAILED "<<failures<<"\n";return failures?1:0;
}
