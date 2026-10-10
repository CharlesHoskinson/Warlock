#include "preview_png.hpp"
#include "capture-resources.hpp"
#include <cassert>
#include <cerrno>
#include <iostream>
#include <map>

using namespace preview;
int main() {
    constexpr uint64_t limit=128ULL*1024*1024;
    capture::Budget budget(limit,2);
    const auto plan=capture::plan(8,8);assert(plan);
    const auto pages=(plan->png+4095)&~uint64_t{4095};
    const auto peak=std::max(plan->peak,plan->png+pages);
    auto make=[&](uint8_t color,bool sealed) {
        std::vector<uint8_t> pixels(plan->pixels,color);
        auto bytes=capture::encodeRgba(pixels,8,8,32,false,false);
        auto reservation=budget.reserve(sealed?peak:plan->peak);assert(reservation);
        return std::make_unique<const capture::OwnedPng>(std::move(*reservation),std::move(bytes),8,8,sealed);
    };
    auto first=make(31,true);assert(budget.items()==1 && budget.used()==peak);
    fd::Owned exported(::fcntl(first->sealedDescriptor(),F_DUPFD_CLOEXEC,0));assert(exported);
    struct stat producer{},consumer{};
    assert(!::fstat(first->sealedDescriptor(),&producer) && !::fstat(exported.get(),&consumer));
    assert(producer.st_dev==consumer.st_dev && producer.st_ino==consumer.st_ino && producer.st_size==static_cast<off_t>(plan->png));
    assert((::fcntl(exported.get(),F_GET_SEALS)&fd::SEALS)==fd::SEALS);
    uint8_t changed=0;errno=0;assert(::pwrite(exported.get(),&changed,1,0)==-1 && errno==EPERM);
    assert(budget.items()==1 && budget.used()==peak);
    auto second=make(97,true);assert(budget.items()==2 && budget.used()==2*peak);
    struct stat other{};assert(!::fstat(second->sealedDescriptor(),&other));assert(other.st_ino!=producer.st_ino);
    assert(!std::equal(first->png().begin(),first->png().end(),second->png().begin()));
    assert(!budget.reserve(peak));
    // Import mapping observes the exact same backing; no PNG bytes are copied.
    auto mapped=::mmap(nullptr,plan->png,PROT_READ,MAP_SHARED,exported.get(),0);assert(mapped!=MAP_FAILED);
    assert(std::equal(first->png().begin(),first->png().end(),static_cast<const uint8_t*>(mapped)));
    assert(!::munmap(mapped,plan->png));exported=fd::Owned{};
    assert(budget.items()==2 && budget.used()==2*peak); // release is not producer retirement
    assert(first->closeBacking());first.reset();assert(budget.items()==1 && budget.used()==peak);
    assert(second->png().size()==plan->png && (::fcntl(second->sealedDescriptor(),F_GET_SEALS)&fd::SEALS)==fd::SEALS);
    second.reset();assert(budget.items()==0 && budget.used()==0);
    auto legacy=make(42,false);assert(legacy->sealedDescriptor()==-1);
    const auto legacyBytes=legacy->png();auto oldExport=budget.reserve(pages);assert(oldExport);
    auto oldFile=fd::seal(legacyBytes);assert(oldFile && budget.items()==2);
    oldFile=fd::Owned{};oldExport.reset();legacy.reset();assert(budget.items()==0 && budget.used()==0);
    // The small-image handoff must reserve its kernel page before allocating it.
    auto insufficient=budget.reserve(plan->peak);assert(insufficient);
    bool refused=false;
    try {capture::OwnedPng value(std::move(*insufficient),capture::encodeRgba(std::vector<uint8_t>(plan->pixels,0),8,8,32,false,false),8,8,true);}
    catch(const std::invalid_argument&){refused=true;}
    assert(refused && budget.items()==0 && budget.used()==0);
    capture::Budget tight(peak-1,2);assert(!tight.reserve(peak));
    // The original client resource protocol still requires its independent
    // export reservation. Picker alias storage cannot enter that client path.
    struct Export {fd::Owned file;std::optional<capture::Reservation> reservation;uint64_t transfer;};
    struct Probe {
        uint64_t session=2,frontend=3,request=10,incarnation=4;
        bool client=true,popup=false,family=false,crop=false,styled=false,backdrop=false;
        std::unique_ptr<const capture::OwnedPng> image;
        std::unique_ptr<Export> exported;
    };
    std::map<int,Probe> records;
    Probe probe;probe.image=make(43,false);auto exportReservation=budget.reserve(pages);assert(exportReservation);
    probe.exported=std::make_unique<Export>(Export{fd::seal(probe.image->png()),std::move(exportReservation),9});
    records.emplace(5,std::move(probe));uint64_t sequence=0;
    auto resource=[&](resources::Operation operation,uint64_t transfer) {
        return resources::execute(records,5,resources::Binding{1,2,3},resources::Target{10,4},11,1,false,operation,transfer,sequence,[](const resources::Result& result){return result;});
    };
    auto observed=resource(resources::Operation::Observe,0);assert(observed.exportBytes==pages && observed.producerBytes==plan->peak);
    auto pending=resource(resources::Operation::RetireProducer,0);assert(pending.status==resources::Status::PendingExport && budget.items()==2);
    const auto before=sequence;bool badTransfer=false;
    try {resource(resources::Operation::ReleaseExport,8);}catch(const std::invalid_argument&){badTransfer=true;}
    assert(badTransfer && sequence==before && budget.items()==2);
    resource(resources::Operation::ReleaseExport,9);assert(budget.items()==1 && records.at(5).image);
    resource(resources::Operation::RetireProducer,0);assert(records.empty() && budget.items()==0);
    std::cout << "{\"passed\":true,\"sameImmutableBacking\":true,\"twoDistinctFamilies\":true,\"thirdRefused\":true,\"chargeRetainedUntilProducerRetirement\":true,\"legacyCopyUnchanged\":true,\"handoffPeakReserved\":true}\n";
}
