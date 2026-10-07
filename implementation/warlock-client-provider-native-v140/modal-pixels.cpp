#include <png.h>
#include <iostream>
#include <vector>
int main(int argc,char** argv) {
    if(argc!=2)return 1;
    png_image image{};image.version=PNG_IMAGE_VERSION;
    if(!png_image_begin_read_from_file(&image,argv[1]))return 2;
    if(!image.width || !image.height || image.width>4096 || image.height>4096){png_image_free(&image);return 3;}
    image.format=PNG_FORMAT_RGBA;std::vector<unsigned char> data(PNG_IMAGE_SIZE(image));
    if(!png_image_finish_read(&image,nullptr,data.data(),0,nullptr)){png_image_free(&image);return 4;}
    unsigned long magenta=0,yellow=0,green=0,opaque=0;
    for(size_t i=0;i<data.size();i+=4){auto r=data[i],g=data[i+1],b=data[i+2],a=data[i+3];magenta+=r>200 && g<40 && b>200 && a>200;yellow+=r>200 && g>200 && b<40 && a>200;green+=r<40 && g>200 && b<40 && a>200;opaque+=a>200;}
    std::cout<<"{\"width\":"<<image.width<<",\"height\":"<<image.height<<",\"magenta\":"<<magenta<<",\"yellow\":"<<yellow<<",\"green\":"<<green<<",\"opaque\":"<<opaque<<"}\n";
    png_image_free(&image);return 0;
}
