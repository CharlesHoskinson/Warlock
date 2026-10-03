#define _GNU_SOURCE
#include "physical_plan.h"
#include "virtual-keyboard-client.h"
#include <wayland-client.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <limits.h>
static struct wl_display*display;
static struct wl_registry*registry;
static struct wl_seat*seat;
static struct zwp_virtual_keyboard_manager_v1*manager;
static unsigned seats,managers;
static uint32_t seat_name,manager_name;
static bool globals_lost;
static char expected_cgroup[4096];
static struct stat socket_before,runtime_before;
static pid_t expected_pid;
static char expected_start[32],socket_path[PATH_MAX],runtime_path[PATH_MAX];
static void global(void*data,struct wl_registry*r,uint32_t name,const char*interface,uint32_t version){
 (void)data;
 if(!strcmp(interface,"wl_seat")){++seats;if(version<1)globals_lost=true;else if(seats==1){seat_name=name;seat=wl_registry_bind(r,name,&wl_seat_interface,1);}}
 if(!strcmp(interface,"zwp_virtual_keyboard_manager_v1")){++managers;if(version<1)globals_lost=true;else if(managers==1){manager_name=name;manager=wl_registry_bind(r,name,&zwp_virtual_keyboard_manager_v1_interface,1);}}
}
static void removed(void*data,struct wl_registry*r,uint32_t name){(void)data;(void)r;if(name==seat_name||name==manager_name)globals_lost=true;}
static const struct wl_registry_listener listener={global,removed};
static int exact_decimal(const char*s){if(!s||!*s||*s=='0')return 0;for(size_t i=0;s[i];++i)if(!isdigit((unsigned char)s[i]))return 0;return 1;}
static int scope_live(void){
 char self[4096],peer[4096],path[64];const char*paths[2]={"/proc/self/cgroup",path};snprintf(path,sizeof(path),"/proc/%d/cgroup",expected_pid);
 for(int i=0;i<2;++i){FILE*f=fopen(paths[i],"r");if(!f)return -1;char*out=i?peer:self;size_t n=fread(out,1,4095,f);int extra=fgetc(f);int bad=ferror(f);fclose(f);if(bad||extra!=EOF||!n)return -1;out[n]=0;}
 const char*marker=strstr(self,"/qa-harness.slice/qa-harness-");if(!marker||strcmp(self,peer))return -1;const char*end=marker+strlen("/qa-harness.slice/qa-harness-");const char*first=end;while(isalnum((unsigned char)*end)||*end=='_'||*end=='-')++end;
 if(end==first||strncmp(end,".scope",6)||(end[6]!='\n'&&end[6]!=0))return -1;
 if(!expected_cgroup[0]){strcpy(expected_cgroup,self);}
 return strcmp(expected_cgroup,self)?-1:0;
}
static int process_live(void){
 char path[64],raw[8192];struct stat st;if(snprintf(path,sizeof(path),"/proc/%d",expected_pid)<0||stat(path,&st)||st.st_uid!=getuid())return -1;
 snprintf(path,sizeof(path),"/proc/%d/stat",expected_pid);FILE*f=fopen(path,"r");if(!f)return -1;if(!fgets(raw,sizeof(raw),f)){fclose(f);return -1;}fclose(f);char*end=strrchr(raw,')');if(!end)return -1;char*save=NULL;char*field=strtok_r(end+2," ",&save);for(int i=0;i<19&&field;++i)field=strtok_r(NULL," ",&save);if(!field||strcmp(field,expected_start))return -1;return 0;
}
static int guarded(void){
 if(scope_live())return -1;
 struct stat st;char resolved[PATH_MAX];if(process_live()||!realpath(runtime_path,resolved)||strcmp(runtime_path,resolved)||lstat(runtime_path,&st)||!S_ISDIR(st.st_mode)||st.st_uid!=getuid()||(st.st_mode&07777)!=0700||st.st_dev!=runtime_before.st_dev||st.st_ino!=runtime_before.st_ino)return -1;
 if(lstat(socket_path,&st)||!S_ISSOCK(st.st_mode)||st.st_uid!=getuid()||st.st_dev!=socket_before.st_dev||st.st_ino!=socket_before.st_ino){return -1;}
 return 0;
}
static int connect_private(void){
 const char*pid=getenv("WINDOW_QA_COMPOSITOR_PID"),*start=getenv("WINDOW_QA_COMPOSITOR_START"),*runtime=getenv("XDG_RUNTIME_DIR"),*wayland=getenv("WAYLAND_DISPLAY"),*signature=getenv("HYPRLAND_INSTANCE_SIGNATURE");
 if(!exact_decimal(pid)||!exact_decimal(start)||strlen(start)>=sizeof(expected_start)||!runtime||runtime[0]!='/'||strlen(runtime)>=sizeof(runtime_path)||!wayland||strncmp(wayland,"wayland-",8)||!signature||!*signature||getenv("WAYLAND_SOCKET")||getenv("DISPLAY"))return -1;
 for(size_t i=8;wayland[i];++i){if(!isdigit((unsigned char)wayland[i]))return -1;}
 if(!wayland[8])return -1;
 for(size_t i=0;signature[i];++i)if(!isalnum((unsigned char)signature[i])&&signature[i]!='_')return -1;
 errno=0;char*tail=NULL;long number=strtol(pid,&tail,10);if(errno||*tail||number<=0||number>INT_MAX)return -1;expected_pid=(pid_t)number;strcpy(expected_start,start);strcpy(runtime_path,runtime);
 if(snprintf(socket_path,sizeof(socket_path),"%s/%s",runtime,wayland)<0||strlen(socket_path)>=sizeof(((struct sockaddr_un*)0)->sun_path))return -1;
 if(lstat(runtime_path,&runtime_before)||lstat(socket_path,&socket_before)||guarded())return -1;
 int fd=socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0);if(fd<0)return -1;struct sockaddr_un address={.sun_family=AF_UNIX};strcpy(address.sun_path,socket_path);
 if(connect(fd,(struct sockaddr*)&address,sizeof(address))){close(fd);return -1;}struct ucred cred;socklen_t size=sizeof(cred);if(getsockopt(fd,SOL_SOCKET,SO_PEERCRED,&cred,&size)||size!=sizeof(cred)||cred.pid!=expected_pid||cred.uid!=getuid()||guarded()){close(fd);return -1;}
 display=wl_display_connect_to_fd(fd);if(!display){close(fd);return -1;}return 0;
}
static int sync_private(void){return guarded()||wl_display_roundtrip(display)<0||guarded()||globals_lost||seats!=1||managers!=1?-1:0;}
int main(int argc,char**argv){
 struct physical_plan plan;if(make_physical_plan(argc,argv,&plan)){destroy_physical_plan(&plan);fprintf(stderr,"Exact whole physical plan refused before connection/input\n");return 2;}
 if(plan.cpu_only){print_physical_plan(&plan);putchar('\n');destroy_physical_plan(&plan);return 0;}
 int result=3;struct zwp_virtual_keyboard_v1*keyboard=NULL;size_t pairs=0;bool held=false;
 if(connect_private())goto done;
 registry=wl_display_get_registry(display);if(!registry||wl_registry_add_listener(registry,&listener,NULL)||wl_display_roundtrip(display)<0||guarded()||globals_lost||seats!=1||managers!=1)goto done;
 keyboard=zwp_virtual_keyboard_manager_v1_create_virtual_keyboard(manager,seat);if(!keyboard)goto done;
 int mapfd=memfd_create("qa-physical-us-keymap",MFD_CLOEXEC|MFD_ALLOW_SEALING);if(mapfd<0)goto done;size_t size=physical_map_size();
 if(write(mapfd,physical_map_bytes(),size)!=(ssize_t)size||fcntl(mapfd,F_ADD_SEALS,F_SEAL_WRITE|F_SEAL_SHRINK|F_SEAL_GROW|F_SEAL_SEAL)<0){close(mapfd);goto done;}
 zwp_virtual_keyboard_v1_keymap(keyboard,WL_KEYBOARD_KEYMAP_FORMAT_XKB_V1,mapfd,(uint32_t)size);close(mapfd);if(sync_private())goto done;
 for(size_t i=0;i<plan.count;++i){
  if(guarded())goto done;
  zwp_virtual_keyboard_v1_key(keyboard,0,plan.keys[i].wire,WL_KEYBOARD_KEY_STATE_PRESSED);held=true;if(sync_private())goto done;
  usleep(2000);if(guarded())goto done;
  zwp_virtual_keyboard_v1_key(keyboard,0,plan.keys[i].wire,WL_KEYBOARD_KEY_STATE_RELEASED);held=false;if(sync_private())goto done;++pairs;usleep(2000);usleep(20000);
 }
 if(guarded())goto done;
 zwp_virtual_keyboard_v1_destroy(keyboard);keyboard=NULL;if(sync_private())goto done;result=0;
 done:
 if(result)fprintf(stderr,"Physical keyboard failed: completedPairs=%zu heldAtFailure=%s noRetry=true\n",pairs,held?"true":"false");
 // On failure no further protocol requests: disconnect destroys the owned virtual device.
 if(keyboard)wl_proxy_destroy((struct wl_proxy*)keyboard);
 if(manager)wl_proxy_destroy((struct wl_proxy*)manager);
 if(seat)wl_proxy_destroy((struct wl_proxy*)seat);
 if(registry)wl_registry_destroy(registry);
 if(display)wl_display_disconnect(display);
 if(!result){printf("{\"normalDestroyed\":true,\"pairCount\":%zu,\"extraKeys\":0,\"peerPID\":%d,\"planEvidence\":",pairs,expected_pid);print_physical_plan(&plan);puts("}");}
 destroy_physical_plan(&plan);return result;
}
