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
int main(int argc,char** argv){try{
    if(argc!=5)return 1;
    Image family(argv[1]),output(argv[2]);const int cx=number(argv[3]),cy=number(argv[4]);
    if(cx<0 || cy<0 || cx>4096-int(family.width) || cy>4096-int(family.height))throw std::runtime_error("crop origin");
    output.point(cx,cy);output.point(cx+family.width-1,cy+family.height-1);
    size_t compared=0,mismatched=0,opaque=0,partial=0,transparent=0,wrongOutputAlpha=0;
    for(unsigned y=0;y<family.height;++y)for(unsigned x=0;x<family.width;++x){
        const auto i=family.point(x,y),j=output.point(cx+x,cy+y);const unsigned alpha=family.rgba[i+3];bool bad=false;
        for(size_t k=0;k<3;++k){const unsigned expected=(unsigned(family.rgba[i+k])*alpha+127)/255;bad|=expected!=output.rgba[j+k];}
        ++compared;mismatched+=bad;opaque+=alpha==255;transparent+=alpha==0;partial+=alpha>0 && alpha<255;wrongOutputAlpha+=output.rgba[j+3]!=255;
    }
    const auto background=output.point(0,0);const bool blackBackground=output.rgba[background]==0 && output.rgba[background+1]==0 && output.rgba[background+2]==0 && output.rgba[background+3]==255;
    const bool passed=compared>76800 && opaque>=76800 && partial+transparent>0 && mismatched==0 && wrongOutputAlpha==0 && blackBackground;
    std::cout<<"{\"passed\":"<<(passed?"true":"false")<<",\"comparedCropPixels\":"<<compared<<",\"mismatchedCompositedPixels\":"<<mismatched<<",\"opaqueFamilyPixels\":"<<opaque<<",\"partialAlphaFamilyPixels\":"<<partial<<",\"transparentFamilyPixels\":"<<transparent<<",\"wrongNativeOutputAlphaPixels\":"<<wrongOutputAlpha<<",\"independentBackgroundRGBA\":["<<unsigned(output.rgba[background])<<','<<unsigned(output.rgba[background+1])<<','<<unsigned(output.rgba[background+2])<<','<<unsigned(output.rgba[background+3])<<"]}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 3;}}
