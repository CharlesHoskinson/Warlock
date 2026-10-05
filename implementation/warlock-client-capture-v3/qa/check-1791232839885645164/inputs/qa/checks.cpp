#include "client_plan.hpp"
#include "preview_fd.hpp"
#include <png.h>
#include <iostream>
#include <limits>
#include <random>
using namespace preview;
static unsigned checks=0;
void check(bool ok,const char* message){if(!ok)throw std::runtime_error(message);++checks;}
fd::Header header(uint64_t flags,uint64_t bytes=8){fd::Header h{};h.fill(1);h[fd::Magic]=fd::MAGIC;h[fd::Version]=1;h[fd::Status]=0;h[fd::Bytes]=bytes;h[fd::Charge]=bytes;h[fd::Flags]=flags;h[fd::Deadline]=3;h[fd::Expires]=3;return h;}
int main(int argc,char** argv){try{
 if(argc==2 && std::string_view(argv[1])=="--flags") {uint64_t f;while(std::cin>>f){const auto h=header(f);std::cout<<fd::imageHeader(h)<<' '<<fd::clientImageHeader(h)<<'\n';}return 0;}
 auto layout=[](double w,double h,double cw,double ch,double s=1,bool transform=false,bool offset=false,bool custom=false){return capture::clientPlan(w,h,cw,ch,s,transform,offset,custom);};
 check(layout(320,240,800,600).has_value(),"Supported unit-scale client");
 for(auto p:{layout(0,1,800,600),layout(-1,1,800,600),layout(320.5,240,800,600),layout(320,240,799.5,600),layout(801,240,800,600),layout(320,601,800,600),layout(1,1,4097,600),layout(320,240,800,600,1.25),layout(320,240,800,600,1,true),layout(320,240,800,600,1,false,true),layout(320,240,800,600,1,false,false,true),layout(std::numeric_limits<double>::infinity(),1,800,600),layout(std::numeric_limits<double>::quiet_NaN(),1,800,600)})check(!p,"Unsupported geometry refuses");
 std::mt19937 rng(720001);for(unsigned i=0;i<2000;++i){unsigned w=1+rng()%800,h=1+rng()%600;auto p=layout(w,h,800,600);check(p && p->client.width==w && p->client.height==h && p->peak==800ULL*600*4+uint64_t(w)*h*4+p->client.png && p->peak>=p->client.peak,"Client bounds and conservative allocation charge");}
 auto p=*layout(2,2,800,600);capture::Budget budget(p.peak,1);auto reservation=budget.reserve(p.peak);check(reservation && !budget.reserve(1),"Held capture charge cannot be reused");
 std::vector<uint8_t> rgba{0,0,255,255,0,0,255,255,255,0,0,255,255,0,0,255};auto bytes=capture::encodeRgba(rgba,2,2,8,true,true);
 auto owned=std::make_unique<const capture::OwnedPng>(std::move(*reservation),std::move(bytes),2,2);check(budget.used()==p.peak && owned->charge()==p.peak,"Encoded result retains allocation reservation");
 png_image image{};image.version=PNG_IMAGE_VERSION;check(png_image_begin_read_from_memory(&image,owned->png().data(),owned->png().size()),"Independent libpng parses encoded pixels");image.format=PNG_FORMAT_RGBA;std::vector<uint8_t> decoded(PNG_IMAGE_SIZE(image));check(png_image_finish_read(&image,nullptr,decoded.data(),0,nullptr),"Independent decoder succeeds");check(image.width==2 && image.height==2 && decoded[0]==255 && decoded[2]==0 && decoded[8]==0 && decoded[10]==255,"Top-left crop orientation retained");png_image_free(&image);
 for(uint64_t f=0;f<32;++f){auto h=header(f);check(fd::imageHeader(h)==(f>0 && f<=7),"Legacy source rejects client kind");check(fd::clientImageHeader(h)==(f>=8 && f<=11),"Client rejects mixed and unknown kinds");}
 auto h=header(fd::IsolatedClientPlane|fd::Present|fd::SourceLive,owned->png().size());auto file=fd::seal(owned->png());const int raw=file.get();check((fcntl(raw,F_GET_SEALS)&fd::SEALS)==fd::SEALS && (fcntl(raw,F_GETFD)&FD_CLOEXEC),"Native backing sealed and close-on-exec");uint8_t byte=0;check(pwrite(raw,&byte,1,0)<0 && errno==EPERM,"Retained descriptor cannot mutate pixels");
 auto mapped=std::make_shared<fd::Mapped>(std::move(file),h,h[fd::Bytes],fd::SourcePlane::IsolatedClient);check(mapped->png().size()==owned->png().size() && std::equal(mapped->png().begin(),mapped->png().end(),owned->png().begin()),"Explicit client mapping owns original sealed bytes");auto streamOwner=mapped;mapped.reset();check(fcntl(raw,F_GETFD)>=0,"Consumer reference retains native mapping");streamOwner.reset();check(fcntl(raw,F_GETFD)<0 && errno==EBADF,"Final physical consumer closes descriptor");
 bool refused=false;try{fd::Mapped legacy(fd::seal(owned->png()),h,h[fd::Bytes]);}catch(const std::invalid_argument&){refused=true;}check(refused,"Legacy default mapping refuses client source");h[fd::Flags]=fd::FullMonitorPlane;refused=false;try{fd::Mapped client(fd::seal(owned->png()),h,h[fd::Bytes],fd::SourcePlane::IsolatedClient);}catch(const std::invalid_argument&){refused=true;}check(refused,"Explicit client mapping refuses monitor source");
 owned.reset();check(!budget.used() && !budget.items(),"Owned PNG destruction releases actual reservation");
 std::cout<<"{\"passed\":true,\"checks\":"<<checks<<"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
