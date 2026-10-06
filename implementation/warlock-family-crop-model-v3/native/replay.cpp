#include "family_crop.hpp"
#include <fstream>
#include <iostream>
using namespace preview::capture;
int main(int argc,char** argv){
 if(argc!=2)return 2;
 std::ifstream input(argv[1]);long n,x,y,w,h,px,py,pw,ph,scale,valid,ox,oy,width,height;size_t states=0;
 while(input>>n>>x>>y>>w>>h>>px>>py>>pw>>ph>>scale>>valid>>ox>>oy>>width>>height){
  std::vector<CropRect> rects(n,CropRect{double(x),double(y),double(w),double(h)});
  if(n>1)rects.back()=CropRect{double(px),double(py),double(pw),double(ph)};
  auto result=familyCropPlan(rects,double(scale));
  if(bool(result)!=bool(valid) || (result && (result->pixelX!=ox || result->pixelY!=oy || int64_t(result->image.width)!=width || int64_t(result->image.height)!=height))){std::cerr<<"Crop projection mismatch "<<states<<"\n";return 1;}
  if(result){const auto p=plan(width,height);if(!p || result->image.pixels!=p->pixels || result->image.png!=p->png || result->image.peak!=p->peak)return 1;}
  ++states;
 }
 if(!input.eof() || !states)return 3;
 std::cout<<"{\"passed\":true,\"states\":"<<states<<"}\n";
}
