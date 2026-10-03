#pragma once
#include <xkbcommon/xkbcommon.h>
#include <cstdint>
#include "key_policy.hpp"

namespace KeyboardMonitor {
// Modifier indices belong to a keymap. Preserve meaning through names rather
// than copying bit positions into a different map; removed names drop out.
inline uint32_t remapModifiers(xkb_keymap* before,xkb_keymap* after,uint32_t mask) {
    uint32_t next=0;
    for(xkb_mod_index_t i=0;i<xkb_keymap_num_mods(before)&&i<32;++i) {
        if(!(mask&(uint32_t(1)<<i)))continue;
        const char* name=xkb_keymap_mod_get_name(before,i);
        const auto target=name?xkb_keymap_mod_get_index(after,name):XKB_MOD_INVALID;
        if(target!=XKB_MOD_INVALID&&target<32)next|=uint32_t(1)<<target;
    }
    return next;
}
inline uint32_t keyLockBits(xkb_keymap* map,uint32_t key,uint32_t group=0) {
    auto* probe=xkb_state_new(map);if(!probe)return 0;
    xkb_state_update_mask(probe,0,0,0,0,0,group);xkb_state_update_key(probe,key+8,XKB_KEY_DOWN);
    auto bits=xkb_state_serialize_mods(probe,XKB_STATE_MODS_LOCKED);
    xkb_state_update_key(probe,key+8,XKB_KEY_UP);bits|=xkb_state_serialize_mods(probe,XKB_STATE_MODS_LOCKED);
    xkb_state_unref(probe);return bits;
}
struct ObserverPacket { uint32_t sym=0,state=0,unicode=0; };
// Exact source convention: prepare before either accepted or captured key
// state changes. KWin and Mutter both serialize their packet before updating
// the normal XKB state. This function is shared by the plugin and replay.
inline ObserverPacket packetBeforeKey(xkb_state* lookup,xkb_state* captured,Mask accepted,uint32_t evdev,uint32_t capturedLockBits=0) {
    // Locking custom keys have a depressed contribution too. Withholding their
    // toggle but retaining that contribution would still uppercase Caps+h.
    const auto depressed=accepted.depressed|(xkb_state_serialize_mods(captured,XKB_STATE_MODS_DEPRESSED)&~capturedLockBits);
    xkb_state_update_mask(lookup,depressed,accepted.latched,accepted.locked,0,0,accepted.group);
    const auto sym=xkb_state_key_get_one_sym(lookup,evdev+8);
    return {sym,xkb_state_serialize_mods(lookup,XKB_STATE_MODS_EFFECTIVE),xkb_keysym_to_utf32(sym)};
}
}
