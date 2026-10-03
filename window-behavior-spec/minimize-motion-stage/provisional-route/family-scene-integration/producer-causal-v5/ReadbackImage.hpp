#pragma once
#include <png.h>
#include <algorithm>
#include <cstdio>
#include <cstdint>
#include <fcntl.h>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <vector>
namespace OwnedReadback {
inline std::vector<unsigned char> topLeftRows(const std::vector<unsigned char>& pixels,int width,int height){
    if(width<=0||height<=0||uint64_t(width)*height*4>256*1024*1024||pixels.size()!=uint64_t(width)*height*4)throw std::invalid_argument("readback extent disagrees");
    std::vector<unsigned char> result(pixels.size());const size_t stride=size_t(width)*4;
    for(int y=0;y<height;++y)std::copy_n(pixels.data()+size_t(height-1-y)*stride,stride,result.data()+size_t(y)*stride);
    return result;
}
inline void publishPNG(int directory,const std::string& filename,int width,int height,const std::vector<unsigned char>& topLeft){
    if(filename.empty()||filename.find('/')!=std::string::npos||filename=="."||filename==".."||width<=0||height<=0||topLeft.size()!=uint64_t(width)*height*4)throw std::invalid_argument("invalid readback publication");
    int fd=openat(directory,filename.c_str(),O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0600);if(fd<0)throw std::runtime_error("readback evidence destination exists or unavailable");
    FILE* file=fdopen(fd,"wb");if(!file){close(fd);throw std::runtime_error("readback stream unavailable");}
    png_image image{};image.version=PNG_IMAGE_VERSION;image.width=width;image.height=height;image.format=PNG_FORMAT_RGBA;
    const bool written=png_image_write_to_stdio(&image,file,0,topLeft.data(),0,nullptr);const bool synced=fflush(file)==0&&fsync(fd)==0;const bool closed=fclose(file)==0;
    if(!written||!synced||!closed||fsync(directory)!=0)throw std::runtime_error("readback PNG publication failed");
}
}
