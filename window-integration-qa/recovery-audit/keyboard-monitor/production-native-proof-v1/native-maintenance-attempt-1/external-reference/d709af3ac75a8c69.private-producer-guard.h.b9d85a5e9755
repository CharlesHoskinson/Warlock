#ifndef PRIVATE_PRODUCER_GUARD_H
#define PRIVATE_PRODUCER_GUARD_H
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <unistd.h>
static int private_producer_error(const char *why){fprintf(stderr,"private producer refused: %s (errno=%d)\n",why,errno);return -1;}
static int private_producer_directory(const char *path){struct stat row;return !lstat(path,&row)&&S_ISDIR(row.st_mode)&&row.st_uid==getuid()&&(row.st_mode&0777)==0700;}
static int private_producer_path(const char *runtime){
    char prefix[96];snprintf(prefix,sizeof(prefix),"/run/user/%lu/wqa/",(unsigned long)getuid());
    if(!runtime||strncmp(runtime,prefix,strlen(prefix))||strlen(runtime)!=strlen(prefix)+4)return 0;
    for(const char *p=runtime+strlen(prefix);*p;p++)if(!strchr("0123456789abcdef",*p))return 0;
    return 1;
}
static int private_producer_live(pid_t pid,const char *start){
    char path[96],line[4096];snprintf(path,sizeof(path),"/proc/%ld/stat",(long)pid);
    struct stat row;if(stat(path,&row)||row.st_uid!=getuid())return 0;
    FILE *file=fopen(path,"r");if(!file)return 0;char *read=fgets(line,sizeof(line),file);fclose(file);if(!read)return 0;
    char *tail=strrchr(line,')'),*save=NULL;if(!tail)return 0;tail+=2;
    char *word=strtok_r(tail," \t\n",&save);for(unsigned n=0;word&&n<19;n++)word=strtok_r(NULL," \t\n",&save);
    return word&&start&&!strcmp(word,start);
}
static int private_producer_connect(void){
    const char *runtime=getenv("XDG_RUNTIME_DIR"),*display=getenv("WAYLAND_DISPLAY"),*flag=getenv("HYPR_A11Y_BRIDGE_PRIVATE");
    if(!private_producer_path(runtime))return private_producer_error("exact owned wqa runtime required; main and legacy tmp forbidden");
    char user[96],parent[104];snprintf(user,sizeof(user),"/run/user/%lu",(unsigned long)getuid());snprintf(parent,sizeof(parent),"%s/wqa",user);
    if(!private_producer_directory(user)||!private_producer_directory(parent)||!private_producer_directory(runtime))return private_producer_error("owned nonsymlink0700 runtime and parents required");
    if(!flag||strcmp(flag,"1")||getenv("WAYLAND_SOCKET")||(getenv("DISPLAY")&&*getenv("DISPLAY")))return private_producer_error("explicit private flag and no inherited/X target required");
    char cgroup[4096]={0};FILE *group=fopen("/proc/self/cgroup","r");if(!group)return private_producer_error("QA scope unavailable");size_t count=fread(cgroup,1,sizeof(cgroup)-1,group);fclose(group);cgroup[count]=0;
    if(!strstr(cgroup,"/qa-harness.slice/qa-harness-")||!strstr(cgroup,".scope"))return private_producer_error("dedicated QA scope required");
    struct rlimit limit;const char *backtrace=getenv("WINDOW_QA_BACKTRACE");int diagnostic=backtrace&&!strcmp(backtrace,"1");
    if(getrlimit(RLIMIT_CORE,&limit)||(diagnostic?(limit.rlim_cur!=RLIM_INFINITY||limit.rlim_max!=RLIM_INFINITY):(limit.rlim_cur!=1||limit.rlim_max!=1)))return private_producer_error("exact inherited QA core limit required");
    if(!display||strncmp(display,"wayland-",8)||!display[8])return private_producer_error("explicit private wayland display required");
    for(const char *p=display+8;*p;p++)if(!isdigit((unsigned char)*p))return private_producer_error("invalid private display name");
    const char *pid_text=getenv("POINTER_QA_COMPOSITOR_PID"),*start=getenv("POINTER_QA_COMPOSITOR_START");char *end=NULL;errno=0;long value=pid_text?strtol(pid_text,&end,10):0;
    if(errno||value<=0||value>INT_MAX||!end||*end||!private_producer_live((pid_t)value,start))return private_producer_error("exact live compositor PID/start required");
    struct sockaddr_un address={.sun_family=AF_UNIX};int length=snprintf(address.sun_path,sizeof(address.sun_path),"%s/%s",runtime,display);
    if(length<0||(size_t)length>=sizeof(address.sun_path))return private_producer_error("private socket path too long");
    struct stat before,after;if(lstat(address.sun_path,&before)||!S_ISSOCK(before.st_mode)||before.st_uid!=getuid())return private_producer_error("owned nonsymlink Wayland socket required");
    int fd=socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0);if(fd<0)return private_producer_error("private socket allocation failed");
    struct ucred peer;socklen_t size=sizeof(peer);
    if(connect(fd,(struct sockaddr*)&address,sizeof(address))||getsockopt(fd,SOL_SOCKET,SO_PEERCRED,&peer,&size)||peer.pid!=(pid_t)value||peer.uid!=getuid()||lstat(address.sun_path,&after)||before.st_dev!=after.st_dev||before.st_ino!=after.st_ino||!private_producer_live((pid_t)value,start)){
        close(fd);return private_producer_error("private peer/socket/process identity changed or unavailable");
    }
    return fd;
}
#endif
