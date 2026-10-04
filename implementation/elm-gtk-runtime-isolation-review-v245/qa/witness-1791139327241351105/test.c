#define _DEFAULT_SOURCE
#define _POSIX_C_SOURCE 200809L
#include <glib.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
static const char *runtime;
static gboolean protected_scope(void){return TRUE;}
static const char *fake_env(const char *key){if(!strcmp(key,"XDG_RUNTIME_DIR"))return runtime;if(!strcmp(key,"WAYLAND_DISPLAY"))return "wayland-owned";if(!strcmp(key,"ELM_GTK_ROLE_QA"))return "1";if(!strcmp(key,"GDK_BACKEND"))return "wayland";if(!strcmp(key,"WAYLAND_DEBUG"))return "client";return NULL;}
static int fake_stat(const char *path,struct stat *st){memset(st,0,sizeof *st);st->st_uid=getuid();st->st_mode=(!strcmp(path,runtime)?S_IFDIR|0700:S_IFSOCK|0600);return 0;}
#define getenv fake_env
#define lstat fake_stat
#include "actual-function.c"
int main(void){char paths[4][128];snprintf(paths[0],128,"/run/user/%u/wqa/isolated",getuid());snprintf(paths[1],128,"/run/user/%u/wqa/.",getuid());snprintf(paths[2],128,"/run/user/%u/wqa/..",getuid());snprintf(paths[3],128,"/run/user/%u",getuid());for(unsigned i=0;i<4;i++){runtime=paths[i];printf("%u %d %s\n",i,private_environment(),runtime);}return 0;}
