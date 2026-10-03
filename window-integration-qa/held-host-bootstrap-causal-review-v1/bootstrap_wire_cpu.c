#define _GNU_SOURCE
#include <wayland-client.h>
#include <sys/socket.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <assert.h>
static void queued_positive(void){
 int pair[2];assert(socketpair(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0,pair)==0);
 struct wl_display *display=wl_display_connect_to_fd(pair[0]);assert(display);
 struct wl_registry *registry=wl_display_get_registry(display);assert(registry);
 // The peer intentionally implements no server: this is only real client-side
 // marshalling/flush, on owned FDs, never a desktop/display/surface connection.
 struct wl_compositor *compositor=wl_registry_bind(registry,1,&wl_compositor_interface,6);assert(compositor);
 struct wl_surface *surface=wl_compositor_create_surface(compositor);assert(surface);
 wl_surface_attach(surface,NULL,0,0);wl_surface_commit(surface);
 struct pollfd server={.fd=pair[1],.events=POLLIN},client={.fd=wl_display_get_fd(display),.events=POLLIN};
 int server_before=poll(&server,1,0),client_before=poll(&client,1,0);assert(server_before==0&&client_before==0);
 errno=0;int flushed=wl_display_flush(display),flush_errno=errno;assert(flushed>0);assert(poll(&server,1,0)==1);
 unsigned char wire[4096];ssize_t n=recv(pair[1],wire,sizeof(wire),MSG_DONTWAIT);assert(n==flushed);
 size_t at=0,count=0;uint32_t last_object=0,last_opcode=0;while(at<(size_t)n){uint32_t object,word;memcpy(&object,wire+at,4);memcpy(&word,wire+at+4,4);size_t size=word>>16;assert(size>=8&&size%4==0&&at+size<=(size_t)n);last_object=object;last_opcode=word&65535;at+=size;count++;}
 assert(at==(size_t)n&&count==5&&last_object==wl_proxy_get_id((struct wl_proxy*)surface)&&last_opcode==6);
 printf("{\"case\":\"real-initial-null-surface-commit-queue\",\"serverReadableBeforeFlush\":%d,\"clientReadableBeforeFlush\":%d,\"flushReturn\":%d,\"flushErrno\":%d,\"wireBytes\":%zd,\"messages\":%zu,\"lastSurfaceObject\":%u,\"lastOpcode\":%u,\"wireHex\":\"",server_before,client_before,flushed,flush_errno,n,count,last_object,last_opcode);
 for(ssize_t i=0;i<n;i++){printf("%02x",wire[i]);}
 puts("\",\"noServerImplemented\":true,\"noNativeGUI\":true}");
 wl_proxy_destroy((struct wl_proxy*)surface);wl_proxy_destroy((struct wl_proxy*)compositor);wl_proxy_destroy((struct wl_proxy*)registry);wl_display_disconnect(display);close(pair[1]);
}
static void full_socket(void){
 int pair[2],buffer=4096;assert(socketpair(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0,pair)==0);assert(setsockopt(pair[0],SOL_SOCKET,SO_SNDBUF,&buffer,sizeof(buffer))==0);
 struct wl_display *display=wl_display_connect_to_fd(pair[0]);assert(display);char bytes[4096]={0};size_t filled=0;for(;;){ssize_t n=send(pair[0],bytes,sizeof(bytes),MSG_DONTWAIT|MSG_NOSIGNAL);if(n<0){assert(errno==EAGAIN||errno==EWOULDBLOCK);break;}filled+=n;assert(filled<1048576);}
 struct wl_registry *registry=wl_display_get_registry(display);assert(registry);errno=0;int result=wl_display_flush(display),error=errno;assert(result==-1&&error==EAGAIN);
 printf("{\"case\":\"real-full-owned-socket-flush-refusal\",\"filledBytes\":%zu,\"flushReturn\":%d,\"flushErrno\":%d,\"noNativeGUI\":true}\n",filled,result,error);
 wl_proxy_destroy((struct wl_proxy*)registry);wl_display_disconnect(display);close(pair[1]);
}
static void closed_peer(void){
 int pair[2];assert(socketpair(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0,pair)==0);struct wl_display *display=wl_display_connect_to_fd(pair[0]);assert(display);struct wl_registry *registry=wl_display_get_registry(display);assert(registry);close(pair[1]);errno=0;int result=wl_display_flush(display),error=errno;assert(result==-1&&error==EPIPE);
 printf("{\"case\":\"real-closed-owned-peer-flush-refusal\",\"flushReturn\":%d,\"flushErrno\":%d,\"noNativeGUI\":true}\n",result,error);wl_proxy_destroy((struct wl_proxy*)registry);wl_display_disconnect(display);
}
int main(void){queued_positive();full_socket();closed_peer();return 0;}
