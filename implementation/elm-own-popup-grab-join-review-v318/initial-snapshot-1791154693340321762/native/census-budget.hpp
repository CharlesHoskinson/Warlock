#pragma once
#include <cstddef>
#include <cstdint>
#include <set>
#include <utility>

struct CensusRefused {};
class CensusBudget {
    std::set<std::pair<uintptr_t, uint32_t>> seen;
    size_t memberCount = 0;
  public:
    void visit(uintptr_t client, uint32_t id, bool accepted) {
        if (!client || !id || seen.size() >= 4096 || !seen.emplace(client, id).second)
            throw CensusRefused{};
        if (accepted && ++memberCount > 256) throw CensusRefused{};
    }
    void output(size_t bytes) const {
        if (bytes > 60000) throw CensusRefused{};
    }
    size_t surfaces() const { return seen.size(); }
    size_t members() const { return memberCount; }
};
