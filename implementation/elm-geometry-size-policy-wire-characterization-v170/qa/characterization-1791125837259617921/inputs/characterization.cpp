
#include <bit>
#include <charconv>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include "candidate/PlacementPolicy.hpp"
#include "candidate/ProspectiveGeometry.hpp"
using Hyprutils::Math::CBox;
using Hyprutils::Math::Vector2D;
using Hyprutils::Math::SBoxExtents;
struct Target {std::optional<Vector2D> minimum=Vector2D{108,42},maximum; auto minSize(){return minimum;}auto maxSize(){return maximum;}};
struct Raw {Vector2D minSize{108,42},maxSize{0,0};};
struct Top {Raw m_current;};
struct XdgCurrent {CBox geometry{0,0,320,180};};
struct Xdg {std::shared_ptr<Top> m_toplevel=std::make_shared<Top>();XdgCurrent m_current;};
struct Monitor {double m_scale=1;};
struct Space {CBox area{0,0,800,600};CBox workArea(bool){return area;}};
struct Workspace {std::shared_ptr<Space> m_space=std::make_shared<Space>();};
struct Window {
 std::shared_ptr<Target> target=std::make_shared<Target>();bool m_isX11=false;
 std::shared_ptr<Xdg> m_xdgSurface=std::make_shared<Xdg>();
 std::shared_ptr<Monitor> keepMonitor=std::make_shared<Monitor>();std::weak_ptr<Monitor> m_monitor=keepMonitor;
 std::shared_ptr<Workspace> m_workspace=std::make_shared<Workspace>();
 SBoxExtents reserved{Vector2D{0,24},Vector2D{0,0}};
 auto layoutTarget(){return target;}auto getFullWindowReservedArea(){return reserved;}
};
using PHLWINDOW=std::shared_ptr<Window>;

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
using GeometryProjection=Elm::ProspectiveGeometry::Projection;
std::optional<Elm::ProspectiveGeometry::Input> geometryInput(const PHLWINDOW& window,
    Elm::ProspectiveGeometry::Operation operation,const CBox& logical,const CBox& visual) {
    if(!window->layoutTarget() || window->m_isX11 || !window->m_xdgSurface || !window->m_xdgSurface->m_toplevel || !window->m_monitor.lock())return {};
    const auto target=window->layoutTarget();
    const auto& raw=window->m_xdgSurface->m_toplevel->m_current;
    const auto minimum=target->minSize(),maximum=target->maxSize();
    const double unlimited=std::numeric_limits<double>::max();
    return Elm::ProspectiveGeometry::Input{operation,logical,visual,window->getFullWindowReservedArea(),
        window->m_xdgSurface->m_current.geometry.pos(),window->m_monitor.lock()->m_scale,
        {raw.minSize,raw.maxSize},{minimum.value_or(Vector2D{0,0}),maximum.value_or(Vector2D{unlimited,unlimited})}};
}
std::optional<GeometryProjection> geometryProspective(const PHLWINDOW& window,bool maximize,
    const std::optional<Elm::Placement::Original>& original={}) {
    if(!window->m_workspace || !window->m_workspace->m_space)return {};
    CBox logical=window->m_workspace->m_space->workArea(true),visual;
    if(!maximize) {
        if(!original)return {};
        const auto& r=original->logical;logical={r.x,r.y,r.width,r.height};
        const auto& v=original->visual;visual={v.x,v.y,v.width,v.height};
    }
    const auto input=geometryInput(window,maximize?Elm::ProspectiveGeometry::Operation::Maximize:
        Elm::ProspectiveGeometry::Operation::RestoreOrdinary,logical,visual);
    if(!input)return {};
    auto projected=Elm::ProspectiveGeometry::project(*input);
    if(projected && !maximize && projected->real!=visual)return {};
    return projected;
}
std::string geometryVector(Vector2D vector) {
    return "["+geometryNumber(vector.x)+","+geometryNumber(vector.y)+"]";
}
std::string geometryPolicyInputs(const PHLWINDOW& window) {
    const auto input=geometryInput(window,Elm::ProspectiveGeometry::Operation::Maximize,CBox{0,0,1,1},{});
    if(!input)return "null";
    // Conversion invalidity is observed explicitly without publishing NaN JSON.
    using namespace Elm::ProspectiveGeometry;
    if(!validBounds(input->raw,true) || !validBounds(input->layout,false) ||
       !finite(input->xdgGeometryOrigin) || !nonnegative(input->reserved.topLeft) ||
       !nonnegative(input->reserved.bottomRight) || !std::isfinite(input->monitorScale) || input->monitorScale<=0)return "null";
    return "{\"profile\":\"wayland-zero-origin-v1\",\"rawMinimum\":"+geometryVector(input->raw.minimum)+
        ",\"rawMaximum\":"+geometryVector(input->raw.maximum)+",\"layoutMinimum\":"+geometryVector(input->layout.minimum)+
        ",\"layoutMaximum\":"+geometryVector(input->layout.maximum)+",\"geometryOrigin\":"+geometryVector(input->xdgGeometryOrigin)+
        ",\"reservedTopLeft\":"+geometryVector(input->reserved.topLeft)+",\"reservedBottomRight\":"+geometryVector(input->reserved.bottomRight)+
        ",\"monitorScale\":"+geometryNumber(input->monitorScale)+"}";
}
std::string geometryProjected(const std::optional<GeometryProjection>& projected) {
    if(!projected)return "null";
    return "{\"logical\":"+geometryRect(projected->logical)+",\"visual\":"+
        (projected->visual.empty()?std::string("null"):geometryRect(projected->visual))+
        ",\"real\":"+geometryRect(projected->real)+",\"configure\":"+geometryVector(projected->configure)+"}";
}

// Preserve dependency revisions even for invalid/fixed constraints that cannot
// safely be emitted as supported JSON conversion inputs.
std::string geometryConstraintFingerprint(const PHLWINDOW& window) {
    const auto input=geometryInput(window,Elm::ProspectiveGeometry::Operation::Maximize,CBox{0,0,1,1},{});
    if(!input)return "unavailable";
    std::string result;
    const auto append=[&](double value){result+=":"+std::to_string(std::bit_cast<uint64_t>(value));};
    for(const auto vector:{input->raw.minimum,input->raw.maximum,input->layout.minimum,input->layout.maximum,
        input->xdgGeometryOrigin,input->reserved.topLeft,input->reserved.bottomRight}) {append(vector.x);append(vector.y);}
    append(input->monitorScale);return result;
}


std::string fragment(int protocol,const PHLWINDOW& window,const std::optional<GeometryProjection>& maximizeProjection,const std::optional<GeometryProjection>& restoreProjection){
const auto sizePolicy=protocol==2 ? ",\"sizePolicy\":{\"inputs\":"+geometryPolicyInputs(window)+",\"maximize\":"+geometryProjected(maximizeProjection)+",\"restoreGeometry\":"+geometryProjected(restoreProjection)+"}" : "";
 return "{"+(sizePolicy.empty()?std::string():sizePolicy.substr(1))+"}";
}
void emit(const char* name,const PHLWINDOW& window,int protocol=2){
 const std::optional<Elm::Placement::Original> original=Elm::Placement::Original{{120,130,320,180},{120,130,320,180}};
 const auto maximize=geometryProspective(window,true),restore=geometryProspective(window,false,original);
 std::cout<<"{\"case\":\""<<name<<"\",\"geometryInputAvailable\":"<<(geometryInput(window,Elm::ProspectiveGeometry::Operation::Maximize,CBox{0,0,1,1},{}).has_value()?"true":"false")<<",\"producerFragment\":"<<fragment(protocol,window,maximize,restore)<<"}\n";
}
int main(){
 auto w=std::make_shared<Window>();emit("GTK108x42-no-layout-maximum",w);emit("version1",w,1);
 w->target.reset();emit("unavailable-target",w);w=std::make_shared<Window>();w->m_xdgSurface->m_toplevel.reset();emit("unavailable-toplevel",w);
 w=std::make_shared<Window>();w->m_monitor.reset();emit("unavailable-monitor",w);
 w=std::make_shared<Window>();w->target->maximum=Vector2D{320,600};w->target->minimum=Vector2D{320,42};emit("fixed-layout-axis",w);
 w=std::make_shared<Window>();w->m_xdgSurface->m_toplevel->m_current.minSize={320,0};w->m_xdgSurface->m_toplevel->m_current.maxSize={320,0};emit("fixed-raw-axis",w);
 w=std::make_shared<Window>();w->m_xdgSurface->m_toplevel->m_current.maxSize={-1,0};emit("invalid-negative-raw",w);
 w=std::make_shared<Window>();w->target->maximum=Vector2D{std::numeric_limits<double>::quiet_NaN(),600.0};emit("invalid-nonfinite-layout",w);
 w=std::make_shared<Window>();w->m_xdgSurface->m_current.geometry.x=8;w->m_xdgSurface->m_current.geometry.y=9;emit("unsupported-nonzero-origin",w);
 w=std::make_shared<Window>();w->m_xdgSurface->m_toplevel->m_current.maxSize={400,300};w->target->maximum=Vector2D{900,700};emit("raw-maximum-widened-by-layout-rule",w);
 w=std::make_shared<Window>();w->keepMonitor->m_scale=2;emit("scale2-already-logical-input",w);
 w=std::make_shared<Window>();w->m_workspace.reset();emit("unavailable-workspace",w);
}
