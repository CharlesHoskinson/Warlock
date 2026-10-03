#include <wayland-client.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct zwlr_virtual_pointer_v1;
static int calls=0,expected_direction;
static uint32_t now(void){return 123;}
static void record_axis(struct zwlr_virtual_pointer_v1*p,uint32_t time,uint32_t axis,wl_fixed_t value,int direction){(void)p;assert(calls++==0);assert(time==123&&axis==WL_POINTER_AXIS_VERTICAL_SCROLL&&direction==expected_direction);assert(wl_fixed_to_double(value)==15.0*direction);}
static void record_source(struct zwlr_virtual_pointer_v1*p,uint32_t source){(void)p;assert(calls++==1);assert(source==WL_POINTER_AXIS_SOURCE_WHEEL);}
static void record_frame(struct zwlr_virtual_pointer_v1*p){(void)p;assert(calls++==2);}
#define zwlr_virtual_pointer_v1_axis_discrete record_axis
#define zwlr_virtual_pointer_v1_axis_source record_source
#define zwlr_virtual_pointer_v1_frame record_frame
#include "wheel-command.h"
int main(void){
 const char* invalid[]={"wheel 0\n","wheel 2\n","wheel -2\n","wheel 1 x\n","wheel 1","wheel 1 \n","wheel +1\n","wheel nan\n","wheel 99999999999999999999999999999999\n","wheel --1\n"};
 for(unsigned i=0;i<sizeof(invalid)/sizeof(invalid[0]);i++){calls=0;assert(pointer_qa_wheel(invalid[i],0)== -1);assert(calls==0);}
 const char* old[]={"absolute 170 637.5 1600 1000\n","relative 1 2\n","button 272 0\n","sync\n"};
 for(unsigned i=0;i<sizeof(old)/sizeof(old[0]);i++){calls=0;assert(pointer_qa_wheel(old[i],0)==0);assert(calls==0);}
 for(int d=-1;d<=1;d+=2){calls=0;expected_direction=d;assert(pointer_qa_wheel(d<0?"wheel -1\n":"wheel 1\n",0)==1);assert(calls==3);}
 puts("PASS16 exact wheel/protocol command cases; no Wayland connection/native input");return 0;}
