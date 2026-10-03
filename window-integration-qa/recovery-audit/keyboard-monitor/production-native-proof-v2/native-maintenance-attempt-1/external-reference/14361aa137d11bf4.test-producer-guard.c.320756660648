#define _GNU_SOURCE
#include "private-producer-guard.h"
int main(void){
    char user[128],bad[128];snprintf(user,sizeof(user),"/run/user/%lu/wqa/1a2b",(unsigned long)getuid());
    if(!private_producer_path(user))return 1;
    for(unsigned n=0;n<8;n++){
        const char *suffix[]={"","/1a2b","/1A2b","/123","/12345","/qa-1a2b","/1a2b/x","/zzzz"};
        snprintf(bad,sizeof(bad),"/run/user/%lu/wqa%s",(unsigned long)getuid(),suffix[n]);if(private_producer_path(bad))return 2;
    }
    if(private_producer_path("/run/user/0")||private_producer_path("/tmp/kbn-old")||private_producer_path(NULL))return 3;
    char temp[]="/tmp/qa-producer-guard-XXXXXX";if(!mkdtemp(temp)||!private_producer_directory(temp))return 4;
    if(chmod(temp,0755)||private_producer_directory(temp))return 5;
    chmod(temp,0700);char link[160];snprintf(link,sizeof(link),"%s-link",temp);if(symlink(temp,link)||private_producer_directory(link))return 6;unlink(link);rmdir(temp);
    FILE *file=fopen("/proc/self/stat","r");char line[4096];if(!file||!fgets(line,sizeof(line),file))return 7;fclose(file);
    char *tail=strrchr(line,')')+2,*save=NULL,*word=strtok_r(tail," ",&save);for(int n=0;word&&n<19;n++)word=strtok_r(NULL," ",&save);
    if(!word||!private_producer_live(getpid(),word)||private_producer_live(getpid(),"0")||private_producer_live(-1,word))return 8;
    (void)private_producer_connect;return 0;
}
