#pragma once
#include "../../../../helpers/memory/Memory.hpp"
#include <vector>
namespace Layout::Tiled {
    struct SScrollingData;
    struct SScrollingTargetData;
    struct SColumnData;
}
namespace Fullscreen::ScrollingFullscreenHandler {
    struct SNativeScrollRow {
        WP<Layout::Tiled::SScrollingTargetData> data;
        float                                   size = 0.F;
    };

    struct SNativeScrollRestore {
        WP<Layout::Tiled::SColumnData> column;
        std::vector<SNativeScrollRow>  rows;
        std::vector<SNativeScrollRow>  remaining;
        float                          width  = 0.F;
        double                         offset = 0.;
    };

    bool nativeReturnValid(const SP<Layout::Tiled::SScrollingData>& owner, const SP<Layout::Tiled::SScrollingTargetData>& selected, const SNativeScrollRestore& restore);
    bool restoreNativeColumn(const SP<Layout::Tiled::SScrollingData>& owner, const SP<Layout::Tiled::SScrollingTargetData>& selected, const SNativeScrollRestore& restore);
}
