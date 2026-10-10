#pragma once
#include "desktop/DesktopTypes.hpp"
#include <array>
#include <cstdint>
#include <optional>
#include <string>
#include <vector>

class CWLSurfaceResource;
namespace Desktop::View { class CPopup; }

namespace Render::CommittedScene {
// Private native ABI. Rebuild the owning renderer, hit tester and authority
// together. Existing Window/Monitor/Seat layouts and public headers stay fixed.
struct Snapshot {
    PHLMONITORREF monitor;
    uint64_t revision=0;
    std::vector<PHLWINDOWREF> order;
    std::vector<WP<CWLSurfaceResource>> surfaces;
    std::vector<WP<Desktop::View::CPopup>> popups;
    std::string structuralFacts; // internal exact equality; never export addresses
};
struct Input {
    bool required=false, ready=false;
    uint64_t revision=0;
    std::vector<PHLWINDOW> order;
};
struct Observation { Snapshot snapshot; bool ready=false; };
struct Hit {
    uint64_t sequence=0, revision=0;
    PHLMONITORREF monitor;
    PHLWINDOWREF recipient;
    std::array<double,2> point{};
    uint16_t properties=0;
    bool ready=false;
};
void begin(const PHLMONITOR& monitor) noexcept;
std::optional<std::vector<PHLWINDOW>> paintOrder(const PHLMONITOR& monitor);
void finish(const PHLMONITOR& monitor, bool outputCommitted) noexcept;
Input inputOrder(const PHLMONITOR& monitor) noexcept;
bool hit(const PHLMONITOR& monitor, const Input& input, const PHLWINDOW& recipient,
         const std::array<double,2>& point, uint16_t properties) noexcept;
std::vector<Observation> observations();
std::vector<Hit> hits();
}
