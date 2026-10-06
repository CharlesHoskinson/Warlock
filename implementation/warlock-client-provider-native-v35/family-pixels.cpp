#include <png.h>
#include <iostream>
#include <vector>
#include <cstdlib>
int main(int argc,char** argv) {
    if(argc!=2 && argc!=6)return 1;
    png_image image{};image.version=PNG_IMAGE_VERSION;
    if(!png_image_begin_read_from_file(&image,argv[1]))return 2;
    if(!image.width || !image.height || image.width>4096 || image.height>4096){png_image_free(&image);return 3;}
    image.format=PNG_FORMAT_RGBA;std::vector<unsigned char> data(PNG_IMAGE_SIZE(image));
    if(!png_image_finish_read(&image,nullptr,data.data(),0,nullptr)){png_image_free(&image);return 4;}
    unsigned long magenta=0,yellow=0,green=0,red=0,blue=0,cyan=0,opaque=0,interiorMagenta=0,interiorYellow=0,interiorArea=0;
    for(size_t i=0;i<data.size();i+=4){auto r=data[i],g=data[i+1],b=data[i+2],a=data[i+3];magenta+=r>200 && g<40 && b>200 && a>200;yellow+=r>200 && g>200 && b<40 && a>200;green+=r<40 && g>200 && b<40 && a>200;red+=r>200 && g<40 && b<40 && a>200;blue+=r<40 && g<40 && b>200 && a>200;cyan+=r<40 && g>200 && b>200 && a>200;opaque+=a>200;}
    if(argc==6){int x=std::atoi(argv[2]),y=std::atoi(argv[3]),w=std::atoi(argv[4]),h=std::atoi(argv[5]);if(x<0 || y<0 || w<=16 || h<=16 || x+w>int(image.width) || y+h>int(image.height))return 5;
        for(int j=y+8;j<y+h-8;++j)for(int k=x+8;k<x+w-8;++k){auto i=(size_t(j)*image.width+k)*4;auto r=data[i],g=data[i+1],b=data[i+2],a=data[i+3];++interiorArea;interiorMagenta+=r>200 && g<40 && b>200 && a>200;interiorYellow+=r>200 && g>200 && b<40 && a>200;}}
    std::cout<<"{\"width\":"<<image.width<<",\"height\":"<<image.height<<",\"magenta\":"<<magenta<<",\"yellow\":"<<yellow<<",\"green\":"<<green<<",\"red\":"<<red<<",\"blue\":"<<blue<<",\"cyan\":"<<cyan<<",\"opaque\":"<<opaque<<",\"interiorArea\":"<<interiorArea<<",\"interiorMagenta\":"<<interiorMagenta<<",\"interiorYellow\":"<<interiorYellow<<"}\n";
    png_image_free(&image);return 0;
}
