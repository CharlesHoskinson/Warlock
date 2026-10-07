#include <png.h>
#include <array>
#include <charconv>
#include <iostream>
#include <string_view>
#include <vector>

int main(int argc,char** argv) {
    if(argc!=6)return 2;
    std::array<unsigned,4> expected{};
    for(size_t i=0;i<4;++i) {
        const std::string_view text=argv[i+2];
        const auto parsed=std::from_chars(text.data(),text.data()+text.size(),expected[i]);
        if(parsed.ec!=std::errc{} || parsed.ptr!=text.data()+text.size() || expected[i]>255)return 2;
    }
    png_image image{};image.version=PNG_IMAGE_VERSION;
    if(!png_image_begin_read_from_file(&image,argv[1]))return 3;
    if(!image.width || !image.height || image.width>4096 || image.height>4096){png_image_free(&image);return 3;}
    image.format=PNG_FORMAT_RGBA;
    std::vector<unsigned char> pixels(PNG_IMAGE_SIZE(image));
    if(!png_image_finish_read(&image,nullptr,pixels.data(),0,nullptr)){png_image_free(&image);return 3;}
    size_t matching=0,foreign=0;
    for(size_t i=0;i<pixels.size();i+=4) {
        bool equal=true;
        for(size_t channel=0;channel<4;++channel)equal=equal && pixels[i+channel]==expected[channel];
        matching+=equal;
        foreign+=pixels[i]<40 && pixels[i+1]>200 && pixels[i+2]<40 && pixels[i+3]>200;
    }
    // A valid measured counterexample exits normally; terminal qualification
    // applies this predicate after retaining the original native assertions.
    std::cout<<"{\"passed\":"<<(matching>128 && !foreign?"true":"false")
        <<",\"width\":"<<image.width<<",\"height\":"<<image.height
        <<",\"matchingNativeColorPixels\":"<<matching<<",\"foreignGreenPixels\":"<<foreign
        <<",\"expectedNativeRGBA\":["<<expected[0]<<','<<expected[1]<<','<<expected[2]<<','<<expected[3]<<"]}\n";
    png_image_free(&image);return 0;
}
