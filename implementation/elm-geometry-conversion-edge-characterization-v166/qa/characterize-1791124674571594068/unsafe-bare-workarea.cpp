
#include <hyprutils/math/Box.hpp>
#include <cmath>
#include <limits>
#include <iostream>
#include <memory>
#include <stdexcept>
using Hyprutils::Math::Vector2D;
using Hyprutils::Math::CBox;
using Hyprutils::Math::SBoxExtents;
namespace Math {     constexpr const Vector2D VECTOR2D_MAX = {std::numeric_limits<double>::max(), std::numeric_limits<double>::max()}; }
struct GeometryOwner { struct {CBox geometry;} m_current; };
struct CXDGToplevelResource {
 struct {Vector2D minSize,maxSize;} m_current;
 GeometryOwner* m_owner=nullptr;
 Vector2D layoutMinSize();Vector2D layoutMaxSize();
};
struct Goal {Vector2D value;Vector2D goal(){return value;}};
struct CWindow {
 bool m_isX11=false;double monitorScale=1;
 Goal goal;Goal* m_realSize=&goal;CBox realBox;SBoxExtents reserved;
 Vector2D configured;int sends=0,decos=0;
 SBoxExtents getFullWindowReservedArea(){return reserved;}
 void setBox(CBox box){realBox=box;goal.value=box.size();}
 void updateWindowDecos(){decos++;}
 void sendWindowSize(){configured=realToReportSize();sends++;}
 Vector2D realToReportSize();
};
struct CWindowTarget {
 struct {CBox logicalBox,visualBox;} m_box;
 CWindow* m_window;
 void characterizeMax(bool CONFIGURECLIENT);
};
Vector2D CXDGToplevelResource::layoutMinSize() {
    Vector2D minSize;
    if (m_current.minSize.x > 1)
        minSize.x = m_owner ? m_current.minSize.x + m_owner->m_current.geometry.pos().x : m_current.minSize.x;
    if (m_current.minSize.y > 1)
        minSize.y = m_owner ? m_current.minSize.y + m_owner->m_current.geometry.pos().y : m_current.minSize.y;
    return minSize;
}
Vector2D CXDGToplevelResource::layoutMaxSize() {
    Vector2D maxSize;
    if (m_current.maxSize.x > 1)
        maxSize.x = m_owner ? m_current.maxSize.x + m_owner->m_current.geometry.pos().x : m_current.maxSize.x;
    if (m_current.maxSize.y > 1)
        maxSize.y = m_owner ? m_current.maxSize.y + m_owner->m_current.geometry.pos().y : m_current.maxSize.y;
    return maxSize;
}
Vector2D CWindow::realToReportSize(){
    if (!m_isX11)
        return m_realSize->goal().clamp(Vector2D{0, 0}, Math::VECTOR2D_MAX);

throw std::runtime_error("X11 excluded");}
void CWindowTarget::characterizeMax(bool CONFIGURECLIENT){m_window->setBox(m_box.logicalBox);        m_window->updateWindowDecos();
        if (CONFIGURECLIENT)
            m_window->sendWindowSize();
        return;}

int total=0,failed=0;
void check(const char* name,bool value){total++;std::cout<<(value?"PASS ":"FAIL ")<<name<<"\n";if(!value)failed++;}
bool vectorEq(Vector2D a,Vector2D b){return a==b;}
bool boxEq(CBox a,CBox b){return vectorEq(a.pos(),b.pos())&&vectorEq(a.size(),b.size());}
int main(){
 CWindow w;CWindowTarget t;t.m_window=&w;
 t.m_box={CBox{0,0,800,600},CBox{}};t.characterizeMax(true);
 check("no-reserve empty visual uses logical box",boxEq(w.realBox,{0,0,800,600}));
 check("actual configure and decoration calls occur once",w.sends==1&&w.decos==1&&vectorEq(w.configured,{800,600}));
 t.m_box={CBox{0,0,800,600},CBox{20,30,700,500}};t.characterizeMax(true);
 check("distinct visual box governs prospective client box",boxEq(w.realBox,{20,30,700,500}));
 check("bare logical workarea control differs",!boxEq(w.realBox,t.m_box.logicalBox));
 w.reserved={{3,7},{5,11}};t.characterizeMax(true);
 check("asymmetric decoration extents applied exactly once",boxEq(w.realBox,{23,37,692,482}));
 check("asymmetric configure uses real client size",vectorEq(w.configured,{692,482}));
 t.m_box={CBox{-200,-100,900,700},CBox{-10.25,20.25,100.25,80.25}};
 w.reserved={{1,2},{3,4}};t.characterizeMax(true);
 std::cout<<"OBSERVED real-box "<<w.realBox.x<<" "<<w.realBox.y<<" "<<w.realBox.w<<" "<<w.realBox.h<<"\n";
 check("fractional negative origin real CBox rounding then reservation",boxEq(w.realBox,{-9,22,96,75}));
 int sends=w.sends;t.characterizeMax(false);
 check("no-client-configure path still updates prospective box",w.sends==sends&&boxEq(w.realBox,{-9,22,96,75}));
 GeometryOwner owner;owner.m_current.geometry={9,13,200,100};CXDGToplevelResource x;x.m_owner=&owner;
 x.m_current.minSize={108,42};x.m_current.maxSize={0,0};
 check("GTK108x42 raw minimum converts with nonzero geometry origin",vectorEq(x.layoutMinSize(),{117,55}));
 check("zero maximum remains zero despite geometry origin",vectorEq(x.layoutMaxSize(),{0,0}));
 x.m_owner=nullptr;check("ownerless GTK minimum stays raw108x42",vectorEq(x.layoutMinSize(),{108,42}));
 x.m_owner=&owner;x.m_current.maxSize={1,1};check("raw positive maximum1 is suppressed by actual layout threshold",vectorEq(x.layoutMaxSize(),{0,0}));
 for(int n=2;n<=4;n++){
  x.m_current.maxSize={n,n};check(("tiny raw maximum "+std::to_string(n)+" adds geometry offset").c_str(),vectorEq(x.layoutMaxSize(),Vector2D{n+9,n+13}));
 }
 owner.m_current.geometry={-8,-3,200,100};x.m_current.maxSize={4,2};
 check("negative geometry origin can produce negative layout maximum",vectorEq(x.layoutMaxSize(),{-4,-1}));
 x.m_current.minSize={0,1};check("zero and1 minimum axes suppressed before geometry offset",vectorEq(x.layoutMinSize(),{0,0}));
 owner.m_current.geometry={0,0,200,100};x.m_current.maxSize={120,80};
 check("zero geometry origin preserves finite maximum",vectorEq(x.layoutMaxSize(),{120,80}));
 w.goal.value={108,42};w.monitorScale=1;check("Waylandscale1 configure size remains logical108x42",vectorEq(w.realToReportSize(),{108,42}));
 w.monitorScale=2;check("Waylandscale2 configure size does not multiply",vectorEq(w.realToReportSize(),{108,42}));
 check("client-times-scale unsafe control differs at scale2",!vectorEq(w.realToReportSize(),w.goal.value*w.monitorScale));
 w.goal.value={-4,42};check("actual Wayland report clamps negative axis to zero",vectorEq(w.realToReportSize(),{0,42}));
 w.goal.value={108.25,42.75};check("Wayland report preserves fractional logical goal",vectorEq(w.realToReportSize(),{108.25,42.75}));
 std::cout<<"TOTAL "<<total<<" FAILED "<<failed<<"\n";return failed?1:0;
}
