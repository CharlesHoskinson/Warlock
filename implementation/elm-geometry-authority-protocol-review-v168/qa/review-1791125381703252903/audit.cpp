#include "ProspectiveGeometry.hpp"
int main(){using namespace Elm::ProspectiveGeometry;const double top=std::numeric_limits<double>::max();
Input i{Operation::Maximize,{0,0,128,180},{},{},{0,0},1,{{128,0},{0,0}},{{1.,1.},{128.,top}}};
auto p=project(i);if(!p || p->configure.x!=128)return 1;
i.logical={0,0,800,180};if(project(i))return 2;
i.raw={{64,0},{0,0}};i.layout={{1.,1.},{top,top}};if(!project(i))return 3;
}