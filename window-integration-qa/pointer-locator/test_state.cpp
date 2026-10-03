#include "PointerLocatorState.hpp"
#include <cassert>
#include <iostream>
#include <limits>
using namespace PointerLocator;
int main() {
    State state;
    assert(!state.replySent(":1.1",1,{0,0}));
    assert(state.claim(":1.1",1));
    assert(state.motion({1,1}).empty());
    assert(state.replySent(":1.1",1,{1,1}));
    assert(state.replySent(":1.1",1,{1,1}));
    assert(state.pendingCount()==1 && state.motion({1,1}).empty());
    auto moved=state.motion({1.25,1});
    assert(moved.size()==1 && moved[0].sender==":1.1" && moved[0].epoch==1);
    assert(state.motion({2,2}).empty());
    assert(state.replySent(":1.1",1,{2,2}));
    assert(state.claim(":1.1",2) && state.pendingCount()==0);
    assert(!state.replySent(":1.1",1,{2,2}));
    assert(state.replySent(":1.1",2,{2,2}));
    state.disconnect(":1.1",1);
    assert(state.authorized(":1.1",2));
    assert(state.claim(":1.2",1));
    assert(state.replySent(":1.2",1,{2,2}));
    state.disconnect(":1.1",2);
    moved=state.motion({3,3});
    assert(moved.size()==1 && moved[0].sender==":1.2");
    assert(state.replySent(":1.2",1,{3,3}));
    assert(state.motion({std::numeric_limits<double>::quiet_NaN(),3}).empty());
    assert(state.pendingCount()==1);
    state.retire();
    assert(!state.claim(":1.3",1) && !state.replySent(":1.2",1,{3,3}));
    assert(state.pendingCount()==0 && state.motion({4,4}).empty());
    const auto local=relative({-32.25,11.5},{-40.5,20.25});
    assert(local && *local==(Point{8.25,-8.75}));
    assert(!relative({std::numeric_limits<double>::infinity(),0},{0,0}));
    std::cout << "Pointer state authority, fractional motion, replacement, disconnect, retirement and signed coordinates PASS\n";
}
