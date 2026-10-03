#ifndef PHYSICAL_PLAN_H
#define PHYSICAL_PLAN_H
#include <stdint.h>
#include <stddef.h>
#include <xkbcommon/xkbcommon.h>
struct physical_key {uint32_t symbol,wire,xkb;const char*name;};
struct physical_plan {struct physical_key keys[256];size_t count;struct xkb_keymap*map;char hash[65];int cpu_only;};
int make_physical_plan(int argc,char**argv,struct physical_plan*plan);
void destroy_physical_plan(struct physical_plan*plan);
void print_physical_plan(const struct physical_plan*plan);
const void*physical_map_bytes(void);
size_t physical_map_size(void);
#endif
