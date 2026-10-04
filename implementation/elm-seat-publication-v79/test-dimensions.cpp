#include "BufferDimensions.hpp"
#include <cassert>
#include <initializer_list>
#include <limits>
using namespace Aquamarine::NestedPolicy;
int main() {
    assert(bufferMatchesMode(800,600,800,600));
    assert(!bufferMatchesMode(960,640,800,600)); // retained oversized buffer after shrink
    assert(!bufferMatchesMode(640,480,800,600)); // retained undersized buffer after growth
    assert(!bufferMatchesMode(800,640,800,600));
    assert(!bufferMatchesMode(960,600,800,600));
    assert(bufferMatchesMode(960,640,960,640)); // independent of parent geometry contract
    for (double invalid : {0., -1., 0.5, std::numeric_limits<double>::infinity(), std::numeric_limits<double>::quiet_NaN(), 2147483648.}) {
        assert(!validPixelDimensions(invalid,600));
        assert(!validPixelDimensions(800,invalid));
        assert(!bufferMatchesMode(invalid,600,800,600));
        assert(!bufferMatchesMode(800,invalid,800,600));
    }
}
