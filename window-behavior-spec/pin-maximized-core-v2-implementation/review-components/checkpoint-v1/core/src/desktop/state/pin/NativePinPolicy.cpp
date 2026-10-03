#include "NativePinPolicy.hpp"
#include <algorithm>
#include <numeric>
#include <functional>
#include <unordered_set>

std::optional<std::vector<size_t>> Desktop::Pin::orderBand(const std::vector<SBandNode>& nodes) {
    if (nodes.size() > 512)
        return std::nullopt;
    std::unordered_set<uintptr_t> keys;
    std::vector<size_t> roots(nodes.size()), rank(nodes.size(), 0);
    for (size_t i = 0; i < nodes.size(); ++i) {
        if (!nodes[i].key || !keys.insert(nodes[i].key).second)
            return std::nullopt;
        std::unordered_set<size_t> seen;
        size_t current = i;
        while (nodes[current].parent >= 0) {
            if (!seen.insert(current).second || static_cast<size_t>(nodes[current].parent) >= nodes.size())
                return std::nullopt;
            rank[current] = std::max(rank[current], i);
            current = static_cast<size_t>(nodes[current].parent);
        }
        roots[i] = current;
        rank[current] = std::max(rank[current], i);
    }
    std::vector<size_t> units;
    for (size_t i = 0; i < nodes.size(); ++i) {
        if (roots[i] == i)
            units.push_back(i);
    }
    std::ranges::sort(units, [&](size_t a, size_t b) { return rank[a] < rank[b]; });
    std::vector<size_t> result;
    std::function<void(size_t)> append = [&](size_t owner) {
        result.push_back(owner);
        std::vector<size_t> children;
        for (size_t i = 0; i < nodes.size(); ++i) {
            if (nodes[i].parent == static_cast<int>(owner))
                children.push_back(i);
        }
        std::ranges::sort(children, [&](size_t a, size_t b) { return rank[a] < rank[b]; });
        for (const auto child : children)
            append(child);
    };
    for (const auto root : units)
        append(root);
    return result.size() == nodes.size() ? std::optional{result} : std::nullopt;
}
