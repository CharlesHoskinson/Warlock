#include "PlacementPolicy.hpp"
#include <functional>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
using namespace Elm::Placement;
static void require(bool value, const char* message) { if (!value) throw std::runtime_error(message); }
static Identity id(uint64_t incarnation, uint64_t lifetime = 7) { return Identity::fromNative(lifetime, incarnation).value(); }
static Scope scope(int64_t workspace = 3, uint64_t workspaceGeneration = 5, uint64_t output = 0, uint64_t outputGeneration = 9) {
    return Scope::fromNative(workspace, workspaceGeneration, output, outputGeneration).value();
}
static Original first() { return {{-40, 30, 640, 480}, {-50, 20, 660, 500}}; }
static Original changed() { return {{0, 0, 1920, 1080}, {-5, -5, 1930, 1090}}; }
static void captured(Records& records, Identity target = id(10)) {
    require(records.capture(target, target, scope(), first()) == Capture::Captured, "valid capture refused");
}
int main() {
    std::vector<std::pair<std::string, std::function<void()>>> tests = {
        {"positive-full-position-size-logical-and-visual", [] {
            Records records; captured(records);
            require(records.read(id(10), id(10), scope()) == first(), "complete original not retained");
        }},
        {"unknown-external-maximized-has-no-invented-original", [] {
            Records records; require(!records.read(id(10), id(10), scope()), "missing original invented");
        }},
        {"opaque-native-identity-positive-and-invalid-zero", [] {
            require(!Identity::fromNative(0, 10) && !Identity::fromNative(7, 0), "zero identity admitted");
            require(Identity::fromNative(7, 10).has_value(), "valid identity refused");
        }},
        {"native-output-zero-and-negative-workspace-supported", [] {
            auto native = Scope::fromNative(-4, 2, 0, 3); require(native.has_value(), "valid native scope refused");
            Records records; require(records.capture(id(10), id(10), *native, first()) == Capture::Captured, "valid scope refused");
            require(records.read(id(10), id(10), *native) == first(), "native output zero not retained");
        }},
        {"unknown-scope-generations-and-workspace-refused", [] {
            require(!Scope::fromNative(0, 1, 0, 1), "workspace zero admitted");
            require(!Scope::fromNative(1, 0, 0, 1), "workspace generation zero admitted");
            require(!Scope::fromNative(1, 1, 0, 0), "output generation zero admitted");
        }},
        {"duplicate-preserves-first-original", [] {
            Records records; captured(records);
            require(records.capture(id(10), id(10), scope(), changed()) == Capture::Duplicate, "duplicate capture accepted");
            require(records.size() == 1 && records.read(id(10), id(10), scope()) == first(), "duplicate overwrote original");
        }},
        {"duplicate-fresh-scope-does-not-rebind-original", [] {
            Records records; captured(records);
            require(records.capture(id(10), id(10), scope(4), changed()) == Capture::Duplicate, "duplicate rebound");
            require(records.read(id(10), id(10), scope()) == first() && !records.read(id(10), id(10), scope(4)), "captured scope changed");
        }},
        {"replacement-incarnation-cannot-read", [] {
            Records records; captured(records);
            require(!records.read(id(11), id(11), scope()), "replacement inherited original");
            require(!records.read(id(10), id(11), scope()), "stale request used live replacement");
        }},
        {"authority-lifetime-change-cannot-read", [] {
            Records records; captured(records);
            require(!records.read(id(10, 8), id(10, 8), scope()), "new lifetime inherited original");
            require(!records.read(id(10), id(10, 8), scope()), "old lifetime request admitted");
        }},
        {"capture-requires-exact-current-native-identity", [] {
            Records records;
            require(records.capture(id(10), id(11), scope(), first()) == Capture::StaleIdentity, "stale capture admitted");
            require(records.capture(id(10), id(10, 8), scope(), first()) == Capture::StaleIdentity, "stale lifetime capture admitted");
            require(records.size() == 0, "stale capture mutated records");
        }},
        {"retired-native-absence-refuses-capture-and-read", [] {
            Records records; captured(records);
            require(records.capture(id(10), std::nullopt, scope(), changed()) == Capture::StaleIdentity, "absent live target admitted");
            require(!records.read(id(10), std::nullopt, scope()), "retired native target read");
            require(records.read(id(10), id(10), scope()) == first(), "failed stale access altered original");
        }},
        {"workspace-id-compatibility", [] {
            Records records; captured(records); require(!records.read(id(10), id(10), scope(4)), "workspace mismatch admitted");
        }},
        {"workspace-generation-compatibility", [] {
            Records records; captured(records); require(!records.read(id(10), id(10), scope(3, 6)), "workspace reuse admitted");
        }},
        {"output-id-compatibility", [] {
            Records records; captured(records); require(!records.read(id(10), id(10), scope(3, 5, 1)), "output mismatch admitted");
        }},
        {"output-generation-compatibility", [] {
            Records records; captured(records); require(!records.read(id(10), id(10), scope(3, 5, 0, 10)), "output reuse admitted");
        }},
        {"invalid-logical-rect-refused-without-record", [] {
            for (Rect rect : {Rect{0,0,0,1}, Rect{0,0,1,-1}, Rect{std::numeric_limits<double>::quiet_NaN(),0,1,1},
                    Rect{0,0,std::numeric_limits<double>::infinity(),1}, Rect{std::numeric_limits<double>::max(),0,std::numeric_limits<double>::max(),1}}) {
                Records records; Original original = first(); original.logical = rect;
                require(records.capture(id(10), id(10), scope(), original) == Capture::InvalidRect, "invalid logical geometry captured");
                require(records.size() == 0 && !records.read(id(10), id(10), scope()), "invalid record retained");
            }
        }},
        {"invalid-visual-rect-independently-refused", [] {
            Records records; Original original = first(); original.visual.height = 0;
            require(records.capture(id(10), id(10), scope(), original) == Capture::InvalidRect, "invalid visual geometry admitted");
            require(records.size() == 0, "invalid visual record retained");
        }},
        {"capacity-256-refuses-257-no-eviction", [] {
            Records records;
            for (uint64_t n = 1; n <= 256; ++n) captured(records, id(n));
            require(records.size() == 256, "capacity is not 256");
            require(records.capture(id(257), id(257), scope(), changed()) == Capture::Capacity, "capacity overflow admitted");
            for (uint64_t n = 1; n <= 256; ++n) require(records.read(id(n), id(n), scope()) == first(), "capacity evicted old record");
            require(!records.read(id(257), id(257), scope()), "overflow record retained");
        }},
        {"duplicate-at-capacity-preserves-first", [] {
            Records records; for (uint64_t n = 1; n <= 256; ++n) captured(records, id(n));
            require(records.capture(id(1), id(1), scope(), changed()) == Capture::Duplicate, "duplicate at capacity incorrectly handled");
            require(records.read(id(1), id(1), scope()) == first() && records.size() == 256, "duplicate at capacity altered store");
        }},
        {"retirement-exact-id-preserves-unrelated-record", [] {
            Records records; captured(records); captured(records, id(11));
            require(!records.retire(id(10, 8)), "wrong lifetime retired original");
            require(records.retire(id(10)) && !records.retire(id(10)), "retirement not exact/idempotent");
            require(!records.read(id(10), id(10), scope()) && records.read(id(11), id(11), scope()) == first() && records.size() == 1, "retirement damaged peer");
        }},
        {"retirement-frees-one-slot-for-new-incarnation", [] {
            Records records; for (uint64_t n = 1; n <= 256; ++n) captured(records, id(n));
            require(records.retire(id(100)), "retirement failed");
            require(records.capture(id(257), id(257), scope(), changed()) == Capture::Captured, "retired slot not reusable");
            require(records.size() == 256 && !records.read(id(100), id(100), scope()) && records.read(id(257), id(257), scope()) == changed(), "reuse mixed originals");
        }},
    };
    unsigned passed = 0;
    for (const auto& [name, test] : tests) {
        try { test(); ++passed; std::cout << "PASS " << name << '\n'; }
        catch (const std::exception& error) { std::cout << "FAIL " << name << ": " << error.what() << '\n'; return 1; }
    }
    std::cout << "CHECKS " << passed << '\n';
    return 0;
}
