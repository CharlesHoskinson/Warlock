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
    size_t compared=0,changedFamily=0,changedOutput=0,mismatchedBefore=0,mismatchedAfter=0,wrongAlpha=0,redPixels=0,bluePixels=0,unexpectedPixels=0;
    for(int y=ry;y<ry+rh;++y)for(int x=rx;x<rx+rw;++x){
        const auto i=first.point(x-cx,y-cy),j=outputFirst.point(x,y);
        bool changed1=false,changed2=false,bad1=false,bad2=false;
        for(size_t k=0;k<4;++k){
            changed1|=first.rgba[i+k]!=second.rgba[i+k];changed2|=outputFirst.rgba[j+k]!=outputSecond.rgba[j+k];
            bad1|=first.rgba[i+k]!=outputFirst.rgba[j+k];bad2|=second.rgba[i+k]!=outputSecond.rgba[j+k];
        }
        const bool red=first.rgba[i]==255 && first.rgba[i+1]==0 && first.rgba[i+2]==0 && second.rgba[i]==204 && second.rgba[i+1]==0 && second.rgba[i+2]==0;
        const bool blue=first.rgba[i]==0 && first.rgba[i+1]==0 && first.rgba[i+2]==255 && second.rgba[i]==0 && second.rgba[i+1]==0 && second.rgba[i+2]==255;
        ++compared;changedFamily+=changed1;changedOutput+=changed2;mismatchedBefore+=bad1;mismatchedAfter+=bad2;
        wrongAlpha+=first.rgba[i+3]!=255 || second.rgba[i+3]!=255 || outputFirst.rgba[j+3]!=255 || outputSecond.rgba[j+3]!=255;
        redPixels+=red;bluePixels+=blue;unexpectedPixels+=!red && !blue;
    }
    const bool passed=compared==76800 && changedFamily==73728 && changedOutput==changedFamily && mismatchedBefore==0 && mismatchedAfter==0 && wrongAlpha==0 && bluePixels==3072 && redPixels==73728 && unexpectedPixels==0;
    std::cout<<"{\"passed\":"<<(passed?"true":"false")<<",\"comparedRootPixels\":"<<compared<<",\"changedFamilyPixels\":"<<changedFamily<<",\"changedOutputPixels\":"<<changedOutput<<",\"mismatchedBefore\":"<<mismatchedBefore<<",\"mismatchedAfter\":"<<mismatchedAfter<<",\"wrongAlphaPixels\":"<<wrongAlpha<<",\"redPixels\":"<<redPixels<<",\"unchangedBlueChildPixels\":"<<bluePixels<<",\"unexpectedFixturePixels\":"<<unexpectedPixels<<"}\n";
    return passed?0:2;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 3;}}
