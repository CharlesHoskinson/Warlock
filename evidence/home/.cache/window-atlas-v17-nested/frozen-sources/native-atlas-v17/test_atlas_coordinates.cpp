#include "atlasCoordinates.hpp"
#include <cassert>
#include <iostream>
using namespace AtlasCoordinates;
static bool same(const CBox& a,const CBox& b) {return std::abs(a.x-b.x)<1e-7 && std::abs(a.y-b.y)<1e-7 && std::abs(a.w-b.w)<1e-7 && std::abs(a.h-b.h)<1e-7;}
int main() {
 const Vector2D outputPixels{1000,760};const int inverse[]={0,3,2,1,4,5,6,7};
 int cases=0;
 for(double scale:{1.,1.5,2.})for(int transform=0;transform<8;transform++)for(Vector2D nativePosition:{Vector2D{200,250},Vector2D{-4,120},Vector2D{880,180}}) {
  const Vector2D offset{std::floor((nativePosition.x-4)*scale),std::floor((nativePosition.y-30)*scale)};
  const CBox outputBox{nativePosition.x*scale,nativePosition.y*scale,380*scale,240*scale};
  const CBox atlas=pixelBox(outputBox,offset);const auto logical=logicalPosition(nativePosition,offset,scale);
  assert(std::abs(logical.x*scale-atlas.x)<1e-7 && std::abs(logical.y*scale-atlas.y)<1e-7);
  const bool swapped=transform==1 || transform==3 || transform==5 || transform==7;
  const Vector2D transformedSize=swapped?Vector2D{outputPixels.y,outputPixels.x}:outputPixels;
  const CBox shader=atlas.copy().transform(static_cast<eTransform>(inverse[transform]),transformedSize.x,transformedSize.y);
  assert(same(canonicalShaderBox(shader,transform,outputPixels),atlas));
  assert(outputBox.x==nativePosition.x*scale && outputBox.y==nativePosition.y*scale);
  cases++;
 }
 bool rejected=false;try{logicalPosition({}, {},0);}catch(const std::runtime_error&){rejected=true;}assert(rejected);
 std::cout<<cases<<" exact Hyprutils scale/transform/edge/gap coordinate cases PASS\n";
}
