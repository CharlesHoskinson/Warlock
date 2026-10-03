// Real private host capability observation only; no input, surface or fake metadata.
#include <wayland-client.h>
#include "linux-dmabuf-client.h"
#include <xf86drm.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static struct zwp_linux_dmabuf_v1 *dmabuf;
static dev_t device_id;
static unsigned format_bytes;
static int complete;
static void global(void *d,struct wl_registry *r,uint32_t n,const char *i,uint32_t v){(void)d;if(!strcmp(i,zwp_linux_dmabuf_v1_interface.name)&&v>=4)dmabuf=wl_registry_bind(r,n,&zwp_linux_dmabuf_v1_interface,v>5?5:v);}
static void removed(void*d,struct wl_registry*r,uint32_t n){(void)d;(void)r;(void)n;}
static void done(void*d,struct zwp_linux_dmabuf_feedback_v1*f){(void)d;(void)f;complete=1;}
static void table(void*d,struct zwp_linux_dmabuf_feedback_v1*f,int fd,uint32_t size){(void)d;(void)f;format_bytes=size;close(fd);}
static void device(void*d,struct zwp_linux_dmabuf_feedback_v1*f,struct wl_array*a){(void)d;(void)f;if(a->size==sizeof(device_id))memcpy(&device_id,a->data,sizeof(device_id));}
static void tranche_done(void*d,struct zwp_linux_dmabuf_feedback_v1*f){(void)d;(void)f;}
static void tranche_device(void*d,struct zwp_linux_dmabuf_feedback_v1*f,struct wl_array*a){(void)d;(void)f;(void)a;}
static void formats(void*d,struct zwp_linux_dmabuf_feedback_v1*f,struct wl_array*a){(void)d;(void)f;(void)a;}
static void flags(void*d,struct zwp_linux_dmabuf_feedback_v1*f,uint32_t flags){(void)d;(void)f;(void)flags;}
int main(void){
 const char *runtime=getenv("XDG_RUNTIME_DIR"),*display=getenv("WAYLAND_DISPLAY");struct stat st;char prefix[128];
 int length=snprintf(prefix,sizeof(prefix),"/run/user/%u/wqa/",(unsigned)getuid());
 if(length<=0||(size_t)length>=sizeof(prefix)||!runtime||strncmp(runtime,prefix,(size_t)length)||strlen(runtime+length)!=4||strspn(runtime+length,"0123456789abcdef")!=4||lstat(runtime,&st)||!S_ISDIR(st.st_mode)||st.st_uid!=getuid()||(st.st_mode&0777)!=0700||!display||strcmp(display,"weston-host"))return 2;
 struct wl_display *connection=wl_display_connect(NULL);if(!connection)return 3;
 struct wl_registry *registry=wl_display_get_registry(connection);const struct wl_registry_listener listener={global,removed};wl_registry_add_listener(registry,&listener,NULL);
 if(wl_display_roundtrip(connection)<0||!dmabuf)return 4;
 struct zwp_linux_dmabuf_feedback_v1 *feedback=zwp_linux_dmabuf_v1_get_default_feedback(dmabuf);
 const struct zwp_linux_dmabuf_feedback_v1_listener events={done,table,device,tranche_done,tranche_device,formats,flags};zwp_linux_dmabuf_feedback_v1_add_listener(feedback,&events,NULL);
 if(wl_display_roundtrip(connection)<0||!complete||!device_id||!format_bytes)return 5;
 drmDevicePtr actual=NULL;if(drmGetDeviceFromDevId(device_id,0,&actual)||!actual||(actual->available_nodes&(1<<DRM_NODE_RENDER))==0)return 6;
 const char *render=actual->nodes[DRM_NODE_RENDER];if(strncmp(render,"/dev/dri/renderD",16))return 7;
 int fd=open(render,O_RDWR|O_CLOEXEC);if(fd<0)return 8;
 drmVersionPtr version=drmGetVersion(fd);uint64_t prime=0;if(!version||drmGetCap(fd,DRM_CAP_PRIME,&prime))return 9;
 printf("{\"defaultFeedbackComplete\":true,\"feedbackDeviceMajor\":%u,\"feedbackDeviceMinor\":%u,\"formatTableBytes\":%u,\"renderNode\":\"%s\",\"driver\":\"%.*s\",\"primeCaps\":%llu}\n",major(device_id),minor(device_id),format_bytes,render,version->name_len,version->name,(unsigned long long)prime);
 drmFreeVersion(version);close(fd);drmFreeDevice(&actual);zwp_linux_dmabuf_feedback_v1_destroy(feedback);zwp_linux_dmabuf_v1_destroy(dmabuf);wl_registry_destroy(registry);wl_display_disconnect(connection);return 0;
}
