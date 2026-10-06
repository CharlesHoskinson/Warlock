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
    if(rw<=16 || rh<=16 || first.width!=second.width || first.height!=second.height || outputFirst.width!=outputSecond.width || outputFirst.height!=outputSecond.height)throw std::runtime_error("geometry dimensions");
    size_t compared=0,changedFamily=0,changedOutput=0,mismatchedBefore=0,mismatchedAfter=0,changedCenter=0;
    for(int y=ry;y<ry+rh;++y)for(int x=rx;x<rx+rw;++x){
        const auto i=first.point(x-cx,y-cy),j=outputFirst.point(x,y);
        bool a=false,b=false,m1=false,m2=false;
        for(size_t k=0;k<4;++k){a|=first.rgba[i+k]!=second.rgba[i+k];b|=outputFirst.rgba[j+k]!=outputSecond.rgba[j+k];m1|=first.rgba[i+k]!=outputFirst.rgba[j+k];m2|=second.rgba[i+k]!=outputSecond.rgba[j+k];}
        ++compared;changedFamily+=a;changedOutput+=b;mismatchedBefore+=m1;mismatchedAfter+=m2;
        if(x>=rx+8 && x<rx+rw-8 && y>=ry+8 && y<ry+rh-8)changedCenter+=a || b;
    }
    const bool passed=changedFamily>0 && changedOutput==changedFamily && mismatchedBefore==0 && mismatchedAfter==0 && changedCenter==0;
    std::cout<<"{\"passed\":"<<(passed?"true":"false")<<",\"comparedRootPixels\":"<<compared<<",\"changedFamilyPixels\":"<<changedFamily<<",\"changedOutputPixels\":"<<changedOutput<<",\"mismatchedBefore\":"<<mismatchedBefore<<",\"mismatchedAfter\":"<<mismatchedAfter<<",\"changedCenterPixels\":"<<changedCenter<<"}\n";
    return passed?0:2;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 3;}}
