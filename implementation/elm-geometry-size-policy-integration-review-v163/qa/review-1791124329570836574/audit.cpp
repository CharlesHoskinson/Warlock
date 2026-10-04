#include "SizeBounds.hpp"
int main(){using namespace Elm::SizeBounds; double nan=std::numeric_limits<double>::quiet_NaN(),top=std::numeric_limits<double>::max();
auto good=derive({{128,64},{0,0}},{});if(!good || !good->admits({800,552}))return 1;
auto tiny=derive({{0,0},{1,0}},{std::nullopt,Size{top,top}});if(!tiny || tiny->admits({800,552}))return 2;
if(derive({{0,0},{0,0}},{Size{nan,0},std::nullopt}))return 3;
auto unsafe=intersect(0,0,nan,top);if(!unsafe || !unsafe->admits(800))return 4;
}