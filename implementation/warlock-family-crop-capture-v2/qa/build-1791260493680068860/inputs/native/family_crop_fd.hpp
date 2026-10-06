#pragma once
#include "preview_fd.hpp"
#include <bit>
#include <cmath>
namespace preview::cropfd {
constexpr uint64_t CroppedFamilyPlane=64;
enum Word:size_t {PixelX=fd::Count,PixelY,Scale,Count};
using Header=std::array<uint64_t,Count>;
inline int64_t pixelX(const Header& h){return std::bit_cast<int64_t>(h[PixelX]);}
inline int64_t pixelY(const Header& h){return std::bit_cast<int64_t>(h[PixelY]);}
inline double scale(const Header& h){return std::bit_cast<double>(h[Scale]);}
inline fd::Header base(const Header& h){fd::Header value{};std::copy_n(h.begin(),fd::Count,value.begin());return value;}
inline bool matches(const Header& h,const fd::Query& q){
    if(q[fd::RVersion]!=2 || h[fd::Version]!=2)return false;
    auto header=base(h);auto query=q;header[fd::Version]=query[fd::RVersion]=1;
    return fd::matches(header,query);
}
inline bool imageHeader(const Header& h){
    if(h[fd::Magic]!=fd::MAGIC || h[fd::Version]!=2 || h[fd::Status]!=0 || !(h[fd::Flags]&CroppedFamilyPlane) || (h[fd::Flags]&~uint64_t{67}))return false;
    const auto x=pixelX(h),y=pixelY(h);const auto s=scale(h);
    if(x<-INT32_MAX || x>INT32_MAX || y<-INT32_MAX || y>INT32_MAX || !std::isfinite(s) || s<=0 ||
       h[fd::Width]>4096 || h[fd::Height]>4096 || x+static_cast<int64_t>(h[fd::Width])>INT32_MAX || y+static_cast<int64_t>(h[fd::Height])>INT32_MAX)return false;
    auto value=base(h);value[fd::Version]=1;value[fd::Flags]=(value[fd::Flags]&uint64_t{3})|fd::NativeFamilyPlane;
    return fd::familyImageHeader(value);
}
// A typed new source; inner storage reuses the physically owning sealed mapping.
// The legacy Header/SourcePlane API cannot decode the version2 crop envelope.
class Mapped final:public uri::Payload {
    Header metadata_;
    std::unique_ptr<fd::Mapped> memory_;
public:
    Mapped(fd::Owned&& file,const Header& h,uint64_t reserved):metadata_(h){
        if(!imageHeader(h))throw std::invalid_argument("Invalid native family crop metadata");
        auto value=base(h);value[fd::Version]=1;value[fd::Flags]=(value[fd::Flags]&uint64_t{3})|fd::NativeFamilyPlane;
        memory_=std::make_unique<fd::Mapped>(std::move(file),value,reserved,fd::SourcePlane::NativeFamily);
    }
    uint64_t charge()const noexcept override{return memory_->charge();}
    std::span<const uint8_t> png()const noexcept override{return memory_->png();}
    const Header& metadata()const noexcept{return metadata_;}
};
}
