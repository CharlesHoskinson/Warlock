#include <GLES2/gl2.h>
#include <vector>
#include <fstream>
#include <cstdlib>
#include <sys/stat.h>
static std::vector<unsigned char> uploadedBytes;
static void cpuGen(GLsizei n,GLuint* p){for(int i=0;i<n;++i)p[i]=1;}
static void cpuBind(GLenum,GLuint){}
static void cpuParameter(GLenum,GLenum,GLint){}
static void cpuStore(GLenum,GLint){}
static void cpuImage(GLenum target,GLint level,GLint internal,GLsizei width,GLsizei height,GLint border,GLenum format,GLenum type,const void* bytes){
 if(target!=GL_TEXTURE_2D||level||internal!=GL_RGBA||border||format!=GL_RGBA||type!=GL_UNSIGNED_BYTE)throw std::invalid_argument("unexpected CPU upload contract");
 const auto* p=static_cast<const unsigned char*>(bytes);uploadedBytes.assign(p,p+size_t(width)*height*4);
}
static GLenum cpuError(){return GL_NO_ERROR;}
static void cpuDelete(GLsizei,const GLuint*){}
#define glGenTextures cpuGen
#define glBindTexture cpuBind
#define glTexParameteri cpuParameter
#define glPixelStorei cpuStore
#define glTexImage2D cpuImage
#define glGetError cpuError
#define glDeleteTextures cpuDelete
#define OWNED_EGL_OFFLINE_TEST
#include "../producer-readback-v4/Renderer.cpp"
struct OfflineCommands {
 static void run(const char* path,const char* hash,int width,int height,const char* output){
  Renderer renderer;renderer.upload(path,hash,width,height);
  std::ofstream file(output,std::ios::binary);file.write(reinterpret_cast<const char*>(uploadedBytes.data()),uploadedBytes.size());if(!file)throw std::runtime_error("CPU upload dump failed");
 }
};
int main(int argc,char** argv){
 if(argc!=6)return 2;umask(0077);
 try{OfflineCommands::run(argv[1],argv[2],std::stoi(argv[3]),std::stoi(argv[4]),argv[5]);return 0;}
 catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
