#include "ParentNormalizedPosition.hpp"
#include <cstdlib>
#include <iostream>
#include <limits>
using namespace Pointer::ParentPolicy;
static int checks=0;
void check(bool valid) { if (!valid) { std::cerr<<"failed check "<<checks+1<<'\n';std::exit(1); } ++checks; }
int main() {
    NormalizedPosition p;
    check(!p.project({0,0,800,600}));
    check(p.remember(317.0/800,238.0/600));
    auto q=p.project({0,0,400,300});
    check(q && q->x==158.5 && q->y==119);
    q=p.project({100,-200,400,300});
    check(q && q->x==258.5 && q->y==-81);
    p.clear();check(!p.project({0,0,800,600}));
    check(p.remember(-1,2));check(p.point==Point{0,1});
    for (int ix=0;ix<=100;++ix) for (int iy=0;iy<=100;++iy) {
        check(p.remember(ix/100.0,iy/100.0));
        for (int size : {100,200,400,800}) {
            auto projected=p.project({-300,700,double(size),double(size)/2});
            const auto expectedX=-300+double(size)*ix/100;
            const auto expectedY=700+double(size)*iy/200;
            check(projected && std::abs(projected->x-expectedX)<1e-9 && std::abs(projected->y-expectedY)<1e-9);
        }
        p.clear();check(!p.project({0,0,400,300}));
    }
    for (double bad : {std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}) {
        check(p.remember(.5,.5));check(!p.remember(bad,.5));check(!p.point);
        check(p.remember(.5,.5));check(!p.remember(.5,bad));check(!p.point);
    }
    check(p.remember(.5,.5));
    check(!p.project({0,0,0,600}));check(!p.project({0,0,800,-1}));
    check(!p.project({std::numeric_limits<double>::infinity(),0,800,600}));
    check(!p.project({0,0,std::numeric_limits<double>::infinity(),600}));
    check(p.remember(1,1));check(!p.project({1e308,1e308,1e308,1e308}));
    std::cout<<"checks: "<<checks<<'\n';
}
