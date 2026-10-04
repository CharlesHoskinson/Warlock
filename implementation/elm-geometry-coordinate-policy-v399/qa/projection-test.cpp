#include "../candidate/ProspectiveGeometry.hpp"
#include <cstdlib>
#include <iostream>
using namespace Elm::ProspectiveGeometry;
int checks=0;
void check(bool ok) { ++checks; if(!ok){ std::cerr<<"failed check "<<checks<<'\n'; std::exit(1); } }
Input fixture() {
    const double unlimited=std::numeric_limits<double>::max();
    return {Operation::Maximize,{0,0,800,552},{},{{4,6},{8,10}},{0,0},1,
            {{108,42},{0,0}},{{1,1},{unlimited,unlimited}}};
}
int main() {
    auto input=fixture(); auto p=project(input);
    check(p && p->real==CBox{4,6,788,536} && p->configure==Vector2D{788,536});
    input.monitorScale=2; check(project(input)->configure==p->configure);
    input.raw.maximum={790,540};check(project(input).has_value());
    input.raw.maximum.x=780;check(!project(input));
    input=fixture();input.operation=Operation::RestoreOrdinary;input.logical={10,20,320,180};
    check(project(input)->real==input.logical && project(input)->configure==Vector2D{320,180});
    input.raw.minimum.x=400;check(!project(input));
    input=fixture();input.raw.minimum.x=788;input.raw.maximum.x=788;check(!project(input));
    input=fixture();input.layout.minimum.x=788;input.layout.maximum.x=788;check(!project(input));
    input=fixture();input.raw.maximum={1,0};check(!project(input));
    input=fixture();input.reserved.bottomRight={800,552};check(!project(input));
    input=fixture();input.reserved.topLeft.x=3.75;input.raw.minimum.x=788.1;check(!project(input));
    input.raw.minimum.x=788;check(project(input)->real.w==788.25 && project(input)->configure.x==788);
    input.layout.minimum.x=788.3;check(!project(input));
    for(double origin:{-10.0,0.5,10.0}) { input=fixture();input.xdgGeometryOrigin.x=origin;check(!project(input)); }
    for(double bad:{-1.0,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}) {
        input=fixture();input.raw.minimum.x=bad;check(!project(input));
        input=fixture();input.raw.maximum.y=bad;check(!project(input));
        input=fixture();input.reserved.topLeft.x=bad;check(!project(input));
        input=fixture();input.monitorScale=bad;check(!project(input));
    }
    input=fixture();input.logical.rot=1;check(!project(input));
    input=fixture();input.operation=static_cast<Operation>(42);check(!project(input));
    input=fixture();input.logical.w=static_cast<double>(INT_MAX)+1;check(!project(input));
    input=fixture();input.logical.w=0.1;check(!project(input));
    // Independently reproduce the owning Target/WindowTarget operations through
    // its actual math library, then check each raw and real-space bound separately.
    for(double width:{320.1,320.5,320.9,800.25})
    for(double reserve:{0.0,0.25,4.5})
    for(double origin:{-100.5,0.0,100.5})
    for(double minimum:{0.0,108.0,320.0,800.0})
    for(double maximum:{0.0,319.0,320.0,1000.0})
    for(auto operation:{Operation::Maximize,Operation::RestoreOrdinary}) {
        input=fixture();input.operation=operation;input.logical={origin,20.5,width,180.5};
        input.reserved={{reserve,reserve},{reserve,reserve}};
        input.raw={{minimum,0},{maximum,0}};
        CBox expected=input.logical;expected.round();
        if(operation==Operation::Maximize)expected=CBox{expected.pos()+Vector2D{reserve,reserve},expected.size()-Vector2D{2*reserve,2*reserve}};
        const int configured=static_cast<int>(expected.w);
        const bool allowed=(maximum==0 || minimum<maximum) && configured>=minimum && (maximum==0 || configured<=maximum);
        p=project(input);check(p.has_value()==allowed);
        if(p)check(p->real==expected && p->configure.x==configured);
    }
    std::cout<<"checks: "<<checks<<'\n';
}
