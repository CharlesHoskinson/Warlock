
#include <algorithm>
#include <charconv>
#include <cmath>
#include <cstdio>
#include <cstdint>
#include <limits>
#include <memory>
#include <ranges>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
struct Object{};
using PHLWORKSPACEREF=std::weak_ptr<Object>;
using PHLMONITORREF=std::weak_ptr<Object>;
struct CBox{double x,y,w,h;};
namespace Fullscreen {enum eFullscreenMode{FSMODE_NONE=0,FSMODE_MAXIMIZED=1,FSMODE_FULLSCREEN=2};}
std::string quote(const std::string&s){return "\""+s+"\"";}
uint64_t outputGeneration=1;

// Separate negotiated observation contract. Geometry effects are unavailable
// until their native mutation/journal/readback path is qualified.
template<class Weak> struct GeometryOwners {
    using Strong=decltype(std::declval<Weak>().lock());
    struct Entry { Weak object; uint64_t generation; };
    std::vector<Entry> entries;
    uint64_t next=0;
    uint64_t bind(const Strong& object) {
        if(!object) throw std::runtime_error("Missing native geometry owner");
        std::erase_if(entries,[](const Entry& entry){return !entry.object.lock();});
        for(const auto& entry:entries) if(entry.object.lock()==object) return entry.generation;
        if(entries.size()>=256 || next==std::numeric_limits<uint64_t>::max()) throw std::runtime_error("Geometry owner bound");
        entries.push_back({Weak{object},++next});return next;
    }
    bool live(uint64_t generation) const {
        return std::ranges::any_of(entries,[&](const Entry& entry){return entry.generation==generation && entry.object.lock();});
    }
};
GeometryOwners<PHLWORKSPACEREF> geometryWorkspaces;
GeometryOwners<PHLMONITORREF> geometryOutputs;
struct GeometryArea { uint64_t workspace, revision; std::string fingerprint; };
std::vector<GeometryArea> geometryAreas;
uint64_t geometryAreaRevision=0, geometrySequence=0, geometryRevision=0;
std::string previousGeometry;

std::string geometryNumber(double value) {
    if(!std::isfinite(value)) throw std::runtime_error("Nonfinite geometry");
    char buffer[64];const auto result=std::to_chars(buffer,buffer+sizeof(buffer),value,std::chars_format::general,std::numeric_limits<double>::max_digits10);
    if(result.ec!=std::errc{}) throw std::runtime_error("Geometry number bound");
    return std::string(buffer,result.ptr);
}
std::string geometryRect(const CBox& box) {
    if(box.w<=0 || box.h<=0 || !std::isfinite(box.x+box.w) || !std::isfinite(box.y+box.h)) throw std::runtime_error("Invalid geometry rectangle");
    return "["+geometryNumber(box.x)+","+geometryNumber(box.y)+","+geometryNumber(box.w)+","+geometryNumber(box.h)+"]";
}
std::string geometryMode(Fullscreen::eFullscreenMode mode) {
    switch(mode) {
        case Fullscreen::FSMODE_NONE:return quote("ordinary");
        case Fullscreen::FSMODE_MAXIMIZED:return quote("maximized");
        case Fullscreen::FSMODE_FULLSCREEN:return quote("fullscreen");
        default:throw std::runtime_error("Unknown native geometry mode");
    }
}
uint64_t geometryWorkAreaRevision(uint64_t workspace,uint64_t output,const std::string& rectangle) {
    std::erase_if(geometryAreas,[](const GeometryArea& area){return !geometryWorkspaces.live(area.workspace);});
    const auto fingerprint=std::to_string(output)+":"+rectangle;
    auto found=std::ranges::find_if(geometryAreas,[&](const GeometryArea& area){return area.workspace==workspace;});
    if(found!=geometryAreas.end() && found->fingerprint==fingerprint) return found->revision;
    if(geometryAreaRevision==std::numeric_limits<uint64_t>::max() || (found==geometryAreas.end() && geometryAreas.size()>=256)) throw std::runtime_error("Geometry workarea bound");
    if(found==geometryAreas.end()) {geometryAreas.push_back({workspace,++geometryAreaRevision,fingerprint});return geometryAreaRevision;}
    found->fingerprint=fingerprint;found->revision=++geometryAreaRevision;return found->revision;
}


int main(){unsigned checks=0;
 auto verify=[&](bool value,const char*name){++checks;if(!value)std::fprintf(stderr,"FAIL %s\n",name);return value;};
 auto throws=[](auto work){try{work();return false;}catch(const std::runtime_error&){return true;}};
 GeometryOwners<PHLWORKSPACEREF> owners;
 auto a=std::make_shared<Object>();auto first=owners.bind(a);
 if(!verify(first!=0&&owners.bind(a)==first&&owners.live(first),"same owner stable generation"))return 1;
 a.reset();if(!verify(!owners.live(first),"destroyed owner unavailable"))return 1;
 a=std::make_shared<Object>();auto replacement=owners.bind(a);
 if(!verify(replacement>first&&!owners.live(first),"replacement cannot inherit old generation"))return 1;
 if(!verify(throws([&]{owners.bind({});}),"null owner refused"))return 1;
 owners.next=UINT64_MAX;
 if(!verify(owners.bind(a)==replacement,"existing owner still readable at generation bound"))return 1;
 if(!verify(throws([&]{owners.bind(std::make_shared<Object>());}),"owner generation overflow refused"))return 1;
 GeometryOwners<PHLWORKSPACEREF> bounded;std::vector<std::shared_ptr<Object>> held;
 for(unsigned i=0;i<256;++i){held.push_back(std::make_shared<Object>());if(!verify(bounded.bind(held.back())==i+1,"bounded owner allocation"))return 1;}
 if(!verify(throws([&]{bounded.bind(std::make_shared<Object>());}),"257th live owner refused"))return 1;
 auto old=bounded.bind(held.front());held.front().reset();auto fresh=std::make_shared<Object>();auto next=bounded.bind(fresh);
 if(!verify(next==257&&!bounded.live(old)&&bounded.entries.size()==256,"expired slot reclaimed without generation reuse"))return 1;
 auto workspace=std::make_shared<Object>();auto wg=geometryWorkspaces.bind(workspace);
 auto output=std::make_shared<Object>();auto og=geometryOutputs.bind(output);
 auto area=geometryWorkAreaRevision(wg,og,"[0,0,800,600]");
 if(!verify(area!=0&&geometryWorkAreaRevision(wg,og,"[0,0,800,600]")==area,"unchanged workarea revision stable"))return 1;
 auto reserved=geometryWorkAreaRevision(wg,og,"[0,20,800,580]");
 if(!verify(reserved>area,"reserved-area-only change advances revision"))return 1;
 ++outputGeneration;auto config=geometryWorkAreaRevision(wg,og,"[0,20,800,580]");
 if(!verify(config>reserved,"same box output configuration change advances revision"))return 1;
 auto output2=std::make_shared<Object>();auto og2=geometryOutputs.bind(output2);
 auto newOwner=geometryWorkAreaRevision(wg,og2,"[0,20,800,580]");
 if(!verify(newOwner>config,"output replacement advances workarea revision"))return 1;
 workspace.reset();workspace=std::make_shared<Object>();auto wg2=geometryWorkspaces.bind(workspace);
 auto replacementArea=geometryWorkAreaRevision(wg2,og2,"[0,20,800,580]");
 if(!verify(wg2!=wg&&replacementArea>newOwner&&geometryAreas.size()==1,"workspace retirement prunes old area"))return 1;
 geometryAreaRevision=UINT64_MAX;
 if(!verify(geometryWorkAreaRevision(wg2,og2,"[0,20,800,580]")==replacementArea,"unchanged workarea remains readable at overflow"))return 1;
 if(!verify(throws([&]{geometryWorkAreaRevision(wg2,og2,"[1,20,799,580]");}),"workarea revision overflow refused"))return 1;
 for(double value:{0.0,-0.0,0.1,-1.25,1e-200,std::numeric_limits<double>::max()}){
  std::string text=geometryNumber(value);double parsed=0;auto r=std::from_chars(text.data(),text.data()+text.size(),parsed);
  if(!verify(r.ec==std::errc{}&&r.ptr==text.data()+text.size()&&parsed==value,"finite numbers serialize losslessly"))return 1;
 }
 for(double value:{std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})
  if(!verify(throws([&]{geometryNumber(value);}),"nonfinite number refused"))return 1;
 if(!verify(geometryRect({83,61,320,180})=="[83,61,320,180]","rectangle preserves noncentered origin"))return 1;
 if(!verify(geometryRect({-83,-61,320,180})=="[-83,-61,320,180]","negative origin supported"))return 1;
 for(CBox box:std::vector<CBox>{{0,0,0,1},{0,0,1,0},{0,0,-1,1},{0,0,1,-1},{INFINITY,0,1,1},{0,NAN,1,1},{0,0,NAN,1},{0,0,1,INFINITY},{std::numeric_limits<double>::max(),0,std::numeric_limits<double>::max(),1}})
  if(!verify(throws([&]{geometryRect(box);}),"invalid rectangle refused"))return 1;
 if(!verify(geometryMode(Fullscreen::FSMODE_NONE)=="\"ordinary\"","ordinary enum"))return 1;
 if(!verify(geometryMode(Fullscreen::FSMODE_MAXIMIZED)=="\"maximized\"","maximized enum"))return 1;
 if(!verify(geometryMode(Fullscreen::FSMODE_FULLSCREEN)=="\"fullscreen\"","fullscreen enum"))return 1;
 for(int value:{-1,3,INT32_MAX})if(!verify(throws([&]{geometryMode(static_cast<Fullscreen::eFullscreenMode>(value));}),"unknown mode refused"))return 1;
 std::printf("checks %u\n",checks);return 0;
}
