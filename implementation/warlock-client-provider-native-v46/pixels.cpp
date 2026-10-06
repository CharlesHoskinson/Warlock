#include <png.h>
#include <iostream>
#include <vector>
int main(int argc,char** argv){
    if(argc!=2)return 1;
    png_image image{};image.version=PNG_IMAGE_VERSION;
    if(!png_image_begin_read_from_file(&image,argv[1]))return 2;
    if(!image.width || !image.height || image.width>4096 || image.height>4096){png_image_free(&image);return 3;}
    image.format=PNG_FORMAT_RGBA;std::vector<unsigned char> data(PNG_IMAGE_SIZE(image));
    if(!png_image_finish_read(&image,nullptr,data.data(),0,nullptr)){png_image_free(&image);return 4;}
    unsigned long red=0,green=0,blue=0,yellow=0,cyan=0,opaque=0;
    for(size_t i=0;i<data.size();i+=4){auto r=data[i],g=data[i+1],b=data[i+2],a=data[i+3];red+=r>200 && g<40 && b<40 && a>200;green+=g>200 && r<40 && b<40 && a>200;blue+=b>200 && r<40 && g<40 && a>200;yellow+=r>200 && g>200 && b<40 && a>200;cyan+=r<40 && g>200 && b>200 && a>200;opaque+=a>200;}
    std::cout<<"{\"width\":"<<image.width<<",\"height\":"<<image.height<<",\"red\":"<<red<<",\"green\":"<<green<<",\"blue\":"<<blue<<",\"yellow\":"<<yellow<<",\"cyan\":"<<cyan<<",\"opaque\":"<<opaque<<",\"points\":{";
    struct Point{const char* name;unsigned x,y;};Point points[]={{"root",5,5},{"old",22,32},{"moved",102,112},{"nested",108,120}};
    bool first=true;for(const auto& p:points){if(p.x>=image.width || p.y>=image.height)return 5;if(!first)std::cout<<',';first=false;auto i=(size_t(p.y)*image.width+p.x)*4;std::cout<<'"'<<p.name<<"\":["<<unsigned(data[i])<<','<<unsigned(data[i+1])<<','<<unsigned(data[i+2])<<','<<unsigned(data[i+3])<<']';}
    std::cout<<"}}\n";png_image_free(&image);return 0;
}
