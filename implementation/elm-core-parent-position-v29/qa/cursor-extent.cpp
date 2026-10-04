#include "CursorBufferExtent.hpp"
#include <cstdlib>
#include <iostream>
using Pointer::BufferPolicy::cursorBufferSize;
using Pointer::BufferPolicy::PixelSize;
static int checks = 0;
static void check(bool valid) { if (!valid) { std::cerr << "failed check " << checks+1 << '\n'; std::exit(1); } ++checks; }
int main() {
    check(cursorBufferSize(24,20,1,2,0,-1,-1) == PixelSize{48,40});
    check(cursorBufferSize(24,20,2,2,0,-1,-1) == PixelSize{24,20});
    check(cursorBufferSize(24,20,1,2,1,-1,-1) == PixelSize{40,48});
    check(cursorBufferSize(24,20,1,2,0,64,64) == PixelSize{64,64});
    check(!cursorBufferSize(48,40,1,2,0,64,64));
    check(!cursorBufferSize(40,24,1,1,1,48,32));
    check(cursorBufferSize(40,24,1,1,1,32,48) == PixelSize{32,48});
    for (int width=1;width<=96;width+=7) for (int height=1;height<=80;height+=9)
        for (int imageScale : {1,2,4}) for (int outputNumerator : {1,2,3,4,5,6,8,12,16}) for (int transform=0;transform<8;++transform) {
            const int denominator = 4*imageScale;
            int w = (width*outputNumerator+denominator-1)/denominator;
            int h = (height*outputNumerator+denominator-1)/denominator;
            if (transform%2) std::swap(w,h);
            check(cursorBufferSize(width,height,imageScale,outputNumerator/4.0,transform,-1,-1) == PixelSize{w,h});
            check(!cursorBufferSize(width,height,imageScale,outputNumerator/4.0,transform,w-1,h));
        }
    for (double bad : {0.0,-1.0,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}) {
        check(!cursorBufferSize(bad,20,1,1,0,-1,-1));
        check(!cursorBufferSize(24,bad,1,1,0,-1,-1));
        check(!cursorBufferSize(24,20,bad,1,0,-1,-1));
        check(!cursorBufferSize(24,20,1,bad,0,-1,-1));
    }
    for (int transform : {-1,8,100}) check(!cursorBufferSize(24,20,1,1,transform,-1,-1));
    check(!cursorBufferSize(24,20,1,1,0,-1,64));
    check(!cursorBufferSize(24,20,1,1,0,64,-1));
    check(!cursorBufferSize(24,20,1,1,0,64.5,64));
    check(!cursorBufferSize(24,20,1e-300,1e300,0,-1,-1));
    std::cout << "checks: " << checks << '\n';
}
