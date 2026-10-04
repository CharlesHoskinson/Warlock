#include <stdio.h>
#include <gdk/gdk.h>
int main(void){printf("{\"button-press\":%d,\"button-release\":%d,\"key-press\":%d,\"key-release\":%d,\"shiftMask\":%u}\n",GDK_BUTTON_PRESS,GDK_BUTTON_RELEASE,GDK_KEY_PRESS,GDK_KEY_RELEASE,GDK_SHIFT_MASK);return 0;}
