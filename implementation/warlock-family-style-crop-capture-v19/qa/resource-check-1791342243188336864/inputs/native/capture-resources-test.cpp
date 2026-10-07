#include "capture-resources.hpp"
#include "preview_fd.hpp"
#include <iostream>
#include <map>
#include <memory>
using namespace preview::resources;
struct Counts {unsigned producer{},exporter{};};
struct Image {Counts& counts;explicit Image(Counts& c):counts(c){++counts.producer;}~Image(){--counts.producer;}uint64_t charge()const{return 4096;}};
struct Reservation {Counts& counts;explicit Reservation(Counts& c):counts(c){++counts.exporter;}~Reservation(){--counts.exporter;}uint64_t bytes()const{return 4096;}};
struct Export {preview::fd::Owned file;Reservation reservation;uint64_t transfer;Export(Counts& c,uint64_t id):file(preview::fd::seal(std::array<uint8_t,8>{137,80,78,71,13,10,26,10})),reservation(c),transfer(id){}};
struct Probe {
 uint64_t session=2,frontend=9007199254740993ULL,incarnation=4,request=7;
 bool client=true,popup=false,family=false,crop=false,styled=false,backdrop=false;
 std::unique_ptr<Image> image;std::unique_ptr<Export> exported;
 explicit Probe(Counts& c):image(std::make_unique<Image>(c)),exported(std::make_unique<Export>(c,9007199254740995ULL)){}
};
static unsigned checks;
static void check(bool ok,const char* name){require(ok,name);++checks;}
template<class F>static bool denied(F&& f){try{f();return false;}catch(const std::exception&){return true;}}
int main(){try{
 Counts counts;std::map<int,Probe> probes;probes.try_emplace(77,counts);const Binding binding{UINT64_MAX,2,9007199254740993ULL};const Target target{7,4};uint64_t sequence=0;
 auto apply=[&](Operation op,uint64_t transfer=0,bool locked=false,Target wanted=Target{7,4}){return execute(probes,77,binding,wanted,10,100,locked,op,transfer,sequence,[](const Result& result){return result;});};
 auto observed=apply(Operation::Observe);check(observed.producerBytes==4096 && observed.exportBytes==4096 && observed.exportTransfer==9007199254740995ULL && sequence==1,"Actual independent producer and export observations");
 auto pending=apply(Operation::RetireProducer);check(pending.status==Status::PendingExport && counts.producer==1 && counts.exporter==1,"Live original export prevents producer retirement");
 const auto before=sequence;check(denied([&]{apply(Operation::ReleaseExport,12);}) && sequence==before && counts.exporter==1,"Wrong original transfer preserves actual native export and sequence");
 check(denied([&]{execute(probes,77,binding,target,10,100,false,Operation::ReleaseExport,9007199254740995ULL,sequence,[](const Result&)->Result{throw std::bad_alloc();});}) && sequence==before && counts.exporter==1,"Failed native response construction precedes resource mutation");
 const int descriptor=probes.at(77).exported->file.get();auto released=apply(Operation::ReleaseExport,9007199254740995ULL,true);
 check(released.status==Status::Settled && !released.exportTransfer && released.producerBytes==4096 && counts.exporter==0 && counts.producer==1,"Export release under original lock policy preserves producer");
 check(fcntl(descriptor,F_GETFD)==-1 && errno==EBADF,"Actual original native export descriptor closed");
 auto retry=apply(Operation::ReleaseExport,9007199254740995ULL,true);check(retry.status==Status::Settled && !retry.exportBytes && counts.producer==1,"Lost release acknowledgment resolves idempotently without new export");
 observed=apply(Operation::Observe,0,true);check(!observed.exportTransfer && observed.producerBytes==4096 && observed.locked,"Resource state remains observable after export release while locked");
 pending=apply(Operation::RetireProducer,0,true);check(pending.status==Status::PendingLock && counts.producer==1 && probes.size()==1,"Original producer remains owned under lock");
 auto retired=apply(Operation::RetireProducer);check(retired.status==Status::Settled && !retired.producerBytes && !retired.exportTransfer && counts.producer==0 && probes.empty(),"Original producer resource retires only after independent barriers");
 retry=apply(Operation::RetireProducer);check(retry.status==Status::Settled && !retry.producerBytes && probes.empty(),"Lost producer acknowledgment resolves original target absence");
 probes.try_emplace(77,counts);probes.at(77).request=9;const int neighborDescriptor=probes.at(77).exported->file.get();
 for(const auto op:{Operation::Observe,Operation::ReleaseExport,Operation::RetireProducer}){
  auto absent=apply(op,op==Operation::ReleaseExport?9007199254740995ULL:0);
  check(!absent.producerBytes && !absent.exportTransfer && probes.at(77).request==9 && counts.producer==1 && counts.exporter==1 && fcntl(neighborDescriptor,F_GETFD)>=0,"Original absent target cannot erase another current capture");
 }
 const auto safe=sequence;
 check(denied([&]{apply(Operation::Observe,0,false,Target{9,5});}) && sequence==safe,"Wrong original subject cannot certify target absence");
 probes.at(77).client=false;check(denied([&]{apply(Operation::Observe,0,false,Target{9,4});}) && sequence==safe,"Wrong native source plane cannot grant client cleanup");probes.at(77).client=true;
 probes.at(77).frontend++;check(denied([&]{apply(Operation::Observe);}) && sequence==safe,"Foreign capture slot binding preserves native resources");probes.at(77).frontend--;
 check(denied([&]{apply(Operation::Observe,1);}) && sequence==safe,"Observation cannot carry an export mutation transfer");
 check(denied([&]{execute(probes,77,binding,Target{10,4},10,100,false,Operation::Observe,0,sequence,[](const Result& result){return result;});}) && sequence==safe,"Future target cannot certify original native retirement");
 sequence=UINT64_MAX;check(denied([&]{apply(Operation::ReleaseExport,9007199254740995ULL,false,Target{9,4});}) && counts.exporter==1 && counts.producer==1,"Sequence exhaustion cannot erase resources or reset history");
 probes.clear();check(!counts.producer && !counts.exporter && fcntl(neighborDescriptor,F_GETFD)==-1 && errno==EBADF,"Owned native resource fixture closes every actual export descriptor");
 std::cout<<"{\"passed\":true,\"checks\":"<<checks<<",\"actualExportDescriptorsClosed\":2,\"nativeAcceptance\":false}\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
