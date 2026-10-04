#define main keymap_fixture_main
#include "keymap.c"
#undef main
#include <assert.h>
#include <fcntl.h>
#include <errno.h>
static int input(const char*raw,size_t length){int fd=memfd_create("qa-keymap",MFD_CLOEXEC);assert(fd>=0);assert(write(fd,raw,length)==(ssize_t)length);return fd;}
static void closed(int fd){errno=0;assert(fcntl(fd,F_GETFD)==-1&&errno==EBADF);}
int main(void){
 struct xkb_context*c=xkb_context_new(XKB_CONTEXT_NO_FLAGS);assert(c);struct xkb_keymap*k=xkb_keymap_new_from_names(c,NULL,XKB_KEYMAP_COMPILE_NO_FLAGS);assert(k);char*raw=xkb_keymap_get_as_string(k,XKB_KEYMAP_FORMAT_TEXT_V1);assert(raw);size_t n=strlen(raw)+1;assert(n<1024*1024);xkb_mod_index_t shift=xkb_keymap_mod_get_index(k,XKB_MOD_NAME_SHIFT);assert(shift<32);
 struct state s={.seat_name=77};int fd=input(raw,n);keymap(&s,NULL,1,fd,n);closed(fd);assert(s.received&&!s.failed);struct stat st;assert(stat("keymap.xkb",&st)==0&&st.st_size==(off_t)n-1);unlink("keymap.xkb");
 s=(struct state){0};fd=input(raw,n);keymap(&s,NULL,0,fd,n);closed(fd);assert(s.failed&&!s.received);
 s=(struct state){0};fd=input(raw,n);keymap(&s,NULL,1,fd,1024*1024+1);closed(fd);assert(s.failed&&!s.received);
 s=(struct state){0};fd=input(raw,n-1);keymap(&s,NULL,1,fd,n);closed(fd);assert(s.failed&&!s.received);
 char nonnul[]="abcd";s=(struct state){0};fd=input(nonnul,4);keymap(&s,NULL,1,fd,4);closed(fd);assert(s.failed&&!s.received);
 char embedded[]={1,0,1,0};s=(struct state){0};fd=input(embedded,4);keymap(&s,NULL,1,fd,4);closed(fd);assert(s.failed&&!s.received);
 s=(struct state){.received=1};fd=input(raw,n);keymap(&s,NULL,1,fd,n);closed(fd);assert(s.failed&&s.received);
 s=(struct state){0};fd=input("bad\n",5);keymap(&s,NULL,1,fd,5);closed(fd);assert(s.failed&&!s.received);
 s=(struct state){0};FILE*f=fopen("keymap.xkb","wx");assert(f);assert(fclose(f)==0);fd=input(raw,n);keymap(&s,NULL,1,fd,n);closed(fd);assert(s.failed&&!s.received);unlink("keymap.xkb");
 free(raw);xkb_keymap_unref(k);xkb_context_unref(c);puts("actual-keymap-callback-checks:9");return 0;
}
