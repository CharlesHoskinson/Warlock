#include "ProspectiveGeometry.hpp"
#include "ReachableAxis.hpp"
#include <set>
#include <iostream>
namespace P=Elm::ProspectiveGeometry;namespace R=Elm::ExperimentalReachableAxis;
int count=0;
void check(const char* label,bool ok){++count;std::cout<<(ok?"PASS ":"FAIL ")<<label<<"\n";if(!ok)throw 1;}
P::Input input(bool restore,bool vertical,double n,double reserve,double lower=128.9,double upper=129.1){double top=std::numeric_limits<double>::max();return {restore?P::Operation::RestoreOrdinary:P::Operation::Maximize,
 {0.,0.,vertical?256.:n,vertical?n:256.},{},{{vertical?0.:reserve,vertical?reserve:0.},{0.,0.}},{0.,0.},1.,
 {{0.,0.},{0.,0.}},{{vertical?0.:lower,vertical?lower:0.},{vertical?top:upper,vertical?upper:top}}};}
std::set<double> enumerate(bool restore,bool vertical,double reserve,double lower=128.9,double upper=129.1){std::set<double>s;for(int n=120;n<=140;n++){auto p=P::project(input(restore,vertical,n,reserve,lower,upper));if(p)s.insert(vertical?p->configure.y:p->configure.x);}return s;}
int main(){try{for(bool vertical:{false,true})for(bool restore:{false,true}){
 auto p=P::project(input(restore,vertical,129.,0.));check("actual409 zeroreserve admits nonfixed source interval",p&&((vertical?p->configure.y:p->configure.x)==129));
 auto values=enumerate(restore,vertical,0.);check("actual rounded enumeration onlyconfigure129",values==std::set<double>{129});
 auto solved=R::solve({120,140,0.,0.,0.,128.9,129.1});check("held176 confirms singleton domain",solved&&!solved->variable()&&solved->first==129&&solved->last==129&&solved->firstConfigure==129);
 auto quarter=enumerate(restore,vertical,.25);check("quarter reservation makesMAXnone butordinary129",restore?quarter==std::set<double>{129}:quarter.empty());
 auto qs=R::solve({120,140,restore?0.:.25,0.,0.,128.9,129.1});check("heldsolver quarter result matchesowning helper",restore?(qs&&!qs->variable()&&qs->firstConfigure==129):!qs);
 auto tenth=enumerate(restore,vertical,.1);check("tenth reservation changesMAXconfigure128 ordinary129",tenth==std::set<double>{restore?129.:128.});
 auto ts=R::solve({120,140,restore?0.:.1,0.,0.,128.9,129.1});check("heldsolver tenth matchesactual singleton",ts&&!ts->variable()&&ts->firstConfigure==*tenth.begin()&&ts->lastConfigure==*tenth.begin());
 auto wide=enumerate(restore,vertical,0.,128.9,130.1);check("wider interval has two actual configure values",wide==std::set<double>({129.,130.}));
 auto ws=R::solve({120,140,0.,0.,0.,128.9,130.1});check("heldsolver wider domain variable",ws&&ws->variable()&&ws->firstConfigure==129&&ws->lastConfigure==130);
 }
 std::cout<<"TOTAL "<<count<<"\n";return 0;}catch(...){return 1;}}
