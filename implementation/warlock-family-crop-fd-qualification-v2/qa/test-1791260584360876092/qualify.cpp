#include "family_crop_fd.hpp"
#include "preview_png.hpp"
#include <fstream>
#include <iostream>
size_t mappings(){std::ifstream input("/proc/self/maps");std::string line;size_t count=0;while(std::getline(input,line))if(line.find("memfd:elm-preview-image")!=std::string::npos)++count;return count;}
int main(){size_t checks=0;try{
    using namespace preview;using namespace fd;
    auto check=[&](bool ok){if(!ok)throw std::runtime_error("crop FD control "+std::to_string(checks));++checks;};
    const std::array<uint8_t,4> rgba{64,0,128,255};const auto png=capture::encodeRgba(rgba,1,1,4,false,false);
    cropfd::Header h{};h[Magic]=MAGIC;h[Version]=2;
    for(size_t i=fd::Lifetime;i<fd::Count;++i)h[i]=1;
    h[Completed]=10;h[Now]=11;h[Deadline]=20;h[Expires]=30;h[Width]=h[Height]=1;h[Bytes]=png.size();h[Charge]=4096;h[CRC]=capture::crc(png);h[Flags]=67;
    h[cropfd::PixelX]=std::bit_cast<uint64_t>(int64_t{-35});h[cropfd::PixelY]=17;h[cropfd::Scale]=std::bit_cast<uint64_t>(1.5);
    check(cropfd::imageHeader(h));check(cropfd::pixelX(h)==-35 && cropfd::pixelY(h)==17 && cropfd::scale(h)==1.5);
    auto legacy=cropfd::base(h);check(!fd::imageHeader(legacy) && !clientImageHeader(legacy) && !popupImageHeader(legacy) && !familyImageHeader(legacy));
    for(uint64_t flags=0;flags<256;++flags){auto value=h;value[Flags]=flags;check(cropfd::imageHeader(value)==bool((flags&64) && !(flags&~uint64_t{67})));}
    for(double scale:{0.,-1.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}){auto value=h;value[cropfd::Scale]=std::bit_cast<uint64_t>(scale);check(!cropfd::imageHeader(value));}
    for(int64_t x:{int64_t{INT32_MAX},int64_t{INT32_MIN},INT64_MAX,INT64_MIN}){auto value=h;value[cropfd::PixelX]=std::bit_cast<uint64_t>(x);check(!cropfd::imageHeader(value));value=h;value[cropfd::PixelY]=std::bit_cast<uint64_t>(x);check(!cropfd::imageHeader(value));}
    for(uint64_t width:std::array<uint64_t,3>{0,4097,UINT64_MAX}){auto value=h;value[Width]=width;check(!cropfd::imageHeader(value));}
    for(uint64_t version:{0ULL,1ULL,3ULL}){auto value=h;value[Version]=version;check(!cropfd::imageHeader(value));}
    Query q{MAGIC,2,Get,1,1,1,1,1,1,0};check(cropfd::matches(h,q));for(size_t i=RLifetime;i<=RSubject;++i){auto foreign=q;++foreign[i];check(!cropfd::matches(h,foreign));}
    auto old=q;old[RVersion]=1;check(!cropfd::matches(h,old));
    const auto bytes=encode(h);check(decode<cropfd::Count>(bytes)==h);
    auto bad=h;bad[Version]=1;auto invalid=seal(png);const auto invalidRaw=invalid.get();bool refused=false;
    try{cropfd::Mapped value(std::move(invalid),bad,4096);}catch(const std::invalid_argument&){refused=true;}
    check(refused);errno=0;check(fcntl(invalidRaw,F_GETFD)==-1 && errno==EBADF);
    capture::Budget budget(4096,1);auto reservation=budget.reserve(4096);check(bool(reservation));auto file=seal(png);const auto raw=file.get();const auto before=mappings();
    auto payload=std::make_unique<cropfd::Mapped>(std::move(file),h,reservation->bytes());check(mappings()==before+1 && payload->charge()==4096 && payload->metadata()==h && capture::crc(payload->png())==h[CRC]);
    errno=0;check(pwrite(raw,rgba.data(),rgba.size(),0)==-1 && errno==EPERM);check(!budget.reserve(1));payload.reset();errno=0;check(fcntl(raw,F_GETFD)==-1 && errno==EBADF && mappings()==before);check(budget.used()==4096);reservation.reset();check(budget.used()==0 && budget.items()==0);
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"physicalFDClosed\":true,\"physicalMappingClosed\":true,\"chargeReleasedAfterClose\":true}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
