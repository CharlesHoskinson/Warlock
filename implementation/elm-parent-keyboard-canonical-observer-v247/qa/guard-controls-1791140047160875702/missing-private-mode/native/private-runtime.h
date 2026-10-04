#ifndef ELM_PRIVATE_RUNTIME_H
#define ELM_PRIVATE_RUNTIME_H
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <limits.h>
static bool canonical_private_runtime(const char *runtime) {
    char prefix[128], resolved[PATH_MAX], descriptor[64];
    int count=snprintf(prefix,sizeof prefix,"/run/user/%u/wqa/",(unsigned)geteuid());
    if (count<0 || (size_t)count>=sizeof prefix || !runtime || strncmp(runtime,prefix,(size_t)count)) return false;
    const char *leaf=runtime+count;
    if (!*leaf || !strcmp(leaf,".") || !strcmp(leaf,"..") || strchr(leaf,'/')) return false;
    int fd=open(runtime,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    if (fd<0) return false;
    struct stat info;
    bool valid=fstat(fd,&info)==0 && S_ISDIR(info.st_mode) && info.st_uid==geteuid();
    count=snprintf(descriptor,sizeof descriptor,"/proc/self/fd/%d",fd);
    ssize_t length=count>0 && (size_t)count<sizeof descriptor ? readlink(descriptor,resolved,sizeof resolved-1):-1;
    close(fd);
    if (!valid || length<0 || (size_t)length>=sizeof resolved-1) return false;
    resolved[length]=0;
    return !strcmp(resolved,runtime);
}
#endif
