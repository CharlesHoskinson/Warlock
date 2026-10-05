#include "demand.hpp"
#include <iostream>
#include <sstream>
using namespace preview;
using namespace preview::demand;
static unsigned checks=0,frees=0;
static void check(bool ok,const char* name){if(!ok)throw std::runtime_error(name);++checks;}
struct Image final:Buffer { ~Image(){++frees;} uint64_t charge()const noexcept override{return 32;} };
static NativeDemand demand(uint64_t entry=1){return {entry,1,{{{1},{2},{3}},{{1},{4},{5},{6},{7},{8},{1}},{10},1,true,true,false,true},{11},32,true};}
static Coordinator coordinator(size_t items=2,size_t records=20,size_t entries=2){return Coordinator({{entries,records,items,64},{1},{10},2});}
static void finish(Coordinator& q,uint64_t entry) {
    const auto slot=q.inspect(entry);if(!slot.capture)return;
    const Job job=*slot.capture; std::unique_ptr<const Buffer> image=std::make_unique<const Image>();
    auto offered=q.nativeBroker().allocate(entry,job,image,q.now()+100);
    if(offered.receipts.empty() && image) image.reset();
    q.nativeBroker().producerComplete(entry,job);q.poll();
}
static void drain(Coordinator& q) {
    for(const auto& r:q.nativeBroker().inspect()) {
        if(r.terminal || !r.producerDone)continue;
        q.nativeBroker().cancel(r.entry,r.job.binding,r.job);
        if(!q.nativeBroker().consumerComplete(r.entry,r.job))continue;
        auto completed=q.nativeBroker().destroy(r.entry,r.job);
        if(!completed.receipts.empty())q.nativeBroker().acknowledge(r.entry,r.job.binding,r.job,completed.receipts.back().sequence);
    }
    q.poll();
}
static void controls(){
    auto q=coordinator();auto d=demand();check(q.observe(d).accepted,"exact native demand enrolled");
    auto first=q.start(1,20);check(first.status==Attempt::Status::Started,"first demand starts immediately");
    const Job original=*first.job;d.scope.context.content={2};check(q.observe(d).accepted,"new tracked revision observed during capture");
    d.scope.context.content={3};q.observe(d);check(q.inspect(1).latest.scope.context.content.value==3,"latest revision retained");
    check(q.start(1,40).status==Attempt::Status::NotReady,"busy producer cannot renew request");
    check(q.inspect(1).capture==original && original.deadline==20,"original admitted deadline unchanged");
    finish(q,1);check(q.nativeBroker().charge()==32 && !q.inspect(1).capture,"producer completion preserves physical charge");
    check(q.start(1,40).status==Attempt::Status::NotReady,"continuous changes remain paced");
    d.scope.now=3;q.observe(d);auto latest=q.start(1,40);check(latest.status==Attempt::Status::Started && latest.job->context.content.value==3,"final tracked revision serviced under pacing");
    check(q.nativeBroker().charge()==64,"old consumer image remains owned beside new capture");
    finish(q,1);d.scope.context.content={4};d.scope.now=5;q.observe(d);
    auto full=q.start(1,60);check(full.status==Attempt::Status::Capacity && !full.job && full.native.receipts.empty(),"capacity is local feedback not Refused");
    drain(q);check(q.nativeBroker().charge()==0,"actual physical retirement clears charge");
    auto after=q.start(1,60);check(after.status==Attempt::Status::Started && after.job->request.value==3,"capacity recovery preserves replay floor");
    d.visible=false;q.observe(d);check(q.nativeBroker().charge()==32 && q.inspect(1).capture==after.job,"close requests cleanup without forgetting owner");
    d.scope.context.content={5};q.observe(d);check(q.start(1,70).status==Attempt::Status::NotReady,"no late capture after close");
    d.visible=true;check(!q.observe(d).accepted,"closed lease cannot reopen");
    finish(q,1);drain(q);d.lease=2;d.scope.now=7;check(q.observe(d).accepted,"fresh native lease can reopen");
    check(q.start(1,80).status==Attempt::Status::Started,"reopened demand uses new request");
    auto bad=d;bad.scope.clock={12};auto floor=q.nativeBroker().requestFloor(1);check(!q.observe(bad).accepted && q.nativeBroker().requestFloor(1)==floor,"foreign clock cannot create native refusal");
    bad=d;bad.scope.now=6;check(!q.observe(bad).accepted,"backwards native clock rejected");
    bad=d;bad.scope.binding.frontend={8};check(!q.observe(bad).accepted,"binding substitution needs fresh lease");
    bad=d;bad.scope.context.incarnation={9};check(!q.observe(bad).accepted,"incarnation substitution needs fresh lease");
    bad=d;bad.scope.context.content={0};check(!q.observe(bad).accepted,"zero typed source identity rejected");
    auto separate=coordinator(1);auto a=demand();separate.observe(a);auto held=separate.start(1,20);a.visible=false;separate.observe(a);
    auto b=demand(2);b.scope.context.incarnation={9};b.scope.now=3;check(separate.observe(b).accepted,"independent demand enrolled");
    check(separate.start(2,30).status==Attempt::Status::Capacity,"held reservation cannot be reused");
    finish(separate,1);drain(separate);check(separate.start(2,30).status==Attempt::Status::Started,"closed demand cannot globally block unrelated eligible capacity");
    auto expiry=coordinator();auto e=demand();expiry.observe(e);auto timed=expiry.start(1,3);e.scope.now=3;expiry.observe(e);check(expiry.inspect(1).capture==timed.job && expiry.nativeBroker().charge()==32,"elapsed deadline is not producer retirement");
    check(expiry.start(1,300).status==Attempt::Status::NotReady,"late caller cannot renew admitted deadline");finish(expiry,1);drain(expiry);
    auto noDeadline=coordinator();auto nd=demand();noDeadline.observe(nd);check(noDeadline.start(1,1).status==Attempt::Status::NotReady && noDeadline.nativeBroker().recordCount()==0,"unsent expired deadline rejected locally");
    auto locked=coordinator();auto l=demand();locked.observe(l);l.scope.locked=true;l.scope.now=2;locked.observe(l);check(locked.start(1,10).status==Attempt::Status::NotReady,"lock blocks queued capture");l.scope.locked=false;l.scope.now=3;check(locked.observe(l).accepted && locked.start(1,12).status==Attempt::Status::Started,"native eligibility recovery retains authorized lease");
    auto limit=coordinator(2,20,1);auto one=demand();limit.observe(one);auto two=demand(2);two.scope.context.incarnation={7};check(!limit.observe(two).accepted,"bounded entry capacity fails closed");
    auto records=coordinator(2,1);auto r=demand();records.observe(r);records.start(1,20);finish(records,1);r.scope.context.content={2};r.scope.now=3;records.observe(r);check(records.start(1,30).status==Attempt::Status::Capacity,"unacknowledged broker records remain bounded");
    auto exhaustion=coordinator();auto x=demand();exhaustion.observe(x);Job max{x.scope.binding,x.scope.context,{UINT64_MAX},x.origin,x.scope.clock,20};exhaustion.nativeBroker().acquire(1,x.scope.binding,max);auto refused=exhaustion.nativeBroker().producerRefused(1,max);exhaustion.nativeBroker().acknowledge(1,x.scope.binding,max,refused.receipts.back().sequence);check(exhaustion.start(1,30).status==Attempt::Status::Exhausted,"request counter never wraps replay floor");
    bool throws=false;try{Coordinator invalid({{1,1,1,32},{1},{10},0});}catch(const std::invalid_argument&){throws=true;}check(throws,"pacing policy cannot be omitted");
    std::cout<<"{\"passed\":true,\"checks\":"<<checks<<"}\n";
}
static void replay(){
    auto q=coordinator();auto d=demand();q.observe(d);std::string line;
    while(std::getline(std::cin,line)){
        if(line=="Content"){++d.scope.context.content.value;q.observe(d);}
        else if(line=="Tick"){++d.scope.now;q.observe(d);}
        else if(line=="Start")q.start(1,d.scope.now+100);
        else if(line=="Finish")finish(q,1);
        else if(line=="Drain")drain(q);
        else if(line=="Close"){d.visible=false;q.observe(d);}
        else if(line=="Reopen"){++d.lease;d.visible=true;q.observe(d);}
        else if(line!="Init")throw std::runtime_error("unknown replay input");
        q.poll();const auto& s=q.inspect(1);const auto& b=q.nativeBroker();
        std::cout<<"{\"latest\":"<<s.latest.scope.context.content.value<<",\"captured\":"<<(s.requested?s.requested->context.content.value:0)<<",\"issuedLease\":"<<(s.requested?s.requested->lease:0)<<",\"busy\":"<<(s.capture?"true":"false")<<",\"owners\":"<<b.activeItems()<<",\"visible\":"<<(s.open?"true":"false")<<",\"now\":"<<q.now()<<",\"lastStart\":"<<q.lastAttempt().value_or(0)<<",\"lease\":"<<s.latest.lease<<",\"floor\":"<<b.requestFloor(1)<<"}\n";
    }
}
int main(int argc,char** argv){try{if(argc==2 && std::string_view(argv[1])=="--replay")replay();else controls();return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
