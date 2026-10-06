#include "family_crop.hpp"
#include <iostream>
#include <limits>
#include <cstdlib>
using namespace preview::capture;
int main() {
    size_t checks=0;auto check=[&](bool value){if(!value){std::cerr<<"Crop assertion "<<checks<<"\n";std::exit(1);}++checks;};
    auto match=[&](std::vector<CropRect> rects,double scale,int64_t x,int64_t y,uint32_t w,uint32_t h){auto p=familyCropPlan(rects,scale);check(bool(p));check(p->pixelX==x && p->pixelY==y && p->image.width==w && p->image.height==h);check(p->image.stride==w*4 && p->image.pixels==uint64_t(w)*h*4);};
    match({{73,73,334,254}},1,73,73,334,254);
    match({{73,73,334,254},{371,291,64,48}},1,73,73,362,266);
    match({{73,73,334,254},{-35,17,10,9}},1,-35,17,442,310);
    match({{73,73,334,254}},2,146,146,668,508);
    match({{-.2,1.1,1.2,1.1}},1.5,-1,1,3,3);
    check(!familyCropPlan({},1));check(!familyCropPlan({std::vector<CropRect>(513,{0,0,1,1})},1));
    check(bool(familyCropPlan({std::vector<CropRect>(512,{0,0,1,1})},1)));
    for(double value:{0.,-1.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})check(!familyCropPlan({std::vector<CropRect>{{0,0,1,1}}},value));
    for(CropRect rect:std::vector<CropRect>{{0,0,0,1},{0,0,1,-1},{0,0,4097,1},{INT32_MAX,0,1,1},{std::numeric_limits<double>::quiet_NaN(),0,1,1}})check(!familyCropPlan({std::vector<CropRect>{rect}},1));
    auto bounded=familyCropPlan({std::vector<CropRect>{{0,0,4096,4096}}},1);check(bool(bounded));Budget budget(128ULL*1024*1024,2);check(!budget.reserve(bounded->image.peak));check(budget.used()==0 && budget.items()==0);
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<"}\n";
}
