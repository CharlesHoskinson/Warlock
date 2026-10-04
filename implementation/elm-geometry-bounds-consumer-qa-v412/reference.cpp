#include "ProspectiveGeometry.hpp"
#include <iomanip>
#include <iostream>
using namespace Elm::ProspectiveGeometry;
void box(CBox b) { std::cout<<'['<<b.x<<','<<b.y<<','<<b.w<<','<<b.h<<']'; }
int main() {
    std::cout<<std::setprecision(17);
    const double infinity=std::numeric_limits<double>::max();
    for(double width:{320.1,320.5,800.25})
    for(double x:{-9.75,-0.5,0.49999999999999994})
    for(double reserve:{0.0,3.75})
    for(double scale:{1.0,2.0}) {
        const CBox area{x,22.5,width,180.5};
        Input input{Operation::Maximize,area,{},{{reserve,reserve},{reserve,reserve}},{0,0},scale,{{108,42},{0,0}},{{1,1},{infinity,infinity}}};
        auto p=project(input);if(!p)return 1;
        std::cout<<"{\"workArea\":";box(area);
        std::cout<<",\"reserve\":"<<reserve<<",\"scale\":"<<scale<<",\"projection\":{\"logical\":";box(p->logical);
        std::cout<<",\"visual\":null,\"real\":";box(p->real);
        std::cout<<",\"configure\":["<<p->configure.x<<','<<p->configure.y<<"]}}\n";
    }
}
