#define _DEFAULT_SOURCE
#include <sys/stat.h>
#include <unistd.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
static const char *runtime,*socket;
static const char *fake_env(const char *key){if(!strcmp(key,"XDG_RUNTIME_DIR"))return runtime;if(!strcmp(key,"WAYLAND_DISPLAY"))return socket;if(!strcmp(key,"ELM_PARENT_INPUT_QA"))return "1";return NULL;}
static int fake_stat(const char *path,struct stat *st){(void)path;memset(st,0,sizeof *st);st->st_uid=geteuid();st->st_mode=S_IFSOCK|0600;return 0;}
#define getenv fake_env
#define lstat fake_stat
#include "actual-function.c"
int main(void){char paths[4][128];snprintf(paths[0],128,"/run/user/%u/wqa/isolated",getuid());snprintf(paths[1],128,"/run/user/%u/wqa/..",getuid());snprintf(paths[2],128,"/run/user/%u",getuid());snprintf(paths[3],128,"/arbitrary/runtime");for(int i=0;i<4;i++){runtime=paths[i];socket="wayland-owned";printf("%d %d %s\n",i,private_socket(),runtime);}runtime=NULL;socket="/arbitrary/owned-socket";printf("4 %d %s\n",private_socket(),socket);return 0;}
