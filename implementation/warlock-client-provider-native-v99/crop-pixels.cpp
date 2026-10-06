#include <png.h>
#include <iostream>
#include <vector>
#include <cstdlib>
#include <array>
int main(int argc,char** argv) {
    if(argc!=4 && argc!=8)return 1;
    png_image image{};image.version=PNG_IMAGE_VERSION;
    if(!png_image_begin_read_from_file(&image,argv[1]))return 2;
    if(!image.width || !image.height || image.width>4096 || image.height>4096){png_image_free(&image);return 3;}
    image.format=PNG_FORMAT_RGBA;std::vector<unsigned char> data(PNG_IMAGE_SIZE(image));
    if(!png_image_finish_read(&image,nullptr,data.data(),0,nullptr)){png_image_free(&image);return 4;}
    unsigned long magenta=0,yellow=0,green=0,red=0,blue=0,cyan=0,opaque=0,interiorMagenta=0,interiorYellow=0,interiorArea=0;
    unsigned long styledCyan=0;int left=int(image.width),top=int(image.height),right=-1,bottom=-1;std::array<int,4> styledRGBA{};bool uniform=true;
    for(size_t i=0;i<data.size();i+=4){auto r=data[i],g=data[i+1],b=data[i+2],a=data[i+3];magenta+=r>200 && g<40 && b>200 && a>200;yellow+=r>200 && g>200 && b<40 && a>200;green+=r<40 && g>200 && b<40 && a>200;red+=r>200 && g<40 && b<40 && a>200;blue+=r<40 && g<40 && b>200 && a>200;cyan+=r<40 && g>200 && b>200 && a>200;opaque+=a>200;if(r==0 && g>0 && g==b && a==255){std::array<int,4> color{r,g,b,a};if(!styledCyan)styledRGBA=color;else uniform=uniform && styledRGBA==color;++styledCyan;int x=int((i/4)%image.width),y=int((i/4)/image.width);left=std::min(left,x);right=std::max(right,x);top=std::min(top,y);bottom=std::max(bottom,y);}}
    if(argc==8){int x=std::atoi(argv[4]),y=std::atoi(argv[5]),w=std::atoi(argv[6]),h=std::atoi(argv[7]);if(x<0 || y<0 || w<=16 || h<=16 || x+w>int(image.width) || y+h>int(image.height))return 5;
        for(int j=y+8;j<y+h-8;++j)for(int k=x+8;k<x+w-8;++k){auto i=(size_t(j)*image.width+k)*4;auto r=data[i],g=data[i+1],b=data[i+2],a=data[i+3];++interiorArea;interiorMagenta+=r>200 && g<40 && b>200 && a>200;interiorYellow+=r>200 && g>200 && b<40 && a>200;}}
    const int pointX=std::atoi(argv[2]),pointY=std::atoi(argv[3]);if(pointX<0 || pointY<0 || pointX>=int(image.width) || pointY>=int(image.height))return 6;
    const size_t point=(size_t(pointY)*image.width+pointX)*4;
    std::cout<<"{\"width\":"<<image.width<<",\"height\":"<<image.height<<",\"magenta\":"<<magenta<<",\"yellow\":"<<yellow<<",\"green\":"<<green<<",\"red\":"<<red<<",\"blue\":"<<blue<<",\"cyan\":"<<cyan<<",\"opaque\":"<<opaque<<",\"styledCyan\":"<<styledCyan<<",\"styledCyanUniform\":"<<(uniform?"true":"false")<<",\"styledCyanRGBA\":["<<styledRGBA[0]<<","<<styledRGBA[1]<<","<<styledRGBA[2]<<","<<styledRGBA[3]<<"],\"styledCyanBox\":["<<(styledCyan?left:0)<<","<<(styledCyan?top:0)<<","<<(styledCyan?right-left+1:0)<<","<<(styledCyan?bottom-top+1:0)<<"],\"rootRGBA\":["<<int(data[point])<<","<<int(data[point+1])<<","<<int(data[point+2])<<","<<int(data[point+3])<<"],\"interiorArea\":"<<interiorArea<<",\"interiorMagenta\":"<<interiorMagenta<<",\"interiorYellow\":"<<interiorYellow<<"}\n";
    png_image_free(&image);return 0;
}
