#include <png.h>
#include <vector>
#include <iostream>
#include <string>
#include <cstdlib>
int main(int argc,char** argv){if(argc!=6)return 2;const int expected[4]={std::atoi(argv[2]),std::atoi(argv[3]),std::atoi(argv[4]),std::atoi(argv[5])};png_image image{};image.version=PNG_IMAGE_VERSION;if(!png_image_begin_read_from_file(&image,argv[1]))return 3;image.format=PNG_FORMAT_RGBA;std::vector<unsigned char> pixels(PNG_IMAGE_SIZE(image));if(!png_image_finish_read(&image,nullptr,pixels.data(),0,nullptr)){png_image_free(&image);return 3;}size_t own=0,red=0,green=0;for(size_t i=0;i<pixels.size();i+=4){own+=pixels[i]==224 && pixels[i+1]==34 && pixels[i+2]==221 && pixels[i+3]==255;bool old=true;for(size_t c=0;c<4;++c)old=old && pixels[i+c]==expected[c];red+=old;green+=pixels[i]<40 && pixels[i+1]>200 && pixels[i+2]<40 && pixels[i+3]>200;}std::cout<<"{\"width\":"<<image.width<<",\"height\":"<<image.height<<",\"ownApplicationIconPixels\":"<<own<<",\"oldSourceExactNativePixels\":"<<red<<",\"foreignGreenPixels\":"<<green<<",\"hardwarePresentation\":false}\n";png_image_free(&image);return 0;}
