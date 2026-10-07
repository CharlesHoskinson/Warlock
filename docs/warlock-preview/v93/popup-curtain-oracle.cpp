// Independent bounded PNG region observer. It has no native/renderer authority.
#include <png.h>
#include <charconv>
#include <iostream>
#include <string_view>
#include <vector>
int main(int argc,char** argv) {
    if(argc!=6)return 1;
    unsigned box[4]{};
    for(unsigned i=0;i<4;i++) {
        const std::string_view text=argv[i+2];
        const auto parsed=std::from_chars(text.data(),text.data()+text.size(),box[i]);
        if(text.empty() || parsed.ec!=std::errc{} || parsed.ptr!=text.data()+text.size() || box[i]>4096)return 2;
    }
    png_image image{};image.version=PNG_IMAGE_VERSION;
    if(!png_image_begin_read_from_file(&image,argv[1]))return 3;
    if(!image.width || !image.height || image.width>4096 || image.height>4096 || !box[2] || !box[3] ||
       box[0]>image.width || box[1]>image.height || box[2]>image.width-box[0] || box[3]>image.height-box[1]) {png_image_free(&image);return 4;}
    image.format=PNG_FORMAT_RGBA;std::vector<unsigned char> pixels(PNG_IMAGE_SIZE(image));
    if(!png_image_finish_read(&image,nullptr,pixels.data(),0,nullptr)){png_image_free(&image);return 5;}
    unsigned red=0,green=0,blue=0,opaque=0;
    for(unsigned y=box[1];y<box[1]+box[3];y++)for(unsigned x=box[0];x<box[0]+box[2];x++) {
        const auto n=(size_t(y)*image.width+x)*4;const auto r=pixels[n],g=pixels[n+1],b=pixels[n+2],a=pixels[n+3];
        red+=r>200 && g<40 && b<40 && a>200;green+=g>200 && r<40 && b<40 && a>200;blue+=b>200 && r<40 && g<40 && a>200;opaque+=a>200;
    }
    std::cout<<"{\"width\":"<<image.width<<",\"height\":"<<image.height<<",\"region\":["<<box[0]<<','<<box[1]<<','<<box[2]<<','<<box[3]<<"],\"samples\":"<<box[2]*box[3]<<",\"red\":"<<red<<",\"green\":"<<green<<",\"blue\":"<<blue<<",\"opaque\":"<<opaque<<"}\n";
    png_image_free(&image);return 0;
}
