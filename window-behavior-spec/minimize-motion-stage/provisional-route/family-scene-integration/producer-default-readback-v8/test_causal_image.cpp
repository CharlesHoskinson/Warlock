#include "CausalImage.hpp"
#include <iostream>
static int checks=0;
static void check(bool condition){++checks;if(!condition)throw std::runtime_error("causal byte contract failed");}
template<class F>static void refuses(F f){bool rejected=false;try{f();}catch(const std::invalid_argument&){rejected=true;}check(rejected);}
int main(){try{
 using namespace OwnedCausal;
 const std::vector<unsigned char> pixels={2,5,7,11,13,17,19,23};
 check(nativeToRGBA(pixels,RGBA,UnsignedByte)==pixels);
 check(nativeToRGBA(pixels,BGRA,UnsignedByte)==std::vector<unsigned char>({7,5,2,11,19,17,13,23}));
 refuses([&]{nativeToRGBA({1,2,3},BGRA,UnsignedByte);});
 refuses([&]{nativeToRGBA(pixels,0x1907,UnsignedByte);});
 refuses([&]{nativeToRGBA(pixels,BGRA,0x8367);});
 check(boundedSampleBytes(320,240,3)==307200);
 refuses([&]{boundedSampleBytes(16384,16384,64);});
 refuses([&]{boundedSampleBytes(320,240,0);});
 refuses([&]{boundedSampleBytes(0,240,3);});
 check(controls()[0]==std::array<unsigned char,4>({100,50,25,255}));
 check(controls()[1]==std::array<unsigned char,4>({10,0,0,128}));
 check(controls()[2]==std::array<unsigned char,4>({0,12,24,64}));
 for(const auto& c:controls())check(c[0]<=c[3]&&c[1]<=c[3]&&c[2]<=c[3]);
 std::cout<<checks<<" causal image checks passed\n";return 0;
 }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
