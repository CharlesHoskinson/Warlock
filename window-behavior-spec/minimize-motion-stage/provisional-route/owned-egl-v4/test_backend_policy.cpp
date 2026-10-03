#include "BackendPolicy.hpp"
#include <cassert>
#include <iostream>
using namespace OwnedRoute;
int main(){int checks=0;auto check=[&](bool value){assert(value);++checks;};
 check(reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 Mesa 26.2.2 (Arch build)","AMD Radeon RX 7900 XTX (radeonsi, gfx1100, LLVM 20.1)"));
 check(reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 Mesa 26.2.2","Mesa Intel(R) Arc Graphics"));
 for(auto renderer:{"llvmpipe (LLVM20)","softpipe","swrast","Software Rasterizer","SWR (LLVM20)","zink (RADV)","Zink Vulkan"})check(!reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 Mesa 26.2.2",renderer));
 check(!reviewedGPUBackend("NVIDIA","OpenGL ES 3.2 Mesa 26.2.2","hardware"));
 check(!reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 Mesa 26.3.0","radeonsi"));
 check(!reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 Mesa 26.2.2",""));
 check(!reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 Mesa 26.2.20","radeonsi"));
 check(!reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 Mesa 26.2.2-devel","radeonsi"));
 check(!reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 NotMesa 26.2.2","radeonsi"));
 check(reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 Mesa 26.2.2-arch1.1","Mesa Intel(R) Graphics"));
 check(!reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 Mesa 26.2.2-arch1.11","Mesa Intel(R) Graphics"));
 check(!reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 Mesa 26.2.2-arch1.1-devel","Mesa Intel(R) Graphics"));
 check(!reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 Mesa 26.2.2-arch1.1","llvmpipe (LLVM)"));
 check(!reviewedGPUBackend("Mesa Project","OpenGL ES 3.2 Mesa 26.2.2-arch1.1","zink Vulkan"));
 std::cout<<checks<<" reviewed GPU backend policy checks PASS\n";
}
