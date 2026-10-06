#include <png.h>
#include <array>
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
};
int number(const char* input){int result{};std::string_view s=input;auto [end,error]=std::from_chars(s.begin(),s.end(),result);if(error!=std::errc{} || end!=s.end())throw std::runtime_error("geometry");return result;}
struct Delta {size_t changed{},inside{};};
Delta delta(const Image& before,const Image& after,int originX,int originY,int rootX,int rootY,int rootW,int rootH){
    if(before.width!=after.width || before.height!=after.height)throw std::runtime_error("changing dimensions");
    Delta result;
    for(size_t i=0;i<before.rgba.size();i+=4){
        bool changed=false;for(size_t k=0;k<4;++k)changed|=before.rgba[i+k]!=after.rgba[i+k];if(!changed)continue;
        ++result.changed;const int x=int((i/4)%before.width)+originX,y=int((i/4)/before.width)+originY;
        result.inside+=x>=rootX+8 && x<rootX+rootW-8 && y>=rootY+8 && y<rootY+rootH-8;
    }
    return result;
}
int main(int argc,char** argv){try{
    if(argc!=11)return 1;
    Image first(argv[1]),second(argv[2]),outputFirst(argv[3]),outputSecond(argv[4]);
    const int x=number(argv[5]),y=number(argv[6]),rx=number(argv[7]),ry=number(argv[8]),rw=number(argv[9]),rh=number(argv[10]);
    if(rw<=16 || rh<=16)throw std::runtime_error("root dimensions");
    const auto family=delta(first,second,x,y,rx,ry,rw,rh),output=delta(outputFirst,outputSecond,0,0,rx,ry,rw,rh);
    const bool passed=family.changed>0 && output.changed>0 && family.inside==0 && output.inside==0;
    std::cout<<"{\"passed\":"<<(passed?"true":"false")<<",\"changedFamilyPixels\":"<<family.changed<<",\"changedOutputPixels\":"<<output.changed<<",\"changedFamilyInterior\":"<<family.inside<<",\"changedOutputInterior\":"<<output.inside<<"}\n";
    return passed?0:2;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 3;}}
