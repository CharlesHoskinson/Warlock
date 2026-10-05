#include <hyprutils/math/Mat3x3.hpp>
#include <hyprutils/math/Vector2D.hpp>
#include <iostream>
int main(){auto m=Hyprutils::Math::Mat3x3::outputProjection({800,600},Hyprutils::Math::HYPRUTILS_TRANSFORM_NORMAL).getMatrix();std::cout<<'[';for(unsigned i=0;i<9;++i){if(i)std::cout<<',';std::cout<<m[i];}std::cout<<"]\n";}
