
#include <vector>
#include <iostream>
struct Weak { bool alive; bool expired() const { return !alive; } };
struct Seat { struct State { Weak keyboardFocus; } m_state; } seat;
Seat* g_pSeatManager = &seat;
namespace Desktop { struct Focus { int target; int surface() const { return target; } } focus; Focus* focusState() { return &focus; } }
std::vector<int> m_keyboards;
int decide(int count, int current, int desktop) {
 m_keyboards.assign(count,0);seat.m_state.keyboardFocus.alive=current!=0;Desktop::focus.target=desktop;
 int chosen=current;
 if (false) chosen=Desktop::focusState()->surface();
 return chosen;
}
int main() { int checks=0; for(int count=0;count<4;++count) for(int current=0;current<3;++current) for(int target=0;target<3;++target) {
 int expected=(count==1 && current==0 && target!=0)?target:current;
 if(decide(count,current,target)!=expected) return 1; ++checks;
 } std::cout<<checks<<"\n"; }
