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
    if(argc!=11)return 1;
    Image first(argv[1]),second(argv[2]),outputFirst(argv[3]),outputSecond(argv[4]);
    const int cx=number(argv[5]),cy=number(argv[6]),rx=number(argv[7]),ry=number(argv[8]),rw=number(argv[9]),rh=number(argv[10]);
    if(rw<=0 || rh<=0 || rw>4096 || rh>4096 || cx<0 || cy<0 || rx<cx || ry<cy || rx>4096-rw || ry>4096-rh || first.width!=second.width || first.height!=second.height || outputFirst.width!=outputSecond.width || outputFirst.height!=outputSecond.height)throw std::runtime_error("geometry dimensions");
    first.point(rx-cx,ry-cy);first.point(rx+rw-1-cx,ry+rh-1-cy);outputFirst.point(rx,ry);outputFirst.point(rx+rw-1,ry+rh-1);
    size_t compared=0,changedFamily=0,changedOutput=0,mismatchedDeltas=0,wrongAlpha=0;
    for(int y=ry;y<ry+rh;++y)for(int x=rx;x<rx+rw;++x){
        const auto i=first.point(x-cx,y-cy),j=outputFirst.point(x,y);
        bool changed1=false,changed2=false,bad=false;
        for(size_t k=0;k<4;++k){changed1|=first.rgba[i+k]!=second.rgba[i+k];changed2|=outputFirst.rgba[j+k]!=outputSecond.rgba[j+k];}
        for(size_t k=0;k<3;++k){
            const int before=(unsigned(first.rgba[i+k])*first.rgba[i+3]+127)/255;
            const int after=(unsigned(second.rgba[i+k])*second.rgba[i+3]+127)/255;
            bad|=after-before!=int(outputSecond.rgba[j+k])-int(outputFirst.rgba[j+k]);
        }
        ++compared;changedFamily+=changed1;changedOutput+=changed2;mismatchedDeltas+=bad;
        wrongAlpha+=first.rgba[i+3]!=second.rgba[i+3] || outputFirst.rgba[j+3]!=255 || outputSecond.rgba[j+3]!=255;
    }
    const auto p=outputFirst.point(0,0);bool background=true;
    for(size_t k=0;k<4;++k)background &= outputFirst.rgba[p+k]==outputSecond.rgba[p+k] && outputFirst.rgba[p+k]==(k==0?204:255);
    const bool passed=compared==76800 && changedOutput>0 && changedFamily==changedOutput && mismatchedDeltas==0 && wrongAlpha==0 && background;
    std::cout<<"{\"passed\":"<<(passed?"true":"false")<<",\"comparedBodyPixels\":"<<compared<<",\"changedFamilyPixels\":"<<changedFamily<<",\"changedNativeOutputPixels\":"<<changedOutput<<",\"mismatchedRGBDeltaPixels\":"<<mismatchedDeltas<<",\"wrongAlphaPixels\":"<<wrongAlpha<<",\"independentUnchangedTintedWhiteBackdrop\":"<<(background?"true":"false")<<"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 3;}}
