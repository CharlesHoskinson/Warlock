#include "physical_plan.h"
#include "physical_keymap.inc"
#include <linux/input-event-codes.h>
#include <openssl/sha.h>
#include <stdio.h>
#include <string.h>
struct physical_symbol {uint32_t symbol,wire;const char*name;};
static const struct physical_symbol SYMBOLS[]={
 {45,KEY_MINUS,"AE11"},{48,KEY_0,"AE10"},{49,KEY_1,"AE01"},{50,KEY_2,"AE02"},{51,KEY_3,"AE03"},{52,KEY_4,"AE04"},{53,KEY_5,"AE05"},{54,KEY_6,"AE06"},{55,KEY_7,"AE07"},{56,KEY_8,"AE08"},{57,KEY_9,"AE09"},
 {'a',KEY_A,"AC01"},{'b',KEY_B,"AB05"},{'c',KEY_C,"AB03"},{'d',KEY_D,"AC03"},{'e',KEY_E,"AD03"},{'f',KEY_F,"AC04"},{'g',KEY_G,"AC05"},{'h',KEY_H,"AC06"},{'i',KEY_I,"AD08"},{'j',KEY_J,"AC07"},{'k',KEY_K,"AC08"},{'l',KEY_L,"AC09"},{'m',KEY_M,"AB07"},{'n',KEY_N,"AB06"},{'o',KEY_O,"AD09"},{'p',KEY_P,"AD10"},{'q',KEY_Q,"AD01"},{'r',KEY_R,"AD04"},{'s',KEY_S,"AC02"},{'t',KEY_T,"AD05"},{'u',KEY_U,"AD07"},{'v',KEY_V,"AB04"},{'w',KEY_W,"AD02"},{'x',KEY_X,"AB02"},{'y',KEY_Y,"AD06"},{'z',KEY_Z,"AB01"},{XKB_KEY_Left,KEY_LEFT,"LEFT"}
};
const void*physical_map_bytes(void){return PHYSICAL_KEYMAP;}
size_t physical_map_size(void){return sizeof(PHYSICAL_KEYMAP);}
static int add(struct physical_plan*p,struct xkb_state*state,uint32_t symbol){
 const struct physical_symbol*known=NULL;
 for(size_t i=0;i<sizeof(SYMBOLS)/sizeof(SYMBOLS[0]);++i)if(SYMBOLS[i].symbol==symbol){known=&SYMBOLS[i];break;}
 if(!known||p->count>=256)return -1;
 xkb_keycode_t key=xkb_keymap_key_by_name(p->map,known->name);const xkb_keysym_t*syms=NULL;
 if(key!=known->wire+8||key<xkb_keymap_min_keycode(p->map)||key>xkb_keymap_max_keycode(p->map)||strcmp(xkb_keymap_key_get_name(p->map,key),known->name)||xkb_state_key_get_syms(state,key,&syms)!=1||syms[0]!=symbol||xkb_state_key_get_layout(state,key)!=0||xkb_state_serialize_mods(state,XKB_STATE_MODS_EFFECTIVE)!=0)return -1;
 if(symbol!=XKB_KEY_Left){char text[8]={0};if(xkb_state_key_get_utf8(state,key,text,sizeof(text))!=1||(unsigned char)text[0]!=symbol||text[1]!=0)return -1;}
 p->keys[p->count++]=(struct physical_key){symbol,known->wire,key,known->name};return 0;
}
int make_physical_plan(int argc,char**argv,struct physical_plan*p){
 memset(p,0,sizeof(*p));if(argc>1&&!strcmp(argv[1],"--plan")){p->cpu_only=1;--argc;++argv;}
 if(argc<3||strcmp(argv[1],"-d")||strcmp(argv[2],"20"))return -1;
 int text_mode=argc==5&&!strcmp(argv[3],"--");int left_mode=argc==9&&!strcmp(argv[3],"-k")&&!strcmp(argv[4],"Left")&&!strcmp(argv[5],"-k")&&!strcmp(argv[6],"Left")&&!strcmp(argv[7],"-k")&&!strcmp(argv[8],"Left");
 if(!text_mode&&!left_mode)return -1;
 if(text_mode&&(strlen(argv[4])==0||strlen(argv[4])>256))return -1;
 struct xkb_context*c=xkb_context_new(XKB_CONTEXT_NO_DEFAULT_INCLUDES|XKB_CONTEXT_NO_ENVIRONMENT_NAMES);if(!c)return -1;
 p->map=xkb_keymap_new_from_string(c,(const char*)PHYSICAL_KEYMAP,XKB_KEYMAP_FORMAT_TEXT_V1,XKB_KEYMAP_COMPILE_NO_FLAGS);xkb_context_unref(c);if(!p->map)return -1;
 struct xkb_state*state=xkb_state_new(p->map);if(!state)return -1;
 int result=0;if(text_mode){for(size_t i=0;argv[4][i];++i)if(add(p,state,(unsigned char)argv[4][i])){result=-1;break;}}else for(int i=0;i<3;++i)if(add(p,state,XKB_KEY_Left)){result=-1;break;}
 xkb_state_unref(state);if(result)return -1;
 unsigned char hash[SHA256_DIGEST_LENGTH];if(!SHA256(PHYSICAL_KEYMAP,sizeof(PHYSICAL_KEYMAP),hash))return -1;
 for(size_t i=0;i<sizeof(hash);++i){snprintf(p->hash+2*i,3,"%02x",hash[i]);}
 return 0;
}
void destroy_physical_plan(struct physical_plan*p){if(p->map)xkb_keymap_unref(p->map);p->map=NULL;}
void print_physical_plan(const struct physical_plan*p){
 printf("{\"cpuOnly\":%s,\"keymapSHA256\":\"%s\",\"keymapBytes\":%zu,\"plan\":[",p->cpu_only?"true":"false",p->hash,sizeof(PHYSICAL_KEYMAP));
 for(size_t i=0;i<p->count;++i){const struct physical_key*k=&p->keys[i];printf("%s{\"symbol\":%u,\"wire\":%u,\"xkb\":%u,\"name\":\"%s\"}",i?",":"",k->symbol,k->wire,k->xkb,k->name);}printf("]}");
}
