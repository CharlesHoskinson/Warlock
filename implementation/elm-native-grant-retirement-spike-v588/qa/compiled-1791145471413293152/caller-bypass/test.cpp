#include "grant-registry.hpp"
#include <iostream>
#include <string>
using namespace Elm::GrantRetirement;
int checks=0;
void check(bool ok,const char* name) { ++checks; if(!ok) throw std::runtime_error(name); }
int main() { try {
 const Peer caller{41,101}, old{42,202};
 Registry r(77); auto a=r.hello(caller);auto b=r.hello(old);
 check(a.status==Status::Admitted && a.binding.session==1,"first-monotonic");
 check(b.status==Status::Admitted && b.binding.session==2,"second-monotonic");
 check(r.retire({41,999},a.binding,b.binding)==Status::CallerMismatch,"wrong-start-refused");
 check(r.retire({99,101},a.binding,b.binding)==Status::CallerMismatch,"foreign-peer-refused");
 auto forged=a.binding; ++forged.frontend;
 check(r.retire(caller,forged,b.binding)==Status::CallerMismatch,"wrong-caller-frontend-refused");
 forged=b.binding;++forged.lifetime;
 check(r.retire(caller,a.binding,forged)==Status::ForeignLifetime,"foreign-lifetime-refused");
 check(r.retire(caller,a.binding,a.binding)==Status::CurrentCaller,"self-retire-refused");
 check(r.registered(a.binding)&&r.registered(b.binding)&&r.size()==2,"refusals-preserve-live-grants");
 forged=b.binding;++forged.frontend;
 check(r.retire(caller,a.binding,forged)==Status::TargetMissing,"stale-target-refused");
 check(r.retire(caller,a.binding,b.binding)==Status::Admitted,"exact-old-live-retired");
 check(r.registered(a.binding)&&!r.registered(b.binding)&&r.size()==1,"caller-preserved-old-denied");
 check(!r.callerMatches(old,b.binding),"old-peer-effect-binding-denied");
 check(r.retire(caller,a.binding,b.binding)==Status::TargetMissing,"duplicate-retire-refused");
 auto c=r.hello(old);
 check(c.binding.session==3&&c.binding!=b.binding,"reattach-new-session");
 check(!r.registered(b.binding)&&r.registered(c.binding),"reattach-old-not-revived");
 check(r.retire(caller,a.binding,b.binding)==Status::TargetMissing&&r.registered(c.binding),"old-target-not-new-target");
 auto d=r.hello(old);
 check(d.binding.session==c.binding.session&&d.binding.frontend==2,"same-peer-hello-new-frontend");
 check(!r.registered(c.binding)&&r.registered(d.binding)&&r.registered(a.binding),"own-old-frontend-only-denied");
 check(r.retire(caller,a.binding,c.binding)==Status::TargetMissing&&r.registered(d.binding),"stale-target-not-current-frontend");
 check(!r.detach({42,999})&&r.registered(d.binding),"foreign-detach-refused");
 check(r.detach(old)&&!r.registered(d.binding),"detach-revokes");
 auto e=r.hello(old);check(e.binding.session==4,"detach-does-not-reset-allocator");
 auto f=r.hello({42,303});
 check(f.binding.session==5&&!r.registered(e.binding)&&!r.callerMatches(old,f.binding),"pid-replacement-new-session");
 check(r.hello({0,1}).status==Status::InvalidPeer&&r.hello({1,0}).status==Status::InvalidPeer,"zero-peer-refused");
 Binding zero{77,0,0};check(!r.registered(zero),"zero-grant-denied");
 bool invalid=false;try {Registry z(0);}catch(const std::invalid_argument&){invalid=true;}check(invalid,"zero-lifetime-refused");
 const auto max=std::numeric_limits<uint64_t>::max();Registry exhausted(88,max-1);
 uint64_t frontend=max-1;check(advanceFrontend(frontend)&&frontend==max,"frontend-max-once");
 check(!advanceFrontend(frontend)&&frontend==max,"frontend-overflow-no-mutation");
 auto last=exhausted.hello(caller);check(last.binding.session==max,"uint64-max-issued-once");
 check(exhausted.hello(old).status==Status::SessionExhausted&&exhausted.lastIssued()==max,"uint64-overflow-refused");
 check(exhausted.detach(caller),"max-detach");
 check(exhausted.hello(caller).status==Status::SessionExhausted&&exhausted.size()==0,"max-reattach-no-reuse");
 Registry full(99);Binding first{};for(uint64_t i=1;i<=16;++i){auto x=full.hello({i,i});check(x.status==Status::Admitted,"bounded-slot-admitted");if(i==1)first=x.binding;}
 check(full.hello({17,17}).status==Status::SessionBound&&full.lastIssued()==16,"capacity-refusal-no-id-burn");
 check(full.hello({1,1}).status==Status::Admitted&&!full.registered(first),"existing-peer-hello-at-capacity");
 check(full.detach({2,2})&&full.hello({17,17}).binding.session==17,"capacity-release-monotonic");
 // Long deterministic churn is a separate no-reuse property across retire/detach.
 Registry churn(101);auto owner=churn.hello(caller);uint64_t previous=owner.binding.session;
 for(uint64_t i=1;i<=1000;++i){auto target=churn.hello({42,i});check(target.binding.session>previous,"churn-strict-increase");previous=target.binding.session;check(churn.retire(caller,owner.binding,target.binding)==Status::Admitted&&!churn.registered(target.binding),"churn-exact-revocation");}
 std::cout<<"{\"passed\":true,\"checks\":"<<checks<<"}\n";return 0;
 }catch(const std::exception& e){std::cerr<<"failed: "<<e.what()<<"\n";return 1;}}
