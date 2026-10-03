#include "ReadbackImage.hpp"
#include <sys/stat.h>
#include <iostream>
int main(){
 char directory[]="/tmp/rb-XXXXXX";if(!mkdtemp(directory))return 1;int fd=open(directory,O_RDONLY|O_DIRECTORY|O_CLOEXEC);int checks=0;
 const auto require=[&](bool p){if(!p)throw std::runtime_error("readback image assertion failed");++checks;};
 try{
  const std::vector<unsigned char> bottom={0,0,0,0,20,10,5,33,42,21,0,64,250,150,1,255};
  const std::vector<unsigned char> expected={42,21,0,64,250,150,1,255,0,0,0,0,20,10,5,33};
  auto top=OwnedReadback::topLeftRows(bottom,2,2);require(top==expected);
  OwnedReadback::publishPNG(fd,"raw.png",2,2,top);struct stat st{};require(fstatat(fd,"raw.png",&st,AT_SYMLINK_NOFOLLOW)==0);require((st.st_mode&0777)==0600);
  png_image image{};image.version=PNG_IMAGE_VERSION;auto path=std::string(directory)+"/raw.png";require(png_image_begin_read_from_file(&image,path.c_str()));image.format=PNG_FORMAT_RGBA;std::vector<unsigned char> decoded(PNG_IMAGE_SIZE(image));require(png_image_finish_read(&image,nullptr,decoded.data(),0,nullptr));png_image_free(&image);require(decoded==expected);
  bool refused=false;try{OwnedReadback::publishPNG(fd,"raw.png",2,2,std::vector<unsigned char>(16,255));}catch(...){refused=true;}require(refused);
  refused=false;try{OwnedReadback::publishPNG(fd,"../escape.png",2,2,top);}catch(...){refused=true;}require(refused);
  refused=false;try{OwnedReadback::topLeftRows(bottom,2,3);}catch(...){refused=true;}require(refused);
  symlinkat("raw.png",fd,"link.png");refused=false;try{OwnedReadback::publishPNG(fd,"link.png",2,2,top);}catch(...){refused=true;}require(refused);
  unlinkat(fd,"link.png",0);unlinkat(fd,"raw.png",0);close(fd);rmdir(directory);std::cout<<checks<<" readback encoding/ownership checks PASS\n";return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';close(fd);return 1;}
}
