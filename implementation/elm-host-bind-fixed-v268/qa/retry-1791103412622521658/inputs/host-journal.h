/* Durable admission belongs to the host; authoritative settlement to the broker. */
#include <errno.h>
#include <sys/file.h>
#include <stdlib.h>
#include <stdio.h>

typedef struct {int directory,lock,instance;char *lifetime;} AdmissionJournal;
static gboolean admission_storage_failed;
static AdmissionJournal admission={-1,-1,-1,NULL};
static gboolean admission_private(int fd,gboolean directory) {
    struct stat st;
    return fd>=0 && fstat(fd,&st)==0 && st.st_uid==getuid() &&
        (directory?S_ISDIR(st.st_mode):S_ISREG(st.st_mode)) &&
        (st.st_mode&0777)==(directory?0700:0600) && (directory || st.st_nlink==1);
}
static int admission_directory(const char *path) {
    if (!path || path[0]!='/' || !path[1]) return -1;
    int fd=open("/",O_DIRECTORY|O_CLOEXEC);
    g_auto(GStrv) parts=g_strsplit(path+1,"/",-1);
    for (guint i=0;parts[i];i++) {
        if (!*parts[i] || g_str_equal(parts[i],".") || g_str_equal(parts[i],"..")) {close(fd);return -1;}
        int next=openat(fd,parts[i],O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);close(fd);fd=next;
        if (fd<0) return -1;
    }
    return fd;
}
static void admission_close(void) {
    if (admission.lock>=0) close(admission.lock);
    if (admission.directory>=0) close(admission.directory);
    if(admission.instance>=0)close(admission.instance);
    g_free(admission.lifetime);
    admission=(AdmissionJournal){-1,-1,-1,NULL};
}
static int admission_child(int parent,const char *name) {
    if(mkdirat(parent,name,0700)<0 && errno!=EEXIST)return -1;
    int fd=openat(parent,name,O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    if(!admission_private(fd,TRUE)){if(fd>=0)close(fd);return -1;}return fd;
}
static gboolean admission_open(const char *config) {
    g_autofree char *parent=g_path_get_dirname(config),*base=g_path_get_basename(config);
    int dir=admission_directory(parent);if (dir<0) return FALSE;
    int fd=openat(dir,base,O_RDONLY|O_NOFOLLOW|O_CLOEXEC);close(dir);
    if (!admission_private(fd,FALSE)) {if (fd>=0) close(fd);return FALSE;}
    char bytes[65537];ssize_t size=read(fd,bytes,sizeof(bytes));close(fd);
    if (size<=0 || size>65536) return FALSE;
    g_autoptr(JsonParser) parser=json_parser_new();
    if (!json_parser_load_from_data(parser,bytes,size,NULL) || !JSON_NODE_HOLDS_OBJECT(json_parser_get_root(parser))) return FALSE;
    JsonNode *runtime=json_object_get_member(json_node_get_object(json_parser_get_root(parser)),"runtime");
    if (!surface_text(runtime,4096,FALSE)) return FALSE;
    int root=admission_directory(json_node_get_string(runtime));
    if (!admission_private(root,TRUE)) {if(root>=0)close(root);return FALSE;}
    JsonNode *instance=json_object_get_member(json_node_get_object(json_parser_get_root(parser)),"instance");
    if(!surface_text(instance,255,FALSE) || !g_regex_match_simple("^[A-Za-z0-9_]{1,255}$",json_node_get_string(instance),0,0)){close(root);return FALSE;}
    int recovery_root=admission_child(root,"elm-window-recovery");close(root);if(recovery_root<0)return FALSE;
    admission.instance=admission_child(recovery_root,json_node_get_string(instance));close(recovery_root);
    return admission.instance>=0;
}
static gboolean admission_bind(JsonNode *bound) {
    if(!bound || !JSON_NODE_HOLDS_OBJECT(bound) || admission.instance<0)return FALSE;
    JsonNode *life=json_object_get_member(json_node_get_object(bound),"lifetime");guint64 number;
    if(!surface_uint(life,&number) || !number)return FALSE;
    const char *name=json_node_get_string(life);
    if(admission.directory>=0)return g_str_equal(name,admission.lifetime);
    admission.directory=admission_child(admission.instance,name);if(admission.directory<0)return FALSE;
    admission.lock=openat(admission.directory,"host-writer.lock",O_RDWR|O_CREAT|O_NOFOLLOW|O_CLOEXEC,0600);
    if(!admission_private(admission.lock,FALSE) || flock(admission.lock,LOCK_EX|LOCK_NB)<0){
        /* A rejected lifetime binding must leave the verified instance available
         * for explicit retry. Final host teardown owns admission_close(). */
        if(admission.lock>=0)close(admission.lock);
        close(admission.directory);admission.lock=-1;admission.directory=-1;
        return FALSE;
    }
    admission.lifetime=g_strdup(name);return TRUE;
}
static gboolean admission_positive(JsonObject *object,const char *name) {
    guint64 number;return surface_uint(json_object_get_member(object,name),&number) && number>0;
}
static JsonNode *admission_record(JsonNode *request) {
    if (!request || !JSON_NODE_HOLDS_OBJECT(request)) return NULL;
    JsonObject *o=json_node_get_object(request);
    const char *const envelope[]={"protocolVersion","kind","effectProtocol","binding","intent"};
    if (!surface_fields(o,envelope,5)) return NULL;
    JsonNode *pn=json_object_get_member(o,"protocolVersion"),*ep=json_object_get_member(o,"effectProtocol"),*kind=json_object_get_member(o,"kind");
    if (json_node_get_value_type(pn)!=G_TYPE_INT64 || json_node_get_int(pn)!=3 || json_node_get_value_type(ep)!=G_TYPE_INT64 || json_node_get_int(ep)!=1 || !surface_text(kind,32,FALSE) || !g_str_equal(json_node_get_string(kind),"window-effect")) return NULL;
    JsonNode *bn=json_object_get_member(o,"binding"),*in=json_object_get_member(o,"intent");
    if (!JSON_NODE_HOLDS_OBJECT(bn) || !JSON_NODE_HOLDS_OBJECT(in)) return NULL;
    JsonObject *b=json_node_get_object(bn),*intent=json_node_get_object(in);
    const char *const bindings[]={"lifetime","session","frontend"},*const intents[]={"request","generation","incarnation","operation","context"},*const contexts[]={"lifetime","epoch","output","revision"};
    if (!surface_fields(b,bindings,3) || !surface_fields(intent,intents,5)) return NULL;
    for(guint i=0;i<3;i++) if (!admission_positive(b,bindings[i]) || !admission_positive(intent,intents[i])) return NULL;
    JsonNode *cn=json_object_get_member(intent,"context"),*op=json_object_get_member(intent,"operation");
    if (!JSON_NODE_HOLDS_OBJECT(cn) || !surface_text(op,32,FALSE)) return NULL;
    JsonObject *context=json_node_get_object(cn);
    if (!surface_fields(context,contexts,4)) return NULL;
    for(guint i=0;i<4;i++) if (!admission_positive(context,contexts[i])) return NULL;
    const char *operation=json_node_get_string(op);
    if ((!g_str_equal(operation,"minimize") && !g_str_equal(operation,"restore") && !g_str_equal(operation,"activate")) ||
        !g_str_equal(json_object_get_string_member(b,"lifetime"),json_object_get_string_member(context,"lifetime")) ||
        !g_str_equal(json_object_get_string_member(b,"frontend"),json_object_get_string_member(context,"epoch"))) return NULL;
    JsonObject *record=json_object_new();json_object_set_int_member(record,"schema",1);json_object_set_member(record,"binding",json_node_copy(bn));json_object_set_member(record,"intent",json_node_copy(in));json_object_set_string_member(record,"status","Pending");
    JsonNode *result=json_node_new(JSON_NODE_OBJECT);json_node_take_object(result,record);return result;
}
static gboolean admission_write(JsonNode *record) {
    if (admission.directory<0) return FALSE;
    struct stat st;
    if (fstatat(admission.directory,"host-intent.json",&st,AT_SYMLINK_NOFOLLOW)==0) {
        if (!S_ISREG(st.st_mode) || st.st_uid!=getuid() || (st.st_mode&0777)!=0600 || st.st_nlink!=1) return FALSE;
    } else if (errno!=ENOENT) return FALSE;
    g_autofree char *raw=json_to_string(record,FALSE),*uuid=g_uuid_string_random(),*name=g_strconcat("host-pending-",uuid,NULL);
    gsize size=strlen(raw),offset=0;if (size>4096) return FALSE;
    int fd=openat(admission.directory,name,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);if(fd<0)return FALSE;
    gboolean ok=TRUE;
    while(offset<size) {ssize_t count=write(fd,raw+offset,size-offset);if(count<0 && errno==EINTR)continue;if(count<=0){ok=FALSE;break;}offset+=(gsize)count;}
    if(ok)ok=fsync(fd)==0;
    if(close(fd)<0)ok=FALSE;
    if(ok)ok=renameat(admission.directory,name,admission.directory,"host-intent.json")==0;
    if(ok)ok=fsync(admission.directory)==0;
    unlinkat(admission.directory,name,0);
    if(ok){g_print("host-intent-durable: %s\n",raw);fflush(stdout);}
    return ok;
}
static gboolean admission_batch(JsonArray *requests,JsonNode *bound) {
    admission_storage_failed=FALSE;JsonNode *selected=NULL;
    for(guint i=0;i<json_array_get_length(requests);i++) {
        JsonNode *request=json_array_get_element(requests,i);
        if (!JSON_NODE_HOLDS_OBJECT(request)) continue;
        JsonNode *kind=json_object_get_member(json_node_get_object(request),"kind");
        if(!surface_text(kind,32,FALSE) || !g_str_equal(json_node_get_string(kind),"window-effect"))continue;
        if(selected){json_node_unref(selected);return FALSE;}
        selected=admission_record(request);if(!selected)return FALSE;
        JsonNode *record_binding=json_object_get_member(json_node_get_object(selected),"binding");
        if(!bound || !json_node_equal(record_binding,bound)){json_node_unref(selected);return FALSE;}
    }
    if(!selected)return TRUE;
    gboolean ok=admission_write(selected);admission_storage_failed=!ok;json_node_unref(selected);return ok;
}
