#include <stdio.h>
#include <gdk/gdk.h>
int main(void){printf("{\"button-press\":%d,\"button-release\":%d,\"key-press\":%d,\"key-release\":%d}\n",GDK_BUTTON_PRESS,GDK_BUTTON_RELEASE,GDK_KEY_PRESS,GDK_KEY_RELEASE);return 0;}
