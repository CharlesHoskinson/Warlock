#define _XOPEN_SOURCE 700
#include <glib.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
static gboolean protected_scope(void){return TRUE;}
static gboolean canonical_runtime(const char *runtime) {
 char *resolved=realpath(runtime,NULL);
 gboolean valid=resolved && !strcmp(resolved,runtime);
 free(resolved);
 return valid;
}
static gboolean private_environment(void){const char*runtime=getenv("XDG_RUNTIME_DIR"),*display=getenv("WAYLAND_DISPLAY");struct stat st;char base[128];snprintf(base,sizeof base,"/run/user/%u/wqa/",(unsigned)getuid());if(!protected_scope()||!runtime||strncmp(runtime,base,strlen(base))||!runtime[strlen(base)]||strchr(runtime+strlen(base),'/')||!strcmp(runtime+strlen(base),".")||!strcmp(runtime+strlen(base),"..")||!canonical_runtime(runtime)||!display||!*display||strchr(display,'/'))return FALSE;if(lstat(runtime,&st)||!S_ISDIR(st.st_mode)||st.st_uid!=getuid()||(st.st_mode&0777)!=0700)return FALSE;char*path=g_build_filename(runtime,display,NULL);gboolean valid=!lstat(path,&st)&&S_ISSOCK(st.st_mode)&&st.st_uid==getuid();g_free(path);return valid && !g_strcmp0(getenv("ELM_GTK_ROLE_QA"),"1") && !g_strcmp0(getenv("GDK_BACKEND"),"wayland") && !g_strcmp0(getenv("WAYLAND_DEBUG"),"client");}
int main(void){printf("%d\n",private_environment());return 0;}
