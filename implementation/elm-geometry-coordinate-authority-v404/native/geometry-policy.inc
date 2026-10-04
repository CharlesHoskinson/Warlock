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
