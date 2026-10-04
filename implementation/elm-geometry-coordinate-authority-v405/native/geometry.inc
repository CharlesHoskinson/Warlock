// Isolated effect2 qualification candidate; capability truth follows native guards.
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
    const auto fingerprint=std::to_string(output)+":"+std::to_string(outputGeneration)+":"+rectangle;
    auto found=std::ranges::find_if(geometryAreas,[&](const GeometryArea& area){return area.workspace==workspace;});
    if(found!=geometryAreas.end() && found->fingerprint==fingerprint) return found->revision;
    if(geometryAreaRevision==std::numeric_limits<uint64_t>::max() || (found==geometryAreas.end() && geometryAreas.size()>=256)) throw std::runtime_error("Geometry workarea bound");
    if(found==geometryAreas.end()) {geometryAreas.push_back({workspace,++geometryAreaRevision,fingerprint});return geometryAreaRevision;}
    found->fingerprint=fingerprint;found->revision=++geometryAreaRevision;return found->revision;
}
#include "geometry-policy.inc"
std::string geometryFacts(int protocol) {
    refreshOutputs();
    const auto boolean=[](bool value){return value?"true":"false";};
    const bool blocked=g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty() || g_pSeatManager->m_seatGrab || g_layoutManager->dragController()->target();
    std::string result="{\"focused\":"+identityOf(Desktop::focusState()->window())+",\"inputBlocked\":"+boolean(blocked)+",\"windows\":[";
    size_t count=0;
    for(const auto& window:Desktop::windowState()->windows()) {
        if(!window->m_isMapped) continue;
        if(++count>256) throw std::runtime_error("Geometry window bound");
        if(count>1) result+=',';
        const auto target=window->layoutTarget();if(!target) throw std::runtime_error("Missing geometry target");
        const auto workspace=window->m_workspace;const auto output=window->m_monitor.lock();
        const auto modes=Fullscreen::controller()->getFullscreenModes(window);
        const auto minimum=target->minSize(),maximum=target->maxSize();
        const bool fixed=minimum && maximum && minimum->x>0 && minimum->y>0 && *minimum==*maximum;
        const bool rawConstrained=window->m_xdgSurface && window->m_xdgSurface->m_toplevel && (window->m_xdgSurface->m_toplevel->m_current.maxSize.x>0 || window->m_xdgSurface->m_toplevel->m_current.maxSize.y>0 || window->m_xdgSurface->m_toplevel->m_current.minSize.x>1 || window->m_xdgSurface->m_toplevel->m_current.minSize.y>1);
        const bool constrained=rawConstrained ||(minimum && (minimum->x>1 || minimum->y>1)) || (maximum && (maximum->x<std::numeric_limits<double>::max() || maximum->y<std::numeric_limits<double>::max()));
        const bool eligible=geometryTargetEligible(window,protocol);
        std::optional<Elm::Placement::Original> saved;
        bool placementKnown=false, originalCompatible=true, unresolved=false;
        std::string workspaceId="null",workspaceOwner="null",outputId="null",outputOwner="null",workRevision="null",workArea="null";
        if(workspace && output && workspace->m_space) {
            if(output->m_id<0) throw std::runtime_error("Invalid output identity");
            const auto wg=geometryWorkspaces.bind(workspace),og=geometryOutputs.bind(output);
            workArea=geometryRect(workspace->m_space->workArea(true));
            workspaceId=quote(std::to_string(workspace->m_id));workspaceOwner=quote(std::to_string(wg));
            outputId=quote(std::to_string(output->m_id));outputOwner=quote(std::to_string(og));
            const auto areaRevision=geometryWorkAreaRevision(wg,og,workArea);
            workRevision=quote(std::to_string(areaRevision));
            const auto entry=std::ranges::find_if(members,[&](const Member& member){return member.window.lock()==window;});
            if(entry!=members.end()) {
                const auto key=Elm::Placement::Identity::fromNative(lifetime,entry->id);
                const auto scope=Elm::Placement::Scope::fromNative(workspace->m_id,wg,static_cast<uint64_t>(output->m_id),og,areaRevision);
                if(key && scope) {
                    const auto known=geometryPlacements.read(*key,key,*scope);saved=known;placementKnown=known.has_value();
                    const bool retained=geometryPlacements.hasRecord(*key,key);
                    originalCompatible=retained ? placementKnown : geometryPlacements.size()<Elm::Placement::Records::capacity;
                    if(known && modes.internal==Fullscreen::FSMODE_NONE) {
                        const Elm::Placement::Original current{{target->position().x,target->position().y,target->position().w,target->position().h},{window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL).x,window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL).y,window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL).w,window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL).h}};
                        originalCompatible=current==*known;
                    }
                }
                unresolved=effectBarriers.blocked({lifetime,entry->id});
            }
        }
        const auto visual=window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL);
        const auto maximizeProjection=geometryProspective(window,true),restoreProjection=geometryProspective(window,false,saved);
        const auto sizePolicy=protocol==2 ? ",\"sizePolicy\":{\"inputs\":"+geometryPolicyInputs(window)+",\"maximize\":"+geometryProjected(maximizeProjection)+",\"restoreGeometry\":"+geometryProjected(restoreProjection)+"}" : "";
        result+="{\"incarnation\":"+identityOf(window)+",\"owner\":"+identityOf(window->parent())+",\"workspace\":"+workspaceId+",\"workspaceGeneration\":"+workspaceOwner+",\"monitor\":"+outputId+",\"outputOwnershipGeneration\":"+outputOwner+",\"workAreaRevision\":"+workRevision+",\"workArea\":"+workArea+",\"logicalGeometry\":"+geometryRect(target->position())+",\"visualGeometry\":"+geometryRect(visual)+",\"nativeMode\":"+geometryMode(modes.internal)+",\"clientMode\":"+geometryMode(modes.client)+",\"minimized\":"+boolean(Desktop::WindowPolicy::isMinimized(window))+",\"floating\":"+boolean(target->floating())+",\"grouped\":"+boolean(!!window->m_group)+",\"fixedSize\":"+boolean(fixed)+",\"constrainedSize\":"+boolean(constrained)+",\"geometryEligible\":"+boolean(eligible)+",\"ordinaryPlacementKnown\":"+boolean(placementKnown)+sizePolicy+",\"capabilities\":{\"maximize\":"+boolean(eligible && (protocol==1 || maximizeProjection.has_value()) && !unresolved && originalCompatible && modes.internal==Fullscreen::FSMODE_NONE)+",\"restoreGeometry\":"+boolean(eligible && (protocol==1 || restoreProjection.has_value()) && !unresolved && modes.internal==Fullscreen::FSMODE_MAXIMIZED && placementKnown)+"}}";
    }
    return result+"]}";
}
std::string refreshGeometryFacts(int protocol=1) {
    const auto value=geometryFacts(2);
    if(value!=previousGeometry) {if(geometryRevision==std::numeric_limits<uint64_t>::max()) throw std::runtime_error("Geometry revision exhausted");++geometryRevision;previousGeometry=value;}
    return protocol==2 ? value : geometryFacts(1);
}
