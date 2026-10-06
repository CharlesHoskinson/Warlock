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
    if(argc!=9)return 1;
    Image family(argv[1]),output(argv[2]);
    const int cx=number(argv[3]),cy=number(argv[4]),rx=number(argv[5]),ry=number(argv[6]),rw=number(argv[7]),rh=number(argv[8]);
    if(rw<=0 || rh<=0 || rw>4096 || rh>4096 || cx<0 || cy<0 || rx<cx || ry<cy || rx>4096-rw || ry>4096-rh)throw std::runtime_error("geometry dimensions");
    family.point(rx-cx,ry-cy);family.point(rx+rw-1-cx,ry+rh-1-cy);output.point(rx,ry);output.point(rx+rw-1,ry+rh-1);
    size_t compared=0,mismatched=0,wrongAlpha=0;unsigned redMin=255,redMax=0,greenMin=255,greenMax=0;
    for(int y=ry;y<ry+rh;++y)for(int x=rx;x<rx+rw;++x){
        const auto i=family.point(x-cx,y-cy),j=output.point(x,y);bool bad=false;
        for(size_t k=0;k<4;++k)bad|=family.rgba[i+k]!=output.rgba[j+k];
        ++compared;mismatched+=bad;wrongAlpha+=family.rgba[i+3]!=255 || output.rgba[j+3]!=255;
        redMin=std::min(redMin,unsigned(output.rgba[j]));redMax=std::max(redMax,unsigned(output.rgba[j]));
        greenMin=std::min(greenMin,unsigned(output.rgba[j+1]));greenMax=std::max(greenMax,unsigned(output.rgba[j+1]));
    }
    const bool passed=compared==76800 && mismatched==0 && wrongAlpha==0 && redMin<redMax && greenMin<greenMax;
    std::cout<<"{\"passed\":"<<(passed?"true":"false")<<",\"comparedRootPixels\":"<<compared<<",\"mismatchedRootPixels\":"<<mismatched<<",\"wrongAlphaPixels\":"<<wrongAlpha<<",\"nativeRedRange\":["<<redMin<<','<<redMax<<"],\"nativeGreenRange\":["<<greenMin<<','<<greenMax<<"]}\n";return passed?0:2;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 3;}}
