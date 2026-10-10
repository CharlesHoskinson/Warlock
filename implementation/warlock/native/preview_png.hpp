#pragma once
#include "preview_uri.hpp"
#include "preview_fd.hpp"
#include <algorithm>
#include <span>

namespace preview::capture {
// This ledger accounts our nominal framebuffer, CPU pixels and encoded storage.
// GPU-driver allocations and compositor intermediates require native measurement.
struct BudgetState { uint64_t limit, used{}; size_t maxItems, items{}; };
class Reservation {
    std::shared_ptr<BudgetState> state_;
    uint64_t bytes_{};
public:
    Reservation(std::shared_ptr<BudgetState> state,uint64_t bytes):state_(std::move(state)),bytes_(bytes){}
    Reservation(const Reservation&)=delete;
    Reservation& operator=(const Reservation&)=delete;
    Reservation(Reservation&&)=default;
    Reservation& operator=(Reservation&&)=delete;
    ~Reservation() { if(state_) {state_->used-=bytes_;--state_->items;} }
    uint64_t bytes() const noexcept {return bytes_;}
};
class Budget {
    std::shared_ptr<BudgetState> state_;
public:
    Budget(uint64_t limit,size_t items):state_(std::make_shared<BudgetState>(BudgetState{limit,0,items,0})) {
        if(!limit || !items) throw std::invalid_argument("Positive producer budget");
    }
    std::optional<Reservation> reserve(uint64_t bytes) {
        if(!bytes || state_->items>=state_->maxItems || bytes>state_->limit-state_->used) return {};
        state_->used+=bytes;++state_->items;return Reservation{state_,bytes};
    }
    uint64_t used() const {return state_->used;}
    size_t items() const {return state_->items;}
};
struct Plan {uint32_t width,height,stride;uint64_t pixels,png,peak;};
inline std::optional<Plan> plan(uint32_t width,uint32_t height) {
    if(!width || !height || width>4096 || height>4096) return {};
    const uint64_t pixels=uint64_t{width}*height*4;
    const uint64_t filtered=(uint64_t{width}*4+1)*height;
    const uint64_t blocks=(filtered+65534)/65535;
    const uint64_t png=57+6+filtered+5*blocks;
    return Plan{width,height,width*4,pixels,png,pixels*2+png};
}
inline constexpr auto crcTable=[] {
    std::array<uint32_t,256> values{};
    for(uint32_t i=0;i<256;++i) {
        uint32_t c=i;
        for(unsigned bit=0;bit<8;++bit)c=(c>>1)^((c&1)?0xedb88320U:0U);
        values[i]=c;
    }
    return values;
}();
inline uint32_t crc(std::span<const uint8_t> data) {
    uint32_t c=0xffffffffU;
    for(uint8_t b:data)c=crcTable[(c^b)&255]^(c>>8);
    return c^0xffffffffU;
}
// Exactly one output allocation. No compression library workspace or filtered
// raster is allocated; stored deflate blocks are written directly into PNG.
inline std::vector<uint8_t> encodeRgba(std::span<const uint8_t> rgba,uint32_t width,uint32_t height,uint32_t stride,bool bottomUp,bool premultiplied) {
    const auto p=plan(width,height);
    if(!p || stride<p->stride || uint64_t{stride}*(height-1)+p->stride>rgba.size()) throw std::invalid_argument("RGBA bounds");
    std::vector<uint8_t> out(p->png);
    if(out.capacity()>p->png) throw std::runtime_error("Encoded capacity exceeds plan");
    size_t pos=0;
    auto byte=[&](uint8_t b){out.at(pos++)=b;};
    auto be=[&](uint32_t v){byte(v>>24);byte(v>>16);byte(v>>8);byte(v);};
    auto beginChunk=[&](uint32_t size,const char* type){be(size);const size_t start=pos;for(unsigned i=0;i<4;++i)byte(type[i]);return start;};
    auto endChunk=[&](size_t start){be(crc(std::span<const uint8_t>{out}.subspan(start,pos-start)));};
    for(uint8_t b:std::array<uint8_t,8>{137,80,78,71,13,10,26,10})byte(b);
    auto chunk=beginChunk(13,"IHDR");be(width);be(height);byte(8);byte(6);byte(0);byte(0);byte(0);endChunk(chunk);
    const uint64_t filtered=(uint64_t{width}*4+1)*height;
    chunk=beginChunk(static_cast<uint32_t>(6+filtered+5*((filtered+65534)/65535)),"IDAT");
    byte(0x78);byte(0x01);
    uint32_t a=1,b=0;
    uint64_t offset=0;
    while(offset<filtered) {
        const uint16_t count=static_cast<uint16_t>(std::min<uint64_t>(65535,filtered-offset));
        byte(offset+count==filtered?1:0);byte(count);byte(count>>8);byte(~count);byte((~count)>>8);
        for(uint32_t i=0;i<count;++i,++offset) {
            const uint64_t row=offset/(uint64_t{width}*4+1),column=offset%(uint64_t{width}*4+1);
            uint8_t value=0;
            if(column) {
                const uint64_t y=bottomUp?height-1-row:row;
                const uint64_t index=y*stride+column-1;
                value=rgba[index];
                const unsigned component=static_cast<unsigned>((column-1)%4);
                if(premultiplied && component<3) {
                    const uint8_t alpha=rgba[index-component+3];
                    value=alpha?static_cast<uint8_t>(std::min<unsigned>(255,(unsigned{value}*255+alpha/2)/alpha)):0;
                }
            }
            byte(value);a=(a+value)%65521;b=(b+a)%65521;
        }
    }
    be((b<<16)|a);endChunk(chunk);chunk=beginChunk(0,"IEND");endChunk(chunk);
    if(pos!=out.size()) throw std::runtime_error("PNG plan mismatch");
    return out;
}
class OwnedPng final:public uri::Payload {
    Reservation reservation_;
    std::vector<uint8_t> bytes_;
    mutable fd::Owned backing_;
    mutable void* mapping_{MAP_FAILED};
    size_t encodedBytes_{};
public:
    const uint32_t width,height;
    OwnedPng(Reservation&& reservation,std::vector<uint8_t>&& bytes,uint32_t w,uint32_t h,bool sealedOutput=false):reservation_(std::move(reservation)),bytes_(std::move(bytes)),width(w),height(h) {
        const auto p=plan(w,h);
        if(!p || bytes_.size()!=p->png || bytes_.capacity()>p->png || reservation_.bytes()<p->peak) throw std::invalid_argument("PNG ownership plan");
        if(sealedOutput) {
            const uint64_t pages=(p->png+4095)&~uint64_t{4095};
            // Pixels/framebuffer have already drained. Charge both the old
            // encoded vector and new backing during this bounded handoff.
            if(reservation_.bytes()<p->png+pages)throw std::invalid_argument("Sealed handoff exceeds original reservation");
            backing_=fd::seal(bytes_);
            encodedBytes_=bytes_.size();
            mapping_=::mmap(nullptr,encodedBytes_,PROT_READ,MAP_SHARED,backing_.get(),0);
            if(mapping_==MAP_FAILED)throw std::runtime_error("Sealed producer mapping unavailable");
            std::vector<uint8_t>{}.swap(bytes_);
        }
    }
    ~OwnedPng() override {closeBacking();}
    bool closeBacking() const noexcept {
        if(mapping_!=MAP_FAILED) {
            if(::munmap(mapping_,encodedBytes_))return false;
            mapping_=MAP_FAILED;
        }
        backing_=fd::Owned{};
        return true;
    }
    // Export aliases the exact sealed backing, never a second raster/copy.
    // Producer reservation remains until actual export release and retirement.
    int sealedDescriptor() const noexcept {return backing_.get();}
    uint64_t charge() const noexcept override {return reservation_.bytes();}
    std::span<const uint8_t> png() const noexcept override {return mapping_==MAP_FAILED?std::span<const uint8_t>{bytes_}:std::span<const uint8_t>{static_cast<const uint8_t*>(mapping_),encodedBytes_};}
};
}
