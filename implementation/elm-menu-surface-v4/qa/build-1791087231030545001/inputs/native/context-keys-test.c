#define CONTEXT_KEYS_PRIMITIVES_ONLY
#include "context-keys.h"
#include <assert.h>
#include <stdio.h>

#define CHECK(name,condition) do {assert(condition);puts(name);checks++;} while (0)
int main(void) {
    unsigned checks=0;
    ContextKeySource bar={0},popup={0};
    ContextKeySignature shift={.type=1,.time=55126914,.hardware=50,.keyval=65505,.window=1,.device=2};
    ContextKeySignature f10=shift;f10.hardware=76;f10.keyval=65479;f10.state=1;
    CHECK("first Shift admitted",context_keys_admit(&bar,&shift));
    CHECK("same-ms distinct F10 admitted",context_keys_admit(&bar,&f10));
    CHECK("WebKit replayed Shift rejected",!context_keys_admit(&bar,&shift));
    CHECK("WebKit replayed F10 rejected",!context_keys_admit(&bar,&f10));
    CHECK("popup has independent source watermark",context_keys_admit(&popup,&shift));
    ContextKeySignature repeat=f10;repeat.time++;
    CHECK("actual newer repeat admitted before held guard",context_keys_admit(&bar,&repeat));
    unsigned held=1;
    CHECK("held guard separately denies admitted repeat",held!=0);
    ContextKeySignature oldrelease=f10;oldrelease.type=2;
    CHECK("old release cannot clear held key",!context_keys_admit(&bar,&oldrelease));
    ContextKeySignature release=repeat;release.type=2;
    CHECK("current equal-ms release distinct from press",context_keys_admit(&bar,&release));
    CHECK("duplicate release rejected",!context_keys_admit(&bar,&release));
    ContextKeySignature distinct=release;distinct.group++;
    CHECK("group contributes signature",context_keys_admit(&bar,&distinct));
    distinct=release;distinct.window++;
    CHECK("window contributes signature",context_keys_admit(&bar,&distinct));
    distinct=release;distinct.device++;
    CHECK("device contributes signature",context_keys_admit(&bar,&distinct));
    ContextKeySource wrapped={0};distinct=shift;distinct.time=UINT32_MAX;
    CHECK("pre-wrap timestamp admitted",context_keys_admit(&wrapped,&distinct));
    distinct.time=0;
    CHECK("forward wrap admitted",context_keys_admit(&wrapped,&distinct));
    distinct.time=UINT32_MAX;
    CHECK("pre-wrap replay after wrap rejected",!context_keys_admit(&wrapped,&distinct));
    distinct.time=UINT32_C(0x80000000);
    CHECK("ambiguous half-range fails closed",!context_keys_admit(&wrapped,&distinct));
    ContextKeySource bounded={0};distinct=shift;
    for (unsigned i=0;i<CONTEXT_KEY_SIGNATURE_LIMIT;i++) {
        distinct.hardware=i;assert(context_keys_admit(&bounded,&distinct));
    }
    CHECK("equal-time signature capacity retained",bounded.count==CONTEXT_KEY_SIGNATURE_LIMIT);
    distinct.hardware=CONTEXT_KEY_SIGNATURE_LIMIT;
    CHECK("overflow timestamp fails closed",!context_keys_admit(&bounded,&distinct));
    distinct.hardware=0;
    CHECK("overflow did not evict oldest signature",!context_keys_admit(&bounded,&distinct));
    distinct.time++;
    CHECK("newer timestamp restores bounded admission",context_keys_admit(&bounded,&distinct) && bounded.count==1);
    printf("context-key checks: %u\n",checks);
    return 0;
}
