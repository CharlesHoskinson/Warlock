#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
int main(int argc,char **argv){
 if(argc!=4||strcmp(argv[1],"-T"))return 64;
 const char *directory=getenv("FIXTURE_GRIM_DIRECTORY"),*mode=getenv("FIXTURE_GRIM_MODE");
 if(!directory)return 65;
 if(mode&&!strcmp(mode,"timeout"))sleep(2);
 char input[4096];if(snprintf(input,sizeof input,"%s/%s.png",directory,argv[2])>=(int)sizeof input)return 66;
 int in=open(input,O_RDONLY|O_NOFOLLOW),out=open(argv[3],O_WRONLY|O_CREAT|O_EXCL,0600);
 if(in<0||out<0)return 67;
 if(!mode||strcmp(mode,"empty")){char bytes[16384];ssize_t n;while((n=read(in,bytes,sizeof bytes))>0){ssize_t offset=0;while(offset<n){ssize_t wrote=write(out,bytes+offset,n-offset);if(wrote<=0)return 68;offset+=wrote;}}if(n<0)return 69;}
 close(in);return close(out)?70:0;
}
