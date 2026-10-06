#define _GNU_SOURCE
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
static const char *control_path,*publisher;
static int replacement,armed;
static int raced_fstat(int fd,struct stat *st){
 if(armed){armed=0;
  if(replacement){char temp[4096];assert(snprintf(temp,sizeof temp,"%s.tmp",control_path)<(int)sizeof temp);int out=open(temp,O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC,0600);assert(out>=0 && write(out,"unlock\n",7)==7);close(out);assert(rename(temp,control_path)==0);}
  else {pid_t child=fork();assert(child>=0);if(!child){execl("/usr/bin/python3","python3","-B",publisher,control_path,"unlock",NULL);_exit(99);}int status;assert(waitpid(child,&status,0)==child && WIFEXITED(status) && WEXITSTATUS(status)==0);}
 }
 return fstat(fd,st);
}
#define fstat raced_fstat
#define main original_fixture_main
#include "session-lock.c"
#undef main
#undef fstat
int main(int argc,char **argv){
 assert(argc==4);publisher=argv[1];control_path=argv[2];replacement=strcmp(argv[3],"replace")==0;
 struct stat before,after;assert(lstat(control_path,&before)==0);
 struct client client={.control=control_path};armed=1;
 const bool unlocked=wants_unlock(&client);
 assert(lstat(control_path,&after)==0 && S_ISREG(after.st_mode) && after.st_uid==getuid() && (after.st_mode&0777)==0600 && after.st_nlink==1);
 if(replacement)assert(!unlocked && client.failed && before.st_ino!=after.st_ino);
 else assert(unlocked && !client.failed && before.st_ino==after.st_ino && before.st_dev==after.st_dev);
 printf("{\"passed\":true,\"reproducedOriginalUnlinkedReaderRefusal\":%s,\"stableIdentityPublisherAccepted\":%s}\n",replacement?"true":"false",replacement?"false":"true");return 0;
}
