#define _GNU_SOURCE
#include <wayland-client.h>
#include "session-lock-client.h"
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <poll.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

struct client;
struct buffer {struct client *owner;struct wl_buffer *resource;void *data;size_t bytes;struct buffer *next;};
struct output {struct client *owner;uint32_t name;struct wl_output *output;struct wl_surface *surface;struct ext_session_lock_surface_v1 *role;};
struct client {
    struct wl_display *display;struct wl_registry *registry;struct wl_compositor *compositor;struct wl_shm *shm;
    struct ext_session_lock_manager_v1 *manager;struct ext_session_lock_v1 *lock;
    struct output outputs[8];struct buffer *buffers;unsigned count,inflight;size_t allocated;
    const char *control;bool locked,failed,finished,unlocked;uint64_t sequence;
};
static volatile sig_atomic_t interrupted;
static void signal_stop(int value){interrupted=value;}
static uint64_t stamp(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return 0;return (uint64_t)t.tv_sec*UINT64_C(1000000000)+(uint64_t)t.tv_nsec;}
static void event(struct client *c,const char *kind){printf("{\"event\":\"%s\",\"sequence\":%" PRIu64 ",\"monotonicNs\":%" PRIu64 ",\"outputs\":%u,\"retainedBytes\":%zu}\n",kind,++c->sequence,stamp(),c->count,c->allocated);fflush(stdout);}
static void failure(struct client *c,const char *reason){fprintf(stderr,"Private lock fixture refused: %s\n",reason);c->failed=true;}
static bool counter(const char *text,uint64_t *value){
    if(!text || !*text || *text=='0')return false;
    uint64_t n=0;for(const char *p=text;*p;++p){if(*p<'0' || *p>'9' || n>(UINT64_MAX-(unsigned)(*p-'0'))/10)return false;n=n*10+(unsigned)(*p-'0');}*value=n;return true;
}
static bool guard(struct client *c,uint64_t *server){
    const char *enabled=getenv("WARLOCK_PRIVATE_LOCK_FIXTURE"),*runtime=getenv("XDG_RUNTIME_DIR"),*display=getenv("WAYLAND_DISPLAY");
    c->control=getenv("WARLOCK_LOCK_CONTROL_PATH");struct rlimit limit;char group[4096]={0};
    FILE *f=fopen("/proc/self/cgroup","r");if(!f)return false;size_t n=fread(group,1,sizeof(group)-1,f);fclose(f);
    if(!n || !strstr(group,"qa-harness-") || !strstr(group,".scope") || getrlimit(RLIMIT_CORE,&limit) || limit.rlim_cur!=1 || limit.rlim_max!=1)return false;
    struct stat directory,socket;uint64_t device,inode;
    if(!enabled || strcmp(enabled,"1") || !runtime || *runtime!='/' || lstat(runtime,&directory) || !S_ISDIR(directory.st_mode) || directory.st_uid!=getuid() || (directory.st_mode&0777)!=0700)return false;
    if(!display || !*display || strchr(display,'/') || !strcmp(display,".") || !strcmp(display,"..") || !c->control || strncmp(c->control,runtime,strlen(runtime)) || c->control[strlen(runtime)]!='/' || !c->control[strlen(runtime)+1] || strchr(c->control+strlen(runtime)+1,'/'))return false;
    if(!counter(getenv("WARLOCK_LOCK_SOCKET_DEV"),&device) || !counter(getenv("WARLOCK_LOCK_SOCKET_INO"),&inode) || !counter(getenv("WARLOCK_LOCK_SERVER_PID"),server) || *server>INT32_MAX)return false;
    char path[4096];if(snprintf(path,sizeof path,"%s/%s",runtime,display)>=(int)sizeof path || lstat(path,&socket) || !S_ISSOCK(socket.st_mode) || socket.st_uid!=getuid() || (uint64_t)socket.st_dev!=device || (uint64_t)socket.st_ino!=inode)return false;
    return true;
}
static void remove_buffer(struct buffer *b){struct client *c=b->owner;struct buffer **p=&c->buffers;while(*p && *p!=b)p=&(*p)->next;if(*p){*p=b->next;--c->inflight;c->allocated-=b->bytes;}wl_buffer_destroy(b->resource);munmap(b->data,b->bytes);free(b);}
static void released(void *data,struct wl_buffer *buffer){(void)buffer;struct buffer *b=data;event(b->owner,"buffer-release");remove_buffer(b);}
static const struct wl_buffer_listener buffer_listener={released};
static bool commit(struct output *out,uint32_t width,uint32_t height){
    struct client *c=out->owner;
    if(width<1 || height<1 || width>4096 || height>4096){failure(c,"configure dimensions");return false;}
    size_t bytes=(size_t)width*height*4;
    if(c->inflight>=8 || bytes>UINT64_C(128)*1024*1024-c->allocated){failure(c,"retained SHM bound");return false;}
    int fd=memfd_create("warlock-private-lock",MFD_CLOEXEC);
    if(fd<0 || ftruncate(fd,(off_t)bytes)){if(fd>=0)close(fd);failure(c,"SHM allocation");return false;}
    void *pixels=mmap(NULL,bytes,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
    if(pixels==MAP_FAILED){close(fd);failure(c,"SHM mapping");return false;}
    for(size_t i=0;i<bytes/4;++i)((uint32_t*)pixels)[i]=UINT32_C(0xff10111a);
    struct wl_shm_pool *pool=wl_shm_create_pool(c->shm,fd,(int)bytes);
    struct wl_buffer *resource=pool?wl_shm_pool_create_buffer(pool,0,(int)width,(int)height,(int)width*4,WL_SHM_FORMAT_ARGB8888):NULL;
    if(pool)wl_shm_pool_destroy(pool);
    close(fd);
    if(!resource){munmap(pixels,bytes);failure(c,"SHM buffer");return false;}
    struct buffer *b=calloc(1,sizeof *b);if(!b){wl_buffer_destroy(resource);munmap(pixels,bytes);failure(c,"buffer record");return false;}
    *b=(struct buffer){.owner=c,.resource=resource,.data=pixels,.bytes=bytes,.next=c->buffers};c->buffers=b;++c->inflight;c->allocated+=bytes;
    wl_buffer_add_listener(resource,&buffer_listener,b);wl_surface_attach(out->surface,resource,0,0);wl_surface_damage(out->surface,0,0,(int)width,(int)height);wl_surface_commit(out->surface);event(c,"opaque-commit");return true;
}
static void configure(void *data,struct ext_session_lock_surface_v1 *role,uint32_t serial,uint32_t width,uint32_t height){
    struct output *out=data;if(out->owner->failed)return;ext_session_lock_surface_v1_ack_configure(role,serial);event(out->owner,"ack-configure");commit(out,width,height);
}
static const struct ext_session_lock_surface_v1_listener surface_listener={configure};
static void create_surface(struct output *out){struct client *c=out->owner;if(!c->lock || out->surface || !out->output)return;out->surface=wl_compositor_create_surface(c->compositor);if(!out->surface){failure(c,"lock surface allocation");return;}out->role=ext_session_lock_v1_get_lock_surface(c->lock,out->surface,out->output);if(!out->role){failure(c,"lock role allocation");return;}ext_session_lock_surface_v1_add_listener(out->role,&surface_listener,out);}
static void global(void *data,struct wl_registry *registry,uint32_t name,const char *interface,uint32_t version){
    struct client *c=data;
    if(!strcmp(interface,"wl_compositor"))c->compositor=wl_registry_bind(registry,name,&wl_compositor_interface,version<4?version:4);
    else if(!strcmp(interface,"wl_shm"))c->shm=wl_registry_bind(registry,name,&wl_shm_interface,1);
    else if(!strcmp(interface,"ext_session_lock_manager_v1"))c->manager=wl_registry_bind(registry,name,&ext_session_lock_manager_v1_interface,1);
    else if(!strcmp(interface,"wl_output")){
        if(c->count==8){failure(c,"output bound");return;}
        struct output *out=&c->outputs[c->count++];*out=(struct output){.owner=c,.name=name,.output=wl_registry_bind(registry,name,&wl_output_interface,1)};if(c->lock)create_surface(out);
    }
}
static void destroy_output(struct output *out){if(out->role){ext_session_lock_surface_v1_destroy(out->role);out->role=NULL;}if(out->surface){wl_surface_destroy(out->surface);out->surface=NULL;}if(out->output){wl_output_destroy(out->output);out->output=NULL;}}
static void removed(void *data,struct wl_registry *registry,uint32_t name){(void)registry;struct client *c=data;for(unsigned i=0;i<c->count;++i)if(c->outputs[i].name==name)destroy_output(&c->outputs[i]);}
static const struct wl_registry_listener registry_listener={global,removed};
static void locked(void *data,struct ext_session_lock_v1 *lock){(void)lock;struct client *c=data;c->locked=true;event(c,"locked");}
static void finished(void *data,struct ext_session_lock_v1 *lock){(void)lock;struct client *c=data;c->finished=true;failure(c,"server finished lock");event(c,"finished");}
static const struct ext_session_lock_v1_listener lock_listener={locked,finished};
static bool wants_unlock(struct client *c){
    int fd=open(c->control,O_RDONLY|O_NOFOLLOW|O_CLOEXEC);if(fd<0){failure(c,"private control missing");return false;}
    struct stat st;char text[17]={0};
    if(fstat(fd,&st) || !S_ISREG(st.st_mode) || st.st_uid!=getuid() || (st.st_mode&0777)!=0600 || st.st_nlink!=1 || st.st_size>16){close(fd);failure(c,"private control identity");return false;}
    ssize_t size=read(fd,text,16);close(fd);if(size<0){failure(c,"private control read");return false;}
    if(!strcmp(text,"unlock\n") || !strcmp(text,"unlock"))return true;
    if(*text && strcmp(text,"hold\n") && strcmp(text,"hold"))failure(c,"private control command");
    return false;
}
int main(void){
    struct client c={0};uint64_t expected;
    if(!guard(&c,&expected)){failure(&c,"protected private endpoint guard");return 1;}
    signal(SIGTERM,signal_stop);signal(SIGINT,signal_stop);
    c.display=wl_display_connect(getenv("WAYLAND_DISPLAY"));if(!c.display){failure(&c,"connect");return 1;}
    struct ucred peer;socklen_t length=sizeof peer;
    if(getsockopt(wl_display_get_fd(c.display),SOL_SOCKET,SO_PEERCRED,&peer,&length) || length!=sizeof peer || peer.uid!=getuid() || peer.pid!=(pid_t)expected){failure(&c,"exact private server peer");goto done;}
    c.registry=wl_display_get_registry(c.display);wl_registry_add_listener(c.registry,&registry_listener,&c);
    if(wl_display_roundtrip(c.display)<0 || !c.compositor || !c.shm || !c.manager || !c.count || c.failed){failure(&c,"required private globals");goto done;}
    c.lock=ext_session_lock_manager_v1_lock(c.manager);ext_session_lock_v1_add_listener(c.lock,&lock_listener,&c);
    for(unsigned i=0;i<c.count;++i)create_surface(&c.outputs[i]);
    event(&c,"lock-requested");
    while(!c.failed && !interrupted){
        if(wl_display_dispatch_pending(c.display)<0){failure(&c,"pending dispatch");break;}
        if(c.locked && wants_unlock(&c))break;
        if(c.failed)break;
        if(wl_display_flush(c.display)<0 && errno!=EAGAIN){failure(&c,"flush");break;}
        struct pollfd p={.fd=wl_display_get_fd(c.display),.events=POLLIN};int ready=poll(&p,1,40);
        if(ready<0 && errno==EINTR)continue;
        if(ready<0 || (ready && (p.revents&(POLLERR|POLLHUP|POLLNVAL)))){failure(&c,"display readiness");break;}
        if(ready && wl_display_dispatch(c.display)<0){failure(&c,"display dispatch");break;}
    }
done:
    if(c.lock){
        // A sync resolves any queued Locked before choosing its destructor.
        if(wl_display_roundtrip(c.display)<0)failure(&c,"pre-teardown sync");
        if(c.locked){ext_session_lock_v1_unlock_and_destroy(c.lock);event(&c,"unlock-requested");}
        else ext_session_lock_v1_destroy(c.lock);
        c.lock=NULL;
        if(wl_display_roundtrip(c.display)<0)failure(&c,"unlock sync");else if(c.locked){c.unlocked=true;event(&c,"unlock-synced");}
    }
    for(unsigned i=0;i<c.count;++i)destroy_output(&c.outputs[i]);
    while(c.buffers)remove_buffer(c.buffers);
    if(c.manager)ext_session_lock_manager_v1_destroy(c.manager);
    if(c.shm)wl_shm_destroy(c.shm);
    if(c.compositor)wl_compositor_destroy(c.compositor);
    if(c.registry)wl_registry_destroy(c.registry);
    if(c.display)wl_display_disconnect(c.display);
    event(&c,"exit");return c.failed || interrupted || !c.unlocked?1:0;
}
