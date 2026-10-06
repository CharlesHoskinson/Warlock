#pragma once
#include "surface_tree.hpp"
#include "../../desktop/view/Popup.hpp"
#include "../../desktop/view/Window.hpp"
namespace preview::capture {
// Read current native renderer membership, never a web-provided family list.
// This is a distinct observer for root/subsurfaces plus owned visible popups;
// decoration and modal capture authority remain independently unqualified.
inline std::optional<SurfaceTree> rootPopupTree(PHLWINDOW window) {
    if(!window || !window->wlSurface() || !window->m_popupHead)return {};
    const auto root=window->wlSurface()->resource();auto tree=surfaceTree(root);if(!tree)return {};
    std::set<const CWLSurfaceResource*> seen;
    for(const auto& row:tree->rows)seen.insert(row.surface.get());
    bool valid=true;size_t visited=0;uint64_t popupOrder=0;
    window->m_popupHead->breadthfirst([&](SP<Desktop::View::CPopup> popup,void*) {
        if(!valid)return;
        if(!popup || ++visited>256){valid=false;return;}
        if(!popup->aliveAndVisible())return;
        const auto owner=popup->getT1Owner();
        if(!owner || owner->resource()!=root || !popup->resource()){valid=false;return;}
        const auto position=popup->coordsRelativeToParent();
        if(!std::isfinite(position.x) || !std::isfinite(position.y) || std::floor(position.x)!=position.x || std::floor(position.y)!=position.y || std::abs(position.x)>INT32_MAX || std::abs(position.y)>INT32_MAX){valid=false;return;}
        const auto part=surfaceTree(popup->resource());
        if(!part || part->rows.size()>256-tree->rows.size()){valid=false;return;}
        const size_t base=tree->rows.size();++popupOrder;
        for(size_t i=0;i<part->rows.size();++i){auto row=part->rows[i];
            if(!seen.insert(row.surface.get()).second){valid=false;return;}
            row.local+=position;
            if(!std::isfinite(row.local.x) || !std::isfinite(row.local.y) || std::abs(row.local.x)>INT32_MAX || std::abs(row.local.y)>INT32_MAX){valid=false;return;}
            row.parent=i?base+row.parent:0;
            if(!i){row.z=1;row.order=popupOrder;}
            tree->rows.push_back(std::move(row));
        }
    },nullptr);
    if(!valid)return {};
    return tree;
}
}
