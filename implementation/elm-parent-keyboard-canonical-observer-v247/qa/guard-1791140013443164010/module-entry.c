#include <dlfcn.h>
#include <stdio.h>
struct weston_compositor;
int main(int argc,char**argv){if(argc!=2)return 2;void*module=dlopen(argv[1],RTLD_NOW);if(!module){fputs(dlerror(),stderr);return 3;}int(*entry)(struct weston_compositor*,int*,char**)=dlsym(module,"wet_module_init");if(!entry)return 4;int result=entry(NULL,NULL,NULL);dlclose(module);return result==-1?0:5;}
