#include "preview_fd.hpp"
#include "preview_png.hpp"
#include <fstream>
#include <iostream>
using namespace preview::fd;
size_t mappings() {
    std::ifstream input("/proc/self/maps");std::string line;size_t count=0;
    while(std::getline(input,line))if(line.find("memfd:elm-preview-image")!=std::string::npos)++count;
    return count;
}
int main() {
    size_t checks=0;auto check=[&](bool ok){if(!ok)throw std::runtime_error("FD ownership qualification "+std::to_string(checks));++checks;};
    const std::array<uint8_t,4> rgba{0,255,255,255};const auto png=preview::capture::encodeRgba(rgba,1,1,4,false,false);
    Header h{};h[Magic]=MAGIC;h[Version]=1;h[Status]=0;
    for(size_t i=Lifetime;i<Count;++i)h[i]=1;
    h[Completed]=10;h[Now]=11;h[Deadline]=20;h[Expires]=30;h[Width]=h[Height]=1;h[Bytes]=png.size();h[Charge]=4096;h[CRC]=preview::capture::crc(png);h[Flags]=RootPopupPlane|Present|SourceLive;
    check(popupImageHeader(h));check(!imageHeader(h));check(!clientImageHeader(h));
    for(uint64_t flags=0;flags<64;++flags){auto candidate=h;candidate[Flags]=flags;check(popupImageHeader(candidate)==bool((flags&RootPopupPlane) && !(flags&~uint64_t{19})));}
    for(const auto plane:{SourcePlane::RootMonitor,SourcePlane::IsolatedClient}){
        auto fd=seal(png);const int raw=fd.get();bool refused=false;
        try{Mapped wrong(std::move(fd),h,4096,plane);}catch(const std::invalid_argument&){refused=true;}
        check(refused);errno=0;check(fcntl(raw,F_GETFD)==-1 && errno==EBADF);
    }
    auto under=seal(png);const int underRaw=under.get();bool underRefused=false;
    try{Mapped wrong(std::move(under),h,png.size()-1,SourcePlane::RootPopup);}catch(const std::invalid_argument&){underRefused=true;}
    check(underRefused);errno=0;check(fcntl(underRaw,F_GETFD)==-1 && errno==EBADF);
    preview::capture::Budget budget(4096,1);auto reservation=budget.reserve(4096);check(bool(reservation) && budget.used()==4096 && budget.items()==1);
    auto fd=seal(png);const int raw=fd.get();const auto before=mappings();
    check((fcntl(raw,F_GET_SEALS)&SEALS)==SEALS && (fcntl(raw,F_GETFD)&FD_CLOEXEC));
    auto payload=std::make_unique<Mapped>(std::move(fd),h,reservation->bytes(),SourcePlane::RootPopup);
    check(mappings()==before+1);check(payload->charge()==4096 && payload->png().size()==png.size() && preview::capture::crc(payload->png())==h[CRC]);
    errno=0;check(pwrite(raw,rgba.data(),rgba.size(),0)==-1 && errno==EPERM);
    check(!budget.reserve(1));payload.reset();errno=0;check(fcntl(raw,F_GETFD)==-1 && errno==EBADF);check(mappings()==before);
    check(budget.used()==4096);reservation.reset();check(budget.used()==0 && budget.items()==0);
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"physicalFDClosed\":true,\"physicalMappingClosed\":true,\"chargeReleasedAfterClose\":true}\n";
}
