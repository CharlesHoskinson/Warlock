#include "key_policy.hpp"
#include "xkb_helpers.hpp"
#include <xkbcommon/xkbcommon.h>
#include <xkbcommon/xkbcommon-keysyms.h>
#include <linux/input-event-codes.h>
#include <iostream>
#include <stdexcept>
#include <memory>
using namespace KeyboardMonitor;
static int checks=0;
static void require(bool ok,const char* label) {
    if(!ok) throw std::runtime_error(label);
    ++checks; std::cout<<"PASS "<<label<<'\n';
}
struct Rig {
    xkb_context* context=xkb_context_new(XKB_CONTEXT_NO_FLAGS);
    xkb_keymap* map=nullptr;
    xkb_state *raw=nullptr,*accepted=nullptr,*lookup=nullptr;
    ObserverPacket lastPacket;
    Policy policy;
    uint64_t now=1000;
    Rig() {
        xkb_rule_names rules{.rules="evdev",.model="pc105",.layout="us",.variant=nullptr,.options=nullptr};
        map=xkb_keymap_new_from_names(context,&rules,XKB_KEYMAP_COMPILE_NO_FLAGS);
        if(!map) throw std::runtime_error("real XKB keymap");
        raw=xkb_state_new(map);accepted=xkb_state_new(map);lookup=xkb_state_new(map);
    }
    ~Rig(){xkb_state_unref(raw);xkb_state_unref(accepted);xkb_state_unref(lookup);xkb_keymap_unref(map);xkb_context_unref(context);}
    uint32_t locks() const{return xkb_state_serialize_mods(accepted,XKB_STATE_MODS_LOCKED);}
    uint32_t mods() const{return xkb_state_serialize_mods(accepted,XKB_STATE_MODS_EFFECTIVE);}
    Result key(uint32_t evdev,bool press,uintptr_t dev=1) {
        auto key=evdev+8;
        uint32_t capturedLocks=0;for(auto held:policy.capturedKeys(dev))capturedLocks|=keyLockBits(map,held);
        lastPacket=packetBeforeKey(lookup,raw,{xkb_state_serialize_mods(accepted,XKB_STATE_MODS_DEPRESSED),xkb_state_serialize_mods(accepted,XKB_STATE_MODS_LATCHED),locks(),xkb_state_serialize_layout(accepted,XKB_STATE_LAYOUT_EFFECTIVE)},evdev,capturedLocks);
        auto sym=lastPacket.sym,state=lastPacket.state;
        const bool known=policy.known(dev,evdev);
        auto result=policy.key(dev,evdev,sym,state,press,now++,300);
        if(press?!known:known) {
            xkb_state_update_key(raw,key,press?XKB_KEY_DOWN:XKB_KEY_UP);
            if(!result.consumed) xkb_state_update_key(accepted,key,press?XKB_KEY_DOWN:XKB_KEY_UP);
        }
        // Observer retains raw held non-locking modifiers and accepted locks.
        xkb_state_update_mask(raw,xkb_state_serialize_mods(raw,XKB_STATE_MODS_DEPRESSED),xkb_state_serialize_mods(raw,XKB_STATE_MODS_LATCHED),locks(),0,0,xkb_state_serialize_layout(accepted,XKB_STATE_LAYOUT_EFFECTIVE));
        return result;
    }
};
int main(){try{
    {Rig r; require(!r.key(KEY_H,true).consumed,"default typing passes");r.key(KEY_H,false);
     r.key(KEY_CAPSLOCK,true);r.key(KEY_CAPSLOCK,false);require(r.locks()!=0,"default Caps toggles");}
    {Rig r;r.policy.clients[":watch"].watch=true;
     require(!r.key(KEY_H,true).consumed,"watch never consumes");r.key(KEY_H,false);
     r.key(KEY_NUMLOCK,true);r.key(KEY_NUMLOCK,false);require(r.locks()!=0,"watch Num toggles");}
    {Rig r;r.policy.clients[":watch"].watch=true;const auto bit=keyLockBits(r.map,KEY_CAPSLOCK);
     r.key(KEY_CAPSLOCK,true);require((r.lastPacket.state&bit)==0,"watch Caps down packet is pre-event unlocked");r.key(KEY_CAPSLOCK,false);
     require((r.lastPacket.state&bit)!=0,"watch Caps first up packet sees prior accepted lock");
     r.key(KEY_CAPSLOCK,true);r.key(KEY_CAPSLOCK,false);
     require((r.lastPacket.state&bit)!=0&&r.locks()==0,"watch Caps unlock up packet carries prior lock while native clears");
     r.key(KEY_H,true);require((r.lastPacket.state&bit)==0&&r.lastPacket.sym==XKB_KEY_h,"next watch packet uses accepted unlocked lookup");r.key(KEY_H,false);}
    {Rig r;r.policy.clients[":watch"].watch=true;const auto bit=keyLockBits(r.map,KEY_NUMLOCK);
     r.key(KEY_NUMLOCK,true);r.key(KEY_NUMLOCK,false);r.key(KEY_NUMLOCK,true);r.key(KEY_NUMLOCK,false);
     require((r.lastPacket.state&bit)!=0&&r.locks()==0,"watch Num unlock release packet is consistently pre-event");
     r.key(KEY_H,true);require((r.lastPacket.state&bit)==0,"next watch packet reflects accepted unlocked Num");r.key(KEY_H,false);}
    {Rig r;r.policy.clients[":reader"].full=true;
     r.key(KEY_LEFTSHIFT,true);require(r.lastPacket.state==0,"captured Shift down packet precedes raw modifier change");
     r.key(KEY_H,true);require(r.lastPacket.sym==XKB_KEY_H&&(r.lastPacket.state&1),"captured H down lookup sees raw held Shift");
     r.key(KEY_H,false);require(r.lastPacket.sym==XKB_KEY_H&&(r.lastPacket.state&1),"captured H up retains pre-event Shift mask");
     r.key(KEY_LEFTSHIFT,false);require((r.lastPacket.state&1)&&r.mods()==0,"captured Shift up packet includes raw pre-release Shift only");
     r.policy.stop();r.key(KEY_H,true);require(r.lastPacket.sym==XKB_KEY_h&&r.lastPacket.state==0,"later lookup clears released raw Shift");r.key(KEY_H,false);}
    {Rig r;r.policy.clients[":reader"].modifiers.insert(XKB_KEY_Caps_Lock);
     r.key(KEY_CAPSLOCK,true);require(r.lastPacket.sym==XKB_KEY_Caps_Lock&&r.lastPacket.state==0,"custom Caps packet uses accepted pre-event unlocked lookup");
     r.key(KEY_H,true);require(r.lastPacket.sym==XKB_KEY_h&&r.lastPacket.state==0&&r.locks()==0,"custom Caps chord retains native unlocked state");
     r.key(KEY_H,false);r.key(KEY_CAPSLOCK,false);require(r.lastPacket.sym==XKB_KEY_Caps_Lock&&r.lastPacket.state==0,"custom Caps release uses same accepted lookup convention");}
    {Rig r;r.policy.clients[":reader"].modifiers.insert(XKB_KEY_Insert);
     r.key(KEY_INSERT,true);require(r.lastPacket.sym==XKB_KEY_Insert&&r.lastPacket.state==0,"custom Insert down packet is pre-event");
     require(r.key(KEY_H,true).consumed&&r.lastPacket.sym==XKB_KEY_h&&r.lastPacket.state==0,"custom Insert H packet captured with matching lookup state");
     r.key(KEY_INSERT,false);require(r.lastPacket.sym==XKB_KEY_Insert&&r.lastPacket.state==0,"custom Insert release preserves lookup identity");
     require(r.key(KEY_H,false).consumed,"Insert H release stays captured after modifier release");}
    {Rig r;r.policy.clients[":reader"].modifiers.insert(XKB_KEY_Caps_Lock);
     require(r.key(KEY_CAPSLOCK,true).consumed,"first custom Caps captured before XKB");r.key(KEY_CAPSLOCK,false);
     require(r.locks()==0,"captured Caps has no accepted lock");
     require(!r.key(KEY_CAPSLOCK,true).consumed,"second standalone Caps passes");r.key(KEY_CAPSLOCK,false);
     require(r.locks()!=0,"second Caps toggles accepted lock exactly once");}
    {Rig r;r.policy.clients[":reader"].modifiers.insert(XKB_KEY_Caps_Lock);
     r.key(KEY_CAPSLOCK,true);require(r.key(KEY_H,true).consumed,"custom Caps chord captures real H key");
     r.key(KEY_CAPSLOCK,false);require(r.key(KEY_H,false).consumed,"chord release remains captured after modifier release");
     require(r.key(KEY_CAPSLOCK,true).consumed,"chord disarms double tap");r.key(KEY_CAPSLOCK,false);require(r.locks()==0,"chord never toggles Caps");}
    {Rig r;r.policy.clients[":reader"].full=true;
     r.key(KEY_LEFTSHIFT,true);require(r.mods()==0,"full grab blocks accepted Shift modifier");
     auto h=r.key(KEY_H,true);require(h.consumed&&h.sym==XKB_KEY_H,"raw observer retains Shift while native state suppressed");
     r.policy.drop(":reader");require(!r.policy.quiescent(),"disconnect retains captured route tombstones");
     require(r.key(KEY_H,false).consumed&&r.key(KEY_LEFTSHIFT,false).consumed,"disconnect releases suppressed without native orphan");
     require(r.policy.quiescent()&&!r.key(KEY_H,true).consumed,"later typing passes after disconnect");r.key(KEY_H,false);}
    {Rig r;r.policy.clients[":reader"].full=true;r.key(KEY_LEFTSHIFT,true);r.key(KEY_LEFTSHIFT,true);r.key(KEY_LEFTSHIFT,false);
     r.policy.stop();auto h=r.key(KEY_H,true);
     require(h.sym==XKB_KEY_h&&!h.consumed,"captured repeats do not leave raw Shift stuck");r.key(KEY_H,false);}
    {Rig r;r.key(KEY_H,true);r.policy.clients[":reader"].full=true;
     require(!r.key(KEY_H,false).consumed,"preexisting accepted press retains real release under new grab");
     require(r.policy.quiescent(),"accepted held keys do not obstruct suppression quiescence");}
    {Rig r;r.policy.clients[":reader"].modifiers.insert(XKB_KEY_Caps_Lock);
     r.key(KEY_CAPSLOCK,true);r.key(KEY_CAPSLOCK,false);r.policy.resetTaps();
     require(r.key(KEY_CAPSLOCK,true).consumed,"grab mutation resets native policy tap state");r.key(KEY_CAPSLOCK,false);}
    {Rig r;r.policy.clients[":reader"].modifiers.insert(XKB_KEY_Caps_Lock);
     r.key(KEY_CAPSLOCK,true);r.key(KEY_CAPSLOCK,false);r.key(KEY_H,true);r.key(KEY_H,false);
     require(r.key(KEY_CAPSLOCK,true).consumed&&r.locks()==0,"Caps H Caps is not a consecutive standalone double tap");r.key(KEY_CAPSLOCK,false);}
    {Rig r;r.policy.clients[":reader"].full=true;r.key(KEY_H,true,1);r.policy.stop();
     require(!r.key(KEY_H,true,2).consumed,"release tombstones are device scoped");
     require(r.key(KEY_H,false,1).consumed&&!r.key(KEY_H,false,2).consumed,"same key on two devices retains independent routes");}
    {Policy p;p.clients[":reader"].watch=true;p.clients[":reader"].full=true;
     auto press=p.key(1,KEY_H,XKB_KEY_h,0,true,1,300);require(press.consumed,"permission fixture starts captured");
     auto release=p.key(1,KEY_H,XKB_KEY_H,0,false,2,300,false,false);
     require(release.consumed&&release.recipients.empty()&&p.quiescent(),"revoked permission release silent and suppressed");
     auto denied=p.key(1,KEY_J,XKB_KEY_j,0,true,3,300,false,false);
     require(!denied.consumed&&denied.recipients.empty(),"fresh revoked packet passes without observation");}
    {Policy p;p.clients[":reader"].full=true;p.key(1,KEY_H,XKB_KEY_h,0,true,1,300);
     p.resetTaps();auto release=p.key(1,KEY_H,XKB_KEY_H,1,false,2,300);
     require(release.consumed&&release.sym==XKB_KEY_h,"keymap change retains captured original keysym and release");
     p.key(1,KEY_H,XKB_KEY_h,0,true,3,300);p.removeDevice(1);p.stop();
     require(p.quiescent()&&!p.key(1,KEY_H,XKB_KEY_h,0,true,4,300).consumed,"removed device cannot leak tombstone into reused identity");}
    {Policy p;p.clients[":reader"].modifiers.insert(XKB_KEY_Caps_Lock);p.clients[":second"].strokes.insert({XKB_KEY_Caps_Lock,0});
     p.key(1,KEY_CAPSLOCK,XKB_KEY_Caps_Lock,0,true,1,300);p.key(1,KEY_CAPSLOCK,XKB_KEY_Caps_Lock,0,false,2,300);
     require(p.key(1,KEY_CAPSLOCK,XKB_KEY_Caps_Lock,0,true,3,300).consumed,"other client's exact stroke cannot be bypassed by custom double tap");}
    {VirtualMaskGuard v;Mask accepted{},raw{0,0,2,0};
     auto filtered=v.filter(raw,accepted,0,2,false);
     require(filtered.locked==0&&v.parity()==2,"explicit captured virtual Caps packet suppressed");
     filtered=v.filter(raw,filtered,0,0,false);require(filtered.locked==0,"virtual lock correction survives grab end");
     raw.locked=0;filtered=v.filter(raw,filtered,0,0,false);require(filtered.locked==2,"next ordinary virtual Caps toggle preserved");
     raw.depressed=1;raw.latched=4;raw.group=1;filtered=v.filter(raw,filtered,1,0,false);
     require(filtered.depressed==0&&filtered.latched==4&&filtered.group==1,"captured depressed modifier filtered while latched/layout preserved");}
    {Rig r;VirtualMaskGuard v;Mask accepted{};
     xkb_state_update_key(r.raw,KEY_NUMLOCK+8,XKB_KEY_DOWN);
     Mask raw{0,0,xkb_state_serialize_mods(r.raw,XKB_STATE_MODS_LOCKED),0};
     require(raw.locked!=0,"real XKB generates Num lock virtual mask");
     accepted=v.filter(raw,accepted,0,0,true);require(accepted.locked==0,"full virtual grab freezes real Num toggle");
     xkb_state_update_key(r.raw,KEY_NUMLOCK+8,XKB_KEY_UP);
     raw.locked=xkb_state_serialize_mods(r.raw,XKB_STATE_MODS_LOCKED);
     accepted=v.filter(raw,accepted,0,0,false);require(accepted.locked==0,"real virtual Num correction retained after ungrab");
     xkb_state_update_key(r.raw,KEY_NUMLOCK+8,XKB_KEY_DOWN);
     raw.locked=xkb_state_serialize_mods(r.raw,XKB_STATE_MODS_LOCKED);
     xkb_state_update_key(r.accepted,KEY_NUMLOCK+8,XKB_KEY_DOWN);
     const auto expected=xkb_state_serialize_mods(r.accepted,XKB_STATE_MODS_LOCKED);
     accepted=v.filter(raw,accepted,0,16,false,expected);
     require(accepted.locked==expected&&expected!=0,"accepted XKB shadow fixes next Num down timing");
     xkb_state_update_key(r.raw,KEY_NUMLOCK+8,XKB_KEY_UP);xkb_state_update_key(r.accepted,KEY_NUMLOCK+8,XKB_KEY_UP);
     raw.locked=xkb_state_serialize_mods(r.raw,XKB_STATE_MODS_LOCKED);
     accepted=v.filter(raw,accepted,0,16,false,xkb_state_serialize_mods(r.accepted,XKB_STATE_MODS_LOCKED));
     require(accepted.locked!=0,"corrected virtual Num release retains accepted lock");}
    {Rig r;VirtualMaskGuard v;Mask accepted{};const auto bit=keyLockBits(r.map,KEY_CAPSLOCK);
     require(bit!=0&&keyLockBits(r.map,KEY_H)==0,"actual keymap distinguishes locking Caps from ordinary H");
     for(int cycle=0;cycle<4;++cycle)for(bool press:{true,false}) {
       xkb_state_update_key(r.raw,KEY_CAPSLOCK+8,press?XKB_KEY_DOWN:XKB_KEY_UP);
       if(cycle)xkb_state_update_key(r.accepted,KEY_CAPSLOCK+8,press?XKB_KEY_DOWN:XKB_KEY_UP);
       const auto raw=xkb_state_serialize_mods(r.raw,XKB_STATE_MODS_LOCKED);
       const auto expected=xkb_state_serialize_mods(r.accepted,XKB_STATE_MODS_LOCKED);
       accepted=v.filter({0,0,raw,0},accepted,0,bit,false,expected);
       require(accepted.locked==expected,"repeated virtual Caps cycles match accepted XKB on each down and up");
     }}
    {Rig r;VirtualMaskGuard v;Mask accepted{};
     v.filter({0,0,2,0},accepted,0,2,false);require(v.parity()==2,"keymap fixture begins with suppressed raw Caps offset");
     xkb_rule_names rules{.rules="evdev",.model="pc105",.layout="de",.variant=nullptr,.options=nullptr};
     auto* next=xkb_keymap_new_from_names(r.context,&rules,XKB_KEYMAP_COMPILE_NO_FLAGS);if(!next)throw std::runtime_error("German XKB map");
     const auto remapped=remapModifiers(r.map,next,v.parity());v.remapCorrection(remapped);
     const auto baselineMask=remapModifiers(r.map,next,2);
     auto filtered=v.filter({0,0,0,0},accepted,0,baselineMask,false,0);
     require(filtered.locked==0&&v.parity()==0,"new-map modifier-only packet establishes accepted off baseline");
     const auto acceptedOn=remapModifiers(r.map,next,2);
     filtered=v.filter({0,0,0,0},accepted,0,baselineMask,false,acceptedOn);
     require(filtered.locked==acceptedOn,"new-map explicit zero preserves remapped accepted Caps on baseline");
     require(remapModifiers(r.map,next,1u<<31)==0,"unrecognized modifier index cannot leak into replacement map");
     xkb_keymap_unref(next);}
    std::cout<<"SUMMARY checks="<<checks<<" nativeCompositorInput=false\n";
    return 0;
}catch(const std::exception& e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
