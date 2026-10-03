#include <xkbcommon/xkbcommon.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc,char**argv){
 if(argc!=2)return 2;
 struct xkb_context*c=xkb_context_new(XKB_CONTEXT_NO_DEFAULT_INCLUDES|XKB_CONTEXT_NO_ENVIRONMENT_NAMES);if(!c)return 3;
 xkb_context_include_path_clear(c);if(!xkb_context_include_path_append(c,"/usr/share/X11/xkb"))return 4;
 struct xkb_rule_names names={.rules="evdev",.model="pc105",.layout="us",.variant="",.options=""};
 struct xkb_keymap*m=xkb_keymap_new_from_names(c,&names,XKB_KEYMAP_COMPILE_NO_FLAGS);xkb_context_unref(c);if(!m)return 5;
 char*text=xkb_keymap_get_as_string(m,XKB_KEYMAP_FORMAT_TEXT_V1);xkb_keymap_unref(m);if(!text)return 6;
 size_t n=strlen(text);if(n==0||n>1048576||strstr(text,"include "))return 7;
 FILE*f=fopen(argv[1],"wx");if(!f)return 8;fputs("/* CPU-materialized evdev/pc105/us; no runtime source includes. */\nstatic const unsigned char PHYSICAL_KEYMAP[]={\n",f);
 for(size_t i=0;i<n;++i){if(fprintf(f,"%u,",(unsigned char)text[i])<0)return 9;if(i%32==31)fputc('\n',f);}fputs("0};\n",f);free(text);return fclose(f)?10:0;
}
