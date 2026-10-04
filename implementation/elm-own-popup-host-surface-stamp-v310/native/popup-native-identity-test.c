#include "popup-native-identity.h"
#include <unistd.h>
#include <stdio.h>
#define CHECK(x) do {g_assert_true(x);++checks;} while(0)
int main(void) {
    guint checks=0;guint64 start=0;g_autofree char *actual=NULL;
    CHECK(g_file_get_contents("/proc/self/stat",&actual,NULL,NULL));
    CHECK(popup_start_parse(actual,&start));CHECK(start>0);
    /* comm can contain whitespace and closing parentheses; field22 stays exact. */
    CHECK(popup_start_parse("1 (odd ) name)) R 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 42 0",&start));CHECK(start==42);
    CHECK(!popup_start_parse("1 (name) R 1",&start));
    CHECK(!popup_start_parse("1 (name) R 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 0 0",&start));
    CHECK(!popup_start_parse("1 (name) R 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 18446744073709551616 0",&start));
    CHECK(!popup_start_parse("1 (name) R 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 04 0",&start));
    PopupNativeIdentity s={.pid=getpid(),.start=start,.view=1,.generation=1,.topology=1,.publication=2,.lease=1,
        .popup=10,.root=11,.active=TRUE,.mapped=TRUE,.root_mapped=TRUE,.same_display=TRUE,.ready=TRUE,.current_owner=TRUE};
    CHECK(popup_identity_valid(&s));
    CHECK(popup_identity_same(&s,&s));
    for(guint i=0;i<15;i++) {
        PopupNativeIdentity bad=s;
        switch(i) {
            case 0:bad.pid=0;break;case 1:bad.start=0;break;case 2:bad.view=0;break;
            case 3:bad.generation=0;break;case 4:bad.topology=0;break;case 5:bad.publication=0;break;
            case 6:bad.lease=0;break;case 7:bad.popup=0;break;case 8:bad.root=bad.popup;break;
            case 9:bad.active=FALSE;break;case 10:bad.mapped=FALSE;break;case 11:bad.root_mapped=FALSE;break;
            case 12:bad.same_display=FALSE;break;case 13:bad.ready=FALSE;break;case 14:bad.current_owner=FALSE;break;
        }
        CHECK(!popup_identity_valid(&bad));
        CHECK(!popup_identity_same(&s,&bad));
    }
    for(guint i=0;i<9;i++) {
        PopupNativeIdentity changed=s;
        switch(i) {
            case 0:changed.pid++;break;case 1:changed.start++;break;case 2:changed.view++;break;
            case 3:changed.generation++;break;case 4:changed.topology++;break;case 5:changed.publication++;break;
            case 6:changed.lease++;break;case 7:changed.popup=12;break;case 8:changed.root=12;break;
        }
        CHECK(popup_identity_valid(&changed));CHECK(!popup_identity_same(&s,&changed));
    }
    CHECK(!popup_identity_valid(NULL));
    printf("identity checks:%u; actual kernel start parser; no GUI/map proof\n",checks);return 0;
}
