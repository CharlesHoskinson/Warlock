#pragma once
#include "tree_revision.hpp"
#include <hyprland/src/protocols/core/Compositor.hpp>
#include <hyprland/src/protocols/core/Subcompositor.hpp>
#include <hyprland/src/protocols/core/AppliedSurfaceRevision.hpp>
#include <functional>
#include <cmath>
#include <map>
#include <optional>
namespace preview::capture {
struct SurfaceRow {SP<CWLSurfaceResource> surface;size_t parent=0;Vector2D local{};int z=0;uint64_t order=0;bool sync=false,sampled=false;};
struct SurfaceTree {std::vector<SurfaceRow> rows;std::vector<size_t> paint;};
inline std::optional<SurfaceTree> surfaceTree(SP<CWLSurfaceResource> root) {
    if(!root || !root->good())return {};
    const auto sampleable=[](const auto& surface){return surface->m_current.texture && surface->m_current.size.x>=1 && surface->m_current.size.y>=1;};
    SurfaceTree tree;tree.rows.push_back({root,0,{},0,0,false,bool(sampleable(root))});std::set<const CWLSurfaceResource*> seen{root.get()};
    for(size_t i=0;i<tree.rows.size();++i){auto parent=tree.rows[i].surface;auto local=tree.rows[i].local;uint64_t order=0;
        for(const auto& weak:parent->m_subsurfaces){++order;auto sub=weak.lock();if(!sub)continue;auto surface=sub->m_surface.lock();if(!surface)continue;
            if(tree.rows.size()>=256 || sub->m_parent.lock()!=parent || !surface->good() || !surface->m_role || surface->m_role->role()!=SURFACE_ROLE_SUBSURFACE || !seen.insert(surface.get()).second)return {};
            auto role=dynamicPointerCast<CSubsurfaceRole>(surface->m_role);if(!role || role->m_subsurface.lock()!=sub)return {};
            const auto pos=local+sub->m_position;if(!std::isfinite(pos.x) || !std::isfinite(pos.y) || std::floor(pos.x)!=pos.x || std::floor(pos.y)!=pos.y || std::abs(pos.x)>INT32_MAX || std::abs(pos.y)>INT32_MAX)return {};
            tree.rows.push_back({surface,i,pos,sub->m_zIndex,order,sub->m_sync,tree.rows[i].sampled && bool(sampleable(surface))});
        }
    }
    // Bounded graph was validated above. Accumulate offsets explicitly rather
    // than calling the core's ancestor helper with its mutable parent walk.
    std::function<void(size_t)> paint=[&](size_t i){for(size_t j=1;j<tree.rows.size();++j)if(tree.rows[j].parent==i && tree.rows[j].z<0)paint(j);tree.paint.push_back(i);for(size_t j=1;j<tree.rows.size();++j)if(tree.rows[j].parent==i && tree.rows[j].z>=0)paint(j);};paint(0);
    return tree;
}
struct TrackedSurface {WP<CWLSurfaceResource> surface;uint64_t id=0;};
class SurfaceRevisionTracker {
    std::map<const CWLSurfaceResource*,TrackedSurface> identities_;uint64_t next_=0;bool exhausted_=false;
    TreeRevision revision_;
public:
    uint64_t observe(const SurfaceTree& tree) {
        if(exhausted_)return 0;
        std::vector<TreeNode> nodes;std::set<const CWLSurfaceResource*> seen;
        for(const auto& row:tree.rows){auto p=row.surface.get();seen.insert(p);auto found=identities_.find(p);
            if(found!=identities_.end() && found->second.surface.lock()!=row.surface){identities_.erase(found);found=identities_.end();}
            if(found==identities_.end()){if(next_==UINT64_MAX){exhausted_=true;return 0;}found=identities_.emplace(p,TrackedSurface{row.surface,++next_}).first;}
            const auto sampled=row.sampled;
            nodes.push_back({found->second.id,nodes.empty()?0:nodes[row.parent].id,Warlock::appliedSurfaceRevision(p),static_cast<int64_t>(row.local.x),static_cast<int64_t>(row.local.y),row.z,row.order,bool(sampled),row.sync});
        }
        std::erase_if(identities_,[&](const auto& pair){return !seen.contains(pair.first);});
        return revision_.observe(std::move(nodes))?revision_.value():0;
    }
    // Read existing native incarnation, without allocation or a raw pointer in the snapshot.
    uint64_t identity(const SP<CWLSurfaceResource>& surface)const {
        if(exhausted_ || !surface)return 0;
        const auto found=identities_.find(surface.get());
        return found!=identities_.end() && found->second.surface.lock()==surface?found->second.id:0;
    }
    void unavailable(){revision_.observe({},false);}
};
}
