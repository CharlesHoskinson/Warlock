#include <algorithm>
#include <cmath>
#include <png.h>
#include <charconv>
#include <iostream>
#include <stdexcept>
#include <string_view>
#include <vector>
struct Image {
    unsigned width{},height{};std::vector<unsigned char> rgba;
    explicit Image(const char* path){
        png_image image{};image.version=PNG_IMAGE_VERSION;
        if(!png_image_begin_read_from_file(&image,path))throw std::runtime_error("PNG read");
        if(!image.width || !image.height || image.width>4096 || image.height>4096){png_image_free(&image);throw std::runtime_error("PNG dimensions");}
        width=image.width;height=image.height;image.format=PNG_FORMAT_RGBA;rgba.resize(PNG_IMAGE_SIZE(image));
        const bool ok=png_image_finish_read(&image,nullptr,rgba.data(),0,nullptr);png_image_free(&image);if(!ok)throw std::runtime_error("PNG decode");
    }
    size_t point(int x,int y)const{if(x<0 || y<0 || x>=int(width) || y>=int(height))throw std::runtime_error("pixel bounds");return (size_t(y)*width+x)*4;}
};
int number(const char* input){int result{};std::string_view s=input;auto [end,error]=std::from_chars(s.begin(),s.end(),result);if(error!=std::errc{} || end!=s.end())throw std::runtime_error("geometry");return result;}
#include <map>
#include <array>
int main(int argc,char** argv){if(argc!=3)return 1;Image f(argv[1]),o(argv[2]);std::map<std::array<int,8>,unsigned> pairs;for(int y=80;y<320;++y)for(int x=80;x<400;++x){auto i=f.point(x-73,y-73),j=o.point(x,y);std::array<int,8> a{};for(int k=0;k<4;++k){a[k]=f.rgba[i+k];a[k+4]=o.rgba[j+k];}++pairs[a];}for(const auto& [a,n]:pairs){std::cout<<n;for(auto k:a)std::cout<<" "<<k;std::cout<<"\n";}}
