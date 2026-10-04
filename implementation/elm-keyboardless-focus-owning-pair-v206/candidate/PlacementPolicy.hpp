#pragma once
// Private prototype only. The caller supplies the live identity read from native
// authority; this store is neither an identity registry nor mutation permission.
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace Elm::Placement {
class Identity {
    uint64_t lifetime_, incarnation_;
    Identity(uint64_t lifetime, uint64_t incarnation)
        : lifetime_(lifetime), incarnation_(incarnation) {}
public:
    static std::optional<Identity> fromNative(uint64_t lifetime, uint64_t incarnation) {
        if (!lifetime || !incarnation) return std::nullopt;
        return Identity(lifetime, incarnation);
    }
    friend bool operator==(const Identity& a, const Identity& b) {
        return a.lifetime_ == b.lifetime_ && a.incarnation_ == b.incarnation_;
    }
};

class Scope {
    int64_t workspace_;
    uint64_t workspaceGeneration_, output_, outputGeneration_, workAreaRevision_;
    Scope(int64_t workspace, uint64_t workspaceGeneration, uint64_t output, uint64_t outputGeneration, uint64_t workAreaRevision)
        : workspace_(workspace), workspaceGeneration_(workspaceGeneration), output_(output), outputGeneration_(outputGeneration), workAreaRevision_(workAreaRevision) {}
public:
    // Native monitor ID zero is valid; ownership generations must be explicit.
    // Peer/frontend session identity is intentionally absent from placement keys.
    static std::optional<Scope> fromNative(int64_t workspace, uint64_t workspaceGeneration, uint64_t output, uint64_t outputGeneration, uint64_t workAreaRevision) {
        if (!workspace || !workspaceGeneration || !outputGeneration || !workAreaRevision) return std::nullopt;
        return Scope(workspace, workspaceGeneration, output, outputGeneration, workAreaRevision);
    }
    friend bool operator==(const Scope& a, const Scope& b) {
        return a.workspace_ == b.workspace_ && a.workspaceGeneration_ == b.workspaceGeneration_ &&
            a.output_ == b.output_ && a.outputGeneration_ == b.outputGeneration_ && a.workAreaRevision_ == b.workAreaRevision_;
    }
};

struct Rect {
    double x, y, width, height;
    bool valid() const {
        return std::isfinite(x) && std::isfinite(y) && std::isfinite(width) && std::isfinite(height) &&
            width > 0 && height > 0 && std::isfinite(x + width) && std::isfinite(y + height);
    }
    friend bool operator==(const Rect&, const Rect&) = default;
};
struct Original {
    Rect logical, visual;
    friend bool operator==(const Original&, const Original&) = default;
};
enum class Capture { Captured, Duplicate, StaleIdentity, InvalidRect, Capacity };

class Records {
public:
    static constexpr size_t capacity = 256;
private:
    struct Entry { Identity identity; Scope scope; Original original; };
    std::array<std::optional<Entry>, capacity> entries_{};
    size_t size_ = 0;
public:
    size_t size() const { return size_; }
    Capture capture(const Identity& requested, const std::optional<Identity>& owningLiveIdentity, const Scope& scope, const Original& original) {
        if (!owningLiveIdentity || !(requested == *owningLiveIdentity)) return Capture::StaleIdentity;
        for (const auto& entry : entries_) if (entry && entry->identity == requested) return Capture::Duplicate;
        if (!original.logical.valid() || !original.visual.valid()) return Capture::InvalidRect;
        if (size_ == capacity) return Capture::Capacity;
        for (auto& entry : entries_) if (!entry) {
            entry = Entry{requested, scope, original};
            ++size_;
            return Capture::Captured;
        }
        return Capture::Capacity;
    }
    std::optional<Original> read(const Identity& requested, const std::optional<Identity>& owningLiveIdentity, const Scope& scope) const {
        if (!owningLiveIdentity || !(requested == *owningLiveIdentity)) return std::nullopt;
        for (const auto& entry : entries_) if (entry && entry->identity == requested && entry->scope == scope) return entry->original;
        return std::nullopt; // Externally maximized or unknown original: explicit absence.
    }
    bool hasRecord(const Identity& requested, const std::optional<Identity>& owningLiveIdentity) const {
        if(!owningLiveIdentity || !(requested==*owningLiveIdentity)) return false;
        for(const auto& entry:entries_) if(entry && entry->identity==requested) return true;
        return false;
    }
    bool retire(const Identity& identity) {
        for (auto& entry : entries_) if (entry && entry->identity == identity) {
            entry.reset(); --size_; return true;
        }
        return false;
    }
};
}
