#define main originalRegressionMain
#include "../plugin/test_pin_action.cpp"
#undef main
static Adapter native(bool known=true) {
 Adapter a;a.s.floating=false;a.s.pinned=true;a.s.fullscreen=true;a.s.internalMode=1;a.s.clientMode=1;a.s.capability=1;
 a.s.nativeAdmission=known;a.s.ownedUnpinReady=true;a.s.restoreKnown=known;a.s.restoreOrigin=true;a.s.restoreManaged=true;a.s.restoreFloating=false;
 a.s.restoreGeneration=9;a.s.target=201;a.s.layoutTarget=202;a.s.space=203;a.s.workspace=204;a.s.monitor=205;
 a.s.geometry={10,20,1280,720};a.s.restoreGeometry={30,40,600,400,31,41,598,398};
 a.afterPin=[](Adapter&x){x.s.restoreOrigin=x.s.pinned;x.s.restoreManaged=true;x.s.ownedUnpinReady=x.s.pinned;};return a;
}
int main(){
 originalRegressionMain();int checks=0;auto check=[&](bool v){++checks;assert(v);};
 {auto a=native();auto before=a.s;auto r=execute(a);check(r.ok&&!a.s.pinned&&a.calls==std::vector<std::string>{"unpin"});check(a.s.geometry==before.geometry&&a.s.restoreGeometry==before.restoreGeometry&&a.s.internalMode==1&&a.s.clientMode==1&&!a.s.floating);}
 {auto a=native(false);auto r=execute(a);check(r.ok&&!a.s.pinned&&a.calls==std::vector<std::string>{"unpin"}&&!a.s.restoreKnown&&!a.s.nativeAdmission);}
 {auto a=native(false);a.s.internalMode=0;a.s.fullscreen=false;auto r=execute(a);check(r.ok&&a.calls==std::vector<std::string>{"unpin"}&&!a.s.floating&&a.s.clientMode==1);}
 {auto a=native(false);a.s.internalMode=2;a.s.clientMode=2;auto r=execute(a);check(r.ok&&a.calls==std::vector<std::string>{"unpin"}&&a.s.internalMode==2&&a.s.clientMode==2);}
 {auto a=native(false);a.s.live=false;check(!execute(a).ok&&a.calls.empty());}
 {auto a=native(false);a.s.normal=false;check(!execute(a).ok&&a.calls.empty());}
 {auto a=native(false);a.s.ownedUnpinReady=false;check(!execute(a).ok&&a.calls.empty());}
 {auto a=native(false);a.s.restoreGeneration=0;check(!execute(a).ok&&a.calls.empty());}
 {auto a=native(false);a.s.pinned=false;check(!execute(a).ok&&a.calls.empty());}
 {auto a=native(false);a.afterPin=[](Adapter&x){x.s.lifetime++;x.s.restoreOrigin=false;x.s.ownedUnpinReady=false;};auto r=execute(a);check(!r.ok&&r.actionsInvoked&&a.calls==std::vector<std::string>{"unpin"});}
 {auto a=native(false);a.afterPin=[](Adapter&x){x.s.geometry[0]+=1;x.s.restoreOrigin=false;x.s.ownedUnpinReady=false;};check(!execute(a).ok&&a.calls==std::vector<std::string>{"unpin"});}
 {auto a=native(false);a.afterPin=[](Adapter&x){x.s.space++;x.s.restoreOrigin=false;x.s.ownedUnpinReady=false;};check(!execute(a).ok&&a.calls==std::vector<std::string>{"unpin"});}
 {auto a=native();a.s.pinned=false;a.s.restoreOrigin=false;a.s.restoreManaged=false;a.s.ownedUnpinReady=false;auto r=execute(a);check(r.ok&&a.calls==std::vector<std::string>{"pin","raise"}&&!a.s.floating&&a.s.internalMode==1);}
 std::cout<<checks<<" native MAX/stale-owned intent action checks passed\n";
}
