#pragma once
#include "ReadbackImage.hpp"
#include <array>
namespace OwnedCausal {
constexpr unsigned RGBA=0x1908,BGRA=0x80e1,UnsignedByte=0x1401;
inline void validateReadPair(unsigned format,unsigned type){
    if((format!=RGBA&&format!=BGRA)||type!=UnsignedByte)
        throw std::invalid_argument("unsupported diagnostic native read pair");
}
inline std::vector<unsigned char> nativeToRGBA(std::vector<unsigned char> bytes,unsigned format,unsigned type){
    validateReadPair(format,type);if(bytes.size()%4)throw std::invalid_argument("partial native RGBA pixel");
    if(format==BGRA)for(size_t i=0;i<bytes.size();i+=4)std::swap(bytes[i],bytes[i+2]);
    return bytes;
}
inline uint64_t boundedSampleBytes(int width,int height,size_t members){
    if(width<=0||height<=0||members<1||members>64)throw std::invalid_argument("invalid causal scene extent/count");
    const uint64_t bytes=uint64_t(width)*height*4;
    // Three constant controls and every real prefix, in two read formats.
    if(bytes>256*1024*1024ULL/(2*(members+3)))throw std::invalid_argument("aggregate causal sample exceeded");
    return bytes;
}
inline const std::array<std::array<unsigned char,4>,3>& controls(){
    static const std::array<std::array<unsigned char,4>,3> colors={{{100,50,25,255},{10,0,0,128},{0,12,24,64}}};
    return colors;
}
}
