#include "CommitLedger.hpp"
#include <cassert>
#include <iostream>
using namespace OwnedRoute;
static Identity id{"ff01",42};
static std::string token="0123456789ab-1",digest(64,'a');
static Rect rect{10,20,380,240};
static CommitLedger setup(){CommitLedger l;l.configure({{"left",1},{"right",2}});l.seed(id,token,digest);return l;}
static Frame frame(CommitLedger& l,std::string output="left",double progress=0,bool endpoint=false,uint64_t now=100){auto f=l.prepare(output,output=="left"?1:2,rect,progress,endpoint,now);assert(f);return *f;}
static void presented(CommitLedger& l,const Frame& f,uint64_t time){assert(l.swapReturned(f.sequence,true)==Result::Deferred);assert(l.present(f.sequence,time,7)==Result::RecordedCurrent);}
int main(){int checks=0;auto check=[&](bool yes){assert(yes);++checks;};
 for(auto suffix:{"-extra","\n","\r\n"})check(!validToken(token+suffix));
 check(!validToken("0123456789ab-0"));check(!validToken("0123456789ab-9999999999999999"));
 {auto l=setup();auto f=frame(l);check(l.present(f.sequence,200,1)==Result::Deferred);check(!l.nativeReady());check(l.swapReturned(f.sequence,true)==Result::RecordedCurrent);check(l.records().size()==1);}
 {auto l=setup();auto f=frame(l);check(l.present(f.sequence,200,1)==Result::Deferred);check(l.swapReturned(f.sequence,false)==Result::Rejected);check(!l.isActive() && l.records().empty());check(l.present(f.sequence,300,2)==Result::Rejected);}
 {auto l=setup();auto a=frame(l);auto b=frame(l,"left",.5,false,150);check(l.swapReturned(a.sequence,true)==Result::Deferred);check(l.swapReturned(b.sequence,true)==Result::Deferred);check(l.present(a.sequence,200,1)==Result::RecordedCurrent);check(l.present(b.sequence,250,2)==Result::RecordedCurrent);check(l.present(a.sequence,300,3)==Result::Rejected);}
 {auto l=setup();auto f=frame(l);check(!l.retarget(id,"0123456789ab-2"));l.discarded(f.sequence);check(!l.isActive());}
 {auto l=setup();auto a=frame(l);presented(l,a,200);auto b=frame(l,"right");presented(l,b,200);check(!l.nativeReady());check(l.promote(id,token));check(l.nativeReady());check(!l.nativeEndpoint());check(l.retarget(id,"0123456789ab-2"));check(l.presentedOrigins().at("left").frame.rectangle==rect);check(!l.nativeReady());check(!l.promote(id,token));}
 {auto l=setup();check(l.promote(id,token));auto a=frame(l,"left",1,true);presented(l,a,200);check(!l.nativeEndpoint());auto b=frame(l,"right",1,true);presented(l,b,200);check(l.nativeEndpoint());auto c=frame(l,"left",.5,false,250);presented(l,c,300);check(!l.nativeEndpoint());}
 {auto l=setup();auto a=frame(l);l.outputRemoved("left",9);check(l.isActive());l.outputRemoved("left",1);check(!l.isActive());check(l.present(a.sequence,200,1)==Result::Rejected);}
 {auto l=setup();auto a=frame(l);l.seed({"ff02",43},"0123456789ab-2",std::string(64,'b'));check(l.present(a.sequence,200,1)==Result::Rejected);check(l.presentedOrigins().empty());check(!l.promote(id,token));}
 {auto l=setup();auto a=frame(l);check(!l.timedOut(200));check(l.timedOut(2000000101ULL));check(l.present(a.sequence,2000000200ULL,1)==Result::Rejected);}
 {auto l=setup();auto a=frame(l);check(l.swapReturned(a.sequence,true)==Result::Deferred);check(l.present(a.sequence,50,1)==Result::Rejected);check(l.present(a.sequence,200,1)==Result::RecordedCurrent);check(l.present(a.sequence,200,1)==Result::Rejected);}
 {auto l=setup();auto a=frame(l);check(l.present(a.sequence,200,1)==Result::Deferred);check(l.present(a.sequence,300,2)==Result::Rejected);check(l.swapReturned(a.sequence,true)==Result::RecordedCurrent);check(l.records().back().timestampNs==200);}
 {auto l=setup();auto a=frame(l);presented(l,a,200);auto b=frame(l,"right");presented(l,b,200);check(l.promote(id,token));check(l.nativeReady());l.suspendAuthority();check(!l.nativeReady());check(l.presentedOrigins().size()==2);}
 {auto l=setup();auto a=frame(l);check(l.swapReturned(a.sequence,true)==Result::Deferred);check(l.present(a.sequence,200,0)==Result::RecordedCurrent);check(l.records().back().compositorSequence==0);}
 {auto l=setup();auto a=frame(l);presented(l,a,200);auto b=frame(l,"left",.5,false,250);check(l.swapReturned(b.sequence,true)==Result::Deferred);check(l.present(b.sequence,300,7)==Result::RecordedCurrent);check(l.records().back().frame.sequence==b.sequence);}
 {auto l=setup();auto a=frame(l);presented(l,a,200);auto b=frame(l,"left",1,true,250);check(l.swapReturned(b.sequence,true)==Result::Deferred);check(l.present(b.sequence,300,6)==Result::Rejected);check(!l.nativeEndpoint());}
 {auto l=setup();auto a=frame(l);check(l.swapReturned(a.sequence,true)==Result::Deferred);check(l.present(a.sequence,200,UINT64_MAX)==Result::RecordedCurrent);auto b=frame(l,"left",1,true,250);check(l.swapReturned(b.sequence,true)==Result::Deferred);check(l.present(b.sequence,300,1)==Result::RecordedCurrent);}
 {auto l=setup();auto a=frame(l);presented(l,a,200);auto b=frame(l,"left",.5,false,250);check(l.swapReturned(b.sequence,true)==Result::Deferred);check(l.present(b.sequence,300,0)==Result::RecordedCurrent);auto c=frame(l,"left",1,true,350);check(l.swapReturned(c.sequence,true)==Result::Deferred);check(l.present(c.sequence,400,6)==Result::Rejected);}
 {auto l=setup();auto a=frame(l);presented(l,a,200);l.configure({{"left",1},{"right",2}});l.seed(id,"0123456789ab-2",digest);auto b=frame(l,"left",0,false,250);check(l.swapReturned(b.sequence,true)==Result::Deferred);check(l.present(b.sequence,300,6)==Result::Rejected);}
 {auto l=setup();auto a=frame(l);presented(l,a,200);l.configure({{"left",2},{"right",3}});l.seed(id,"0123456789ab-2",digest);auto b=l.prepare("left",2,rect,0,false,250);check(b.has_value());check(l.swapReturned(b->sequence,true)==Result::Deferred);check(l.present(b->sequence,300,6)==Result::RecordedCurrent);}
 {auto l=setup();l.suspendAuthority();check(!l.promote(id,token));}
 {auto l=setup();check(!l.prepare("missing",1,rect,0,false,100));check(!l.prepare("left",3,rect,0,false,100));check(!l.prepare("left",1,{NAN,0,1,1},0,false,100));check(!l.prepare("left",1,rect,.5,true,100));}
 std::cout<<checks<<" owned EGL commit ledger checks PASS\n";
}
