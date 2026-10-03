#include "physical_plan.h"
#include "physical_keymap.inc"
#include <linux/input-event-codes.h>
#include <openssl/sha.h>
#include <stdio.h>
#include <string.h>
struct known_key{uint32_t symbol,wire;const char*name;};
static const struct known_key META={XKB_KEY_Super_L,KEY_LEFTMETA,"LWIN"},CTRL={XKB_KEY_Control_L,KEY_LEFTCTRL,"LCTL"},PKEY={'p',KEY_P,"AD10"},TKEY={'t',KEY_T,"AD05"},MENU={XKB_KEY_Menu,KEY_COMPOSE,"COMP"},RETURN={XKB_KEY_Return,KEY_ENTER,"RTRN"},ESCAPE={XKB_KEY_Escape,KEY_ESC,"ESC"};
const void*physical_map_bytes(void){return PHYSICAL_KEYMAP;}
size_t physical_map_size(void){return sizeof(PHYSICAL_KEYMAP);}
static int add(struct physical_plan*p,struct xkb_state*state,const struct known_key*known,uint32_t direction){
 if(p->count>=6)return -1;
 xkb_keycode_t key=xkb_keymap_key_by_name(p->map,known->name);
 if(key!=known->wire+8||key<xkb_keymap_min_keycode(p->map)||key>xkb_keymap_max_keycode(p->map)||strcmp(xkb_keymap_key_get_name(p->map,key),known->name)||xkb_state_key_get_one_sym(state,key)!=known->symbol||xkb_state_key_get_layout(state,key)!=0)return -1;
 uint32_t before=xkb_state_serialize_mods(state,XKB_STATE_MODS_DEPRESSED);
 xkb_state_update_key(state,key,direction?XKB_KEY_DOWN:XKB_KEY_UP);
 uint32_t depressed=xkb_state_serialize_mods(state,XKB_STATE_MODS_DEPRESSED),latched=xkb_state_serialize_mods(state,XKB_STATE_MODS_LATCHED),locked=xkb_state_serialize_mods(state,XKB_STATE_MODS_LOCKED),group=xkb_state_serialize_layout(state,XKB_STATE_LAYOUT_EFFECTIVE);
 xkb_mod_index_t meta=xkb_keymap_mod_get_index(p->map,XKB_MOD_NAME_LOGO),ctrl=xkb_keymap_mod_get_index(p->map,XKB_MOD_NAME_CTRL);
 if(meta>=32||ctrl>=32||latched||locked||group||(depressed&~((1U<<meta)|(1U<<ctrl))))return -1;
 p->keys[p->count++]=(struct physical_key){known->symbol,known->wire,key,known->name,direction,depressed,latched,locked,group,depressed!=before};return 0;
}
int make_physical_plan(int argc,char**argv,struct physical_plan*p){
 memset(p,0,sizeof(*p));if(argc>1&&!strcmp(argv[1],"--plan")){p->cpu_only=1;--argc;++argv;}
 if(argc!=3||strcmp(argv[1],"--chord"))return -1;
 const struct known_key*list[3];size_t count=0;
 if(!strcmp(argv[2],"super-p")){list[count++]=&META;list[count++]=&PKEY;}
 else if(!strcmp(argv[2],"super-ctrl-t")){list[count++]=&META;list[count++]=&CTRL;list[count++]=&TKEY;}
 else if(!strcmp(argv[2],"menu"))list[count++]=&MENU;
 else if(!strcmp(argv[2],"return"))list[count++]=&RETURN;
 else if(!strcmp(argv[2],"escape"))list[count++]=&ESCAPE;
 else return -1;
 struct xkb_context*c=xkb_context_new(XKB_CONTEXT_NO_DEFAULT_INCLUDES|XKB_CONTEXT_NO_ENVIRONMENT_NAMES);if(!c)return -1;
 p->map=xkb_keymap_new_from_string(c,(const char*)PHYSICAL_KEYMAP,XKB_KEYMAP_FORMAT_TEXT_V1,XKB_KEYMAP_COMPILE_NO_FLAGS);xkb_context_unref(c);if(!p->map)return -1;
 struct xkb_state*state=xkb_state_new(p->map);if(!state)return -1;
 int result=0;
 for(size_t i=0;i<count;++i)if(add(p,state,list[i],1)){result=-1;break;}
 if(!result)for(size_t i=count;i>0;--i)if(add(p,state,list[i-1],0)){result=-1;break;}
 if(xkb_state_serialize_mods(state,XKB_STATE_MODS_EFFECTIVE)||xkb_state_serialize_layout(state,XKB_STATE_LAYOUT_EFFECTIVE))result=-1;
 xkb_state_unref(state);if(result)return -1;
 unsigned char hash[SHA256_DIGEST_LENGTH];if(!SHA256(PHYSICAL_KEYMAP,sizeof(PHYSICAL_KEYMAP),hash))return -1;
 for(size_t i=0;i<sizeof(hash);++i)snprintf(p->hash+2*i,3,"%02x",hash[i]);
 return 0;
}
void destroy_physical_plan(struct physical_plan*p){if(p->map)xkb_keymap_unref(p->map);p->map=NULL;}
void print_physical_plan(const struct physical_plan*p){
 printf("{\"cpuOnly\":%s,\"keymapSHA256\":\"%s\",\"keymapBytes\":%zu,\"plan\":[",p->cpu_only?"true":"false",p->hash,sizeof(PHYSICAL_KEYMAP));
 for(size_t i=0;i<p->count;++i){const struct physical_key*k=&p->keys[i];printf("%s{\"symbol\":%u,\"wire\":%u,\"xkb\":%u,\"name\":\"%s\",\"state\":%u,\"modsDepressed\":%u,\"modsLatched\":%u,\"modsLocked\":%u,\"group\":%u,\"modifierTransition\":%s}",i?",":"",k->symbol,k->wire,k->xkb,k->name,k->state,k->depressed,k->latched,k->locked,k->group,k->modifiers_changed?"true":"false");}printf("]}");
}
