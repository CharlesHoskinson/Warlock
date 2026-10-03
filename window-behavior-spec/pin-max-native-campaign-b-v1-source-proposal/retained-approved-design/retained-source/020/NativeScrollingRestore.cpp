#include "NativeScrollingRestore.hpp"
#include "ScrollingAlgorithm.hpp"
#include <cmath>
#include <unordered_set>
using namespace Fullscreen::ScrollingFullscreenHandler;

bool Fullscreen::ScrollingFullscreenHandler::nativeReturnValid(const SP<Layout::Tiled::SScrollingData>& owner, const SP<Layout::Tiled::SScrollingTargetData>& selected,
                                                               const SNativeScrollRestore& restore) {
    const auto column = restore.column.lock();
    if (!owner || !owner->controller || !selected || !selected->target || !selected->column || selected->column->scrollingData != owner || !column ||
        column->scrollingData != owner || owner->idx(column) < 0 || owner->idx(selected->column.lock()) < 0 || !std::isfinite(restore.width) || restore.width <= 0.F ||
        !std::isfinite(restore.offset) || restore.rows.empty() || selected->column->targetDatas.size() != 1 || selected->column->targetDatas.front() != selected)
        return false;
    const auto& current = column == selected->column ? restore.rows : restore.remaining;
    if (column->targetDatas.size() != current.size())
        return false;
    for (size_t i = 0; i < current.size(); ++i) {
        const auto row = current[i].data.lock();
        if (!row || !row->target || column->targetDatas[i] != row || row->column != column || !std::isfinite(current[i].size) || current[i].size <= 0.F ||
            (column != selected->column && column->getTargetSize(i) != current[i].size))
            return false;
    }
    bool                                    containsSelected = false;
    std::unordered_set<WP<Layout::ITarget>> targets;
    for (const auto& saved : restore.rows) {
        const auto row = saved.data.lock();
        if (!row || !row->target || !targets.insert(row->target).second || row->target->space() != selected->target->space() || !std::isfinite(saved.size) || saved.size <= 0.F)
            return false;
        if (row == selected)
            containsSelected = true;
        else if (row->column != column)
            return false;
    }
    return containsSelected;
}

bool Fullscreen::ScrollingFullscreenHandler::restoreNativeColumn(const SP<Layout::Tiled::SScrollingData>& owner, const SP<Layout::Tiled::SScrollingTargetData>& selected,
                                                                 const SNativeScrollRestore& restore) {
    if (!nativeReturnValid(owner, selected, restore))
        return false;
    const auto original     = restore.column.lock();
    const auto current      = selected->column.lock();
    const auto layoutTarget = selected->target.lock();
    if (original != current) {
        const auto index = std::ranges::find_if(restore.rows, [&](const auto& row) { return row.data == selected; }) - restore.rows.begin();
        current->remove(layoutTarget);
        original->add(selected, sc<int>(index) - 1);
    }
    original->setColumnWidth(restore.width);
    for (size_t i = 0; i < restore.rows.size(); ++i)
        original->setTargetSize(i, restore.rows[i].size);
    owner->controller->setOffset(restore.offset);
    return true;
}
