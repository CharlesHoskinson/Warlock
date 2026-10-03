#include "PointerLocatorState.hpp"
#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace PointerLocator;

// A process-local driver for the actual staged C++ helper. No compositor/DBus.
int main() {
    State state;
    std::string line;
    while (std::getline(std::cin,line)) {
        std::istringstream in(line);
        char op; in >> op;
        if (op=='I') {state=State{};continue;}
        std::string owner;
        long long epoch;
        Point point{},origin{};
        bool replied=false;
        std::optional<Point> local;
        std::vector<Notification> sent;
        if (op=='C') {in>>owner>>epoch;state.claim(owner,static_cast<std::uint64_t>(epoch));}
        else if (op=='D') {in>>owner>>epoch;state.disconnect(owner,static_cast<std::uint64_t>(epoch));}
        else if (op=='Q') {
            in>>owner>>epoch>>point.x>>point.y>>origin.x>>origin.y;
            replied=state.replySent(owner,static_cast<std::uint64_t>(epoch),point);
            if (replied) local=relative(point,origin);
        } else if (op=='M') {in>>point.x>>point.y;sent=state.motion(point);}
        else if (op=='R') state.retire();
        else if (op!='N') return 2;
        if (!in) return 3;
        std::sort(sent.begin(),sent.end(),[](const auto& a,const auto& b){return a.sender<b.sender;});
        std::cout<<state.pendingCount()<<' '<<replied<<' ';
        if (local) std::cout<<local->x<<' '<<local->y;
        else std::cout<<"- -";
        for (const auto& notification:sent) std::cout<<' '<<notification.sender<<':'<<notification.epoch;
        std::cout<<'\n';
    }
}
