#pragma once
#include <cmath>
#include <cstdint>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

namespace PointerLocator {
struct Point {
    double x, y;
    bool valid() const { return std::isfinite(x) && std::isfinite(y); }
    bool operator==(const Point&) const = default;
};
inline std::optional<Point> relative(Point pointer, Point clientOrigin) {
    if (!pointer.valid() || !clientOrigin.valid()) return std::nullopt;
    Point result{pointer.x-clientOrigin.x, pointer.y-clientOrigin.y};
    return result.valid() ? std::optional{result} : std::nullopt;
}
struct Notification { std::string sender; std::uint64_t epoch; };

// The native bridge supplies an already authenticated unique bus owner and
// compositor-session epoch. This class never infers authority from a string.
// replySent is called only AFTER an authorized method reply/error is sent.
class State {
    struct Pending { std::uint64_t epoch; Point replyPosition; };
    std::unordered_map<std::string,std::uint64_t> m_registered;
    std::unordered_map<std::string,Pending> m_pending;
    bool m_retired=false;
    static constexpr std::size_t MAX_CLIENTS=256;
public:
    bool claim(const std::string& sender, std::uint64_t epoch) {
        if (m_retired || sender.empty() || !epoch) return false;
        auto found=m_registered.find(sender);
        if (found!=m_registered.end()) {
            if (epoch<found->second) return false;
            if (epoch==found->second) return true;
            m_pending.erase(sender);
        } else if (m_registered.size()>=MAX_CLIENTS) return false;
        m_registered.insert_or_assign(sender,epoch);
        return true;
    }
    bool authorized(const std::string& sender, std::uint64_t epoch) const {
        const auto found=m_registered.find(sender);
        return !m_retired && found!=m_registered.end() && found->second==epoch;
    }
    void disconnect(const std::string& sender, std::uint64_t epoch) {
        if (!authorized(sender,epoch)) return;
        m_registered.erase(sender);m_pending.erase(sender);
    }
    bool replySent(const std::string& sender, std::uint64_t epoch, Point pointer) {
        if (!authorized(sender,epoch) || !pointer.valid()) return false;
        m_pending.insert_or_assign(sender,Pending{epoch,pointer});
        return true;
    }
    std::vector<Notification> motion(Point pointer) {
        std::vector<Notification> result;
        if (m_retired || !pointer.valid()) return result;
        for (auto it=m_pending.begin();it!=m_pending.end();) {
            if (pointer==it->second.replyPosition) {++it;continue;}
            if (authorized(it->first,it->second.epoch))
                result.push_back({it->first,it->second.epoch});
            it=m_pending.erase(it);
        }
        return result;
    }
    void retire() {m_retired=true;m_registered.clear();m_pending.clear();}
    std::size_t pendingCount() const {return m_pending.size();}
};
}
