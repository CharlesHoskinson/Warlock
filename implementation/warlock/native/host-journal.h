#include <math.h>
/* Durable admission belongs to the host; authoritative settlement to the broker. */
#include <errno.h>
#include <sys/file.h>
#include <stdlib.h>
#include <stdio.h>
#include <dirent.h>

typedef struct {int directory,lock,instance,owner,entries;char *lifetime;} AdmissionJournal;
static gboolean admission_storage_failed;
static AdmissionJournal admission={-1,-1,-1,-1,-1,NULL};
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
    if (admission.owner>=0) close(admission.owner);
    if (admission.entries>=0) close(admission.entries);
    if (admission.lock>=0) close(admission.lock);
    if (admission.directory>=0) close(admission.directory);
    if(admission.instance>=0)close(admission.instance);
    g_free(admission.lifetime);
    admission=(AdmissionJournal){-1,-1,-1,-1,-1,NULL};
}
static int admission_child(int parent,const char *name) {
    int made=mkdirat(parent,name,0700);
    if(made<0 && errno!=EEXIST)return -1;
    if(made==0 && fsync(parent)<0)return -1;
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
    admission.owner=openat(admission.directory,"host-owner.lock",O_RDWR|O_CREAT|O_NOFOLLOW|O_CLOEXEC,0600);
    admission.lock=openat(admission.directory,"host-writer.lock",O_RDWR|O_CREAT|O_NOFOLLOW|O_CLOEXEC,0600);
    gboolean ok=admission_private(admission.owner,FALSE) && admission_private(admission.lock,FALSE) && flock(admission.owner,LOCK_EX|LOCK_NB)==0;
    if(ok)ok=flock(admission.lock,LOCK_EX|LOCK_NB)==0;
    if(ok){admission.entries=admission_child(admission.directory,"admissions-v1");ok=admission.entries>=0;flock(admission.lock,LOCK_UN);}
    if(!ok){
        if(admission.owner>=0)close(admission.owner);
        if(admission.entries>=0)close(admission.entries);
        if(admission.lock>=0)close(admission.lock);
        close(admission.directory);admission.owner=-1;admission.entries=-1;admission.lock=-1;admission.directory=-1;
        return FALSE;
    }
    admission.lifetime=g_strdup(name);return TRUE;
}
static gboolean admission_positive(JsonObject *object,const char *name) {
    guint64 number;return surface_uint(json_object_get_member(object,name),&number) && number>0;
}
static gboolean admission_placement(JsonObject *intent) {
    JsonNode *node=json_object_get_member(intent,"placement");if(!node || !JSON_NODE_HOLDS_OBJECT(node))return FALSE;
    JsonObject *p=json_node_get_object(node);const char *const fields[]={"region","geometry","monitor","outputOwnershipGeneration","workAreaRevision","workspaceGeneration"};
    if(!surface_fields(p,fields,6))return FALSE;
    JsonNode *name=json_object_get_member(p,"region");if(!surface_text(name,32,FALSE))return FALSE;
    const char *region=json_node_get_string(name);
    if(!g_str_equal(region,"left-half")&&!g_str_equal(region,"right-half")&&!g_str_equal(region,"top-left")&&!g_str_equal(region,"top-right")&&!g_str_equal(region,"bottom-left")&&!g_str_equal(region,"bottom-right"))return FALSE;
    guint64 monitor;if(!surface_uint(json_object_get_member(p,"monitor"),&monitor))return FALSE;
    for(guint i=3;i<6;i++)if(!admission_positive(p,fields[i]))return FALSE;
    JsonNode *rect=json_object_get_member(p,"geometry");if(!rect || !JSON_NODE_HOLDS_ARRAY(rect))return FALSE;
    JsonArray *values=json_node_get_array(rect);if(json_array_get_length(values)!=4)return FALSE;
    for(guint i=0;i<4;i++){
        JsonNode *value=json_array_get_element(values,i);if(!JSON_NODE_HOLDS_VALUE(value))return FALSE;
        GType type=json_node_get_value_type(value);if(type!=G_TYPE_INT64 && type!=G_TYPE_DOUBLE)return FALSE;
        double n=json_node_get_double(value);if(!isfinite(n)||fabs(n)>2147483647.0||(i>=2&&n<=0))return FALSE;
    }
    return TRUE;
}
static gboolean admission_transfer(JsonObject *intent) {
    JsonNode *node=json_object_get_member(intent,"transfer");
    if(!node || !JSON_NODE_HOLDS_OBJECT(node))return FALSE;
    JsonObject *p=json_node_get_object(node);const char *const fields[]={"source","sourceGeneration","destination"};
    guint64 source,destination;
    return surface_fields(p,fields,3) && admission_positive(p,"sourceGeneration")
        && surface_uint(json_object_get_member(p,"source"),&source) && source && source<=G_MAXINT64
        && surface_uint(json_object_get_member(p,"destination"),&destination) && destination && destination<=G_MAXINT64 && source!=destination;
}
static JsonNode *admission_record(JsonNode *request) {
    if (!request || !JSON_NODE_HOLDS_OBJECT(request)) return NULL;
    JsonObject *o=json_node_get_object(request);
    const char *const envelope[]={"protocolVersion","kind","effectProtocol","binding","intent"};
    if (!surface_fields(o,envelope,5)) return NULL;
    JsonNode *pn=json_object_get_member(o,"protocolVersion"),*ep=json_object_get_member(o,"effectProtocol"),*kind=json_object_get_member(o,"kind");
    if (json_node_get_value_type(pn)!=G_TYPE_INT64 || json_node_get_int(pn)!=3 || json_node_get_value_type(ep)!=G_TYPE_INT64 || (json_node_get_int(ep)!=1 && json_node_get_int(ep)!=2) || !surface_text(kind,32,FALSE) || !g_str_equal(json_node_get_string(kind),"window-effect")) return NULL;
    JsonNode *bn=json_object_get_member(o,"binding"),*in=json_object_get_member(o,"intent");
    if (!JSON_NODE_HOLDS_OBJECT(bn) || !JSON_NODE_HOLDS_OBJECT(in)) return NULL;
    JsonObject *b=json_node_get_object(bn),*intent=json_node_get_object(in);
    const char *const bindings[]={"lifetime","session","frontend"},*const intents[]={"request","generation","incarnation","operation","context"},*const contexts[]={"lifetime","epoch","output","revision"};
    JsonNode *operationNode=json_object_get_member(intent,"operation");
    gboolean snap=json_node_get_int(ep)==2 && operationNode && surface_text(operationNode,32,FALSE) && g_str_equal(json_node_get_string(operationNode),"snap");
    gboolean transfer=json_node_get_int(ep)==2 && operationNode && surface_text(operationNode,32,FALSE) && g_str_equal(json_node_get_string(operationNode),"transfer-workspace");
    const char *const transferFields[]={"request","generation","incarnation","operation","context","transfer"};
    const char *const snapFields[]={"request","generation","incarnation","operation","context","placement"};
    if (!surface_fields(b,bindings,3) || !(snap ? surface_fields(intent,snapFields,6)&&admission_placement(intent) : transfer ? surface_fields(intent,transferFields,6)&&admission_transfer(intent) : surface_fields(intent,intents,5))) return NULL;
    for(guint i=0;i<3;i++) if (!admission_positive(b,bindings[i]) || !admission_positive(intent,intents[i])) return NULL;
    JsonNode *cn=json_object_get_member(intent,"context"),*op=json_object_get_member(intent,"operation");
    if (!JSON_NODE_HOLDS_OBJECT(cn) || !surface_text(op,32,FALSE)) return NULL;
    JsonObject *context=json_node_get_object(cn);
    if (!surface_fields(context,contexts,4)) return NULL;
    for(guint i=0;i<4;i++) if (!admission_positive(context,contexts[i])) return NULL;
    const char *operation=json_node_get_string(op);
    gint64 protocol=json_node_get_int(ep);
    gboolean supported=protocol==1 ? (g_str_equal(operation,"minimize") || g_str_equal(operation,"restore") || g_str_equal(operation,"activate")) : (g_str_equal(operation,"maximize") || g_str_equal(operation,"restore-geometry") || g_str_equal(operation,"exit-fullscreen") || g_str_equal(operation,"pin") || g_str_equal(operation,"unpin") || snap || transfer);
    if (!supported ||
        !g_str_equal(json_object_get_string_member(b,"lifetime"),json_object_get_string_member(context,"lifetime")) ||
        !g_str_equal(json_object_get_string_member(b,"frontend"),json_object_get_string_member(context,"epoch"))) return NULL;
    JsonObject *record=json_object_new();json_object_set_int_member(record,"schema",2);json_object_set_int_member(record,"effectProtocol",protocol);json_object_set_member(record,"binding",json_node_copy(bn));json_object_set_member(record,"intent",json_node_copy(in));json_object_set_string_member(record,"status","Pending");
    JsonNode *result=json_node_new(JSON_NODE_OBJECT);json_node_take_object(result,record);return result;
}
/* SHA256 of a fixed array; JSON object member order never enters the key. */
static char *admission_key(JsonNode *record) {
    JsonObject *r=json_node_get_object(record),*b=json_object_get_object_member(r,"binding"),*i=json_object_get_object_member(r,"intent"),*c=json_object_get_object_member(i,"context");
    JsonArray *a=json_array_new();
    const char *const bindings[]={"lifetime","session","frontend"},*const ids[]={"request","generation","incarnation"},*const contexts[]={"lifetime","epoch","output","revision"};
    for(guint n=0;n<3;n++)json_array_add_string_element(a,json_object_get_string_member(b,bindings[n]));
    json_array_add_int_element(a,json_object_get_int_member(r,"effectProtocol"));
    for(guint n=0;n<3;n++)json_array_add_string_element(a,json_object_get_string_member(i,ids[n]));
    json_array_add_string_element(a,json_object_get_string_member(i,"operation"));
    for(guint n=0;n<4;n++)json_array_add_string_element(a,json_object_get_string_member(c,contexts[n]));
    if(g_str_equal(json_object_get_string_member(i,"operation"),"transfer-workspace")){
        JsonObject *p=json_object_get_object_member(i,"transfer");const char *const fields[]={"source","sourceGeneration","destination"};
        for(guint n=0;n<3;n++)json_array_add_string_element(a,json_object_get_string_member(p,fields[n]));
    }
    if(g_str_equal(json_object_get_string_member(i,"operation"),"snap")){
        JsonObject *p=json_object_get_object_member(i,"placement");const char *const fields[]={"region","monitor","outputOwnershipGeneration","workAreaRevision","workspaceGeneration"};
        for(guint n=0;n<5;n++)json_array_add_string_element(a,json_object_get_string_member(p,fields[n]));
        JsonArray *rect=json_object_get_array_member(p,"geometry");
        for(guint n=0;n<4;n++){
            double value=json_array_get_double_element(rect,n);if(value==0)value=0;
            guint64 bits;memcpy(&bits,&value,sizeof(bits));char hex[17];g_snprintf(hex,sizeof(hex),"%016" G_GINT64_MODIFIER "x",bits);
            json_array_add_string_element(a,hex);
        }
    }
    g_autoptr(JsonNode) node=json_node_new(JSON_NODE_ARRAY);json_node_take_array(node,a);
    g_autofree char *raw=json_to_string(node,FALSE);return g_compute_checksum_for_string(G_CHECKSUM_SHA256,raw,-1);
}
static JsonNode *admission_normalize(JsonNode *node,gboolean terminal) {
    if(!node || !JSON_NODE_HOLDS_OBJECT(node))return NULL;
    JsonObject *r=json_node_get_object(node);const char *const fields[]={"schema","effectProtocol","binding","intent","status"};
    if(!surface_fields(r,fields,5))return NULL;
    JsonNode *sn=json_object_get_member(r,"schema"),*st=json_object_get_member(r,"status");
    if(json_node_get_value_type(sn)!=G_TYPE_INT64 || json_node_get_int(sn)!=2 || !surface_text(st,32,FALSE))return NULL;
    const char *status=json_node_get_string(st);
    if(terminal ? (!g_str_equal(status,"Committed") && !g_str_equal(status,"Refused")) : !g_str_equal(status,"Pending"))return NULL;
    JsonObject *request=json_object_new();json_object_set_int_member(request,"protocolVersion",3);json_object_set_string_member(request,"kind","window-effect");
    for(guint n=1;n<4;n++)json_object_set_member(request,fields[n],json_node_copy(json_object_get_member(r,fields[n])));
    g_autoptr(JsonNode) envelope=json_node_new(JSON_NODE_OBJECT);json_node_take_object(envelope,request);
    return admission_record(envelope);
}
typedef struct {GHashTable *keys;gboolean duplicate;} AdmissionJson;
static void admission_json_member(JsonParser *parser,JsonObject *object,const char *member,gpointer data) {
    (void)parser;AdmissionJson *seen=data;char *key=g_strdup_printf("%p:%s",(void *)object,member);
    if(g_hash_table_contains(seen->keys,key)){seen->duplicate=TRUE;g_free(key);}else g_hash_table_add(seen->keys,key);
}
static JsonNode *admission_read_entry(const char *name) {
    int fd=openat(admission.entries,name,O_RDONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC);if(fd<0)return NULL;
    if(!admission_private(fd,FALSE)){close(fd);return NULL;}
    char raw[4097];ssize_t size=read(fd,raw,sizeof(raw));int closed=close(fd);
    if(size<=0 || size>4096 || closed<0)return NULL;
    g_autoptr(JsonParser) parser=json_parser_new();AdmissionJson seen={g_hash_table_new_full(g_str_hash,g_str_equal,g_free,NULL),FALSE};
    gulong handler=g_signal_connect(parser,"object-member",G_CALLBACK(admission_json_member),&seen);
    gboolean ok=json_parser_load_from_data(parser,raw,size,NULL);g_signal_handler_disconnect(parser,handler);g_hash_table_unref(seen.keys);
    if(!ok || seen.duplicate)return NULL;
    JsonNode *record=admission_normalize(json_parser_get_root(parser),FALSE);if(!record)return NULL;
    JsonObject *bound=json_object_get_object_member(json_node_get_object(record),"binding");
    g_autofree char *key=admission_key(record),*expected=g_strconcat(key,".json",NULL);
    if(!g_str_equal(name,expected) || !g_str_equal(json_object_get_string_member(bound,"lifetime"),admission.lifetime)){json_node_unref(record);return NULL;}
    return record;
}
static gboolean admission_scan(JsonNode *candidate,guint *count) {
    int fd=openat(admission.entries,".",O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);if(fd<0)return FALSE;
    DIR *dir=fdopendir(fd);if(!dir){close(fd);return FALSE;}gboolean ok=TRUE;*count=0;
    GHashTable *targets=g_hash_table_new_full(g_str_hash,g_str_equal,g_free,NULL);struct dirent *entry;
    while((entry=readdir(dir))) {
        if(g_str_equal(entry->d_name,".") || g_str_equal(entry->d_name,".."))continue;
        if(g_str_has_prefix(entry->d_name,"host-pending-")) {
            int temporary=openat(admission.entries,entry->d_name,O_RDONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC);
            ok=admission_private(temporary,FALSE);if(temporary>=0)close(temporary);if(!ok)break;continue;
        }
        if(!g_regex_match_simple("^[0-9a-f]{64}\\.json$",entry->d_name,0,0)){ok=FALSE;break;}
        g_autoptr(JsonNode) record=admission_read_entry(entry->d_name);if(!record){ok=FALSE;break;}
        const char *target=json_object_get_string_member(json_object_get_object_member(json_node_get_object(record),"intent"),"incarnation");
        if(g_hash_table_contains(targets,target)){ok=FALSE;break;}g_hash_table_add(targets,g_strdup(target));
        if(candidate && g_str_equal(target,json_object_get_string_member(json_object_get_object_member(json_node_get_object(candidate),"intent"),"incarnation"))){ok=FALSE;break;}
        if(++*count>64){ok=FALSE;break;}
    }
    g_hash_table_unref(targets);closedir(dir);return ok;
}
static gboolean admission_mutation_lock(void) {
    struct stat held,current;
    return admission.directory>=0 && admission.entries>=0 && admission_private(admission.lock,FALSE) && fstat(admission.lock,&held)==0 && fstatat(admission.directory,"host-writer.lock",&current,AT_SYMLINK_NOFOLLOW)==0 && held.st_dev==current.st_dev && held.st_ino==current.st_ino && flock(admission.lock,LOCK_EX|LOCK_NB)==0;
}
/* A workspace has its own typed durable record in the same writer namespace. */
static gboolean workspace_admission_row(JsonObject *row) {
    const char *const fields[]={"identity","generation","monitor","outputOwnershipGeneration"};guint64 id,monitor;
    return row && surface_fields(row,fields,4) && admission_positive(row,"identity") && surface_uint(json_object_get_member(row,"identity"),&id) && id<=G_MAXINT64 && admission_positive(row,"generation") && surface_uint(json_object_get_member(row,"monitor"),&monitor) && admission_positive(row,"outputOwnershipGeneration");
}
static gboolean workspace_admission_record_valid(JsonNode *node) {
    if(!node || !JSON_NODE_HOLDS_OBJECT(node))return FALSE;
    JsonObject *record=json_node_get_object(node);const char *const fields[]={"schema","binding","intent","status","reason"};
    if(!surface_fields(record,fields,5))return FALSE;
    JsonNode *schema=json_object_get_member(record,"schema"),*bn=json_object_get_member(record,"binding"),*in=json_object_get_member(record,"intent"),*status=json_object_get_member(record,"status"),*reason=json_object_get_member(record,"reason");
    if(json_node_get_value_type(schema)!=G_TYPE_INT64 || json_node_get_int(schema)!=1 || !JSON_NODE_HOLDS_OBJECT(bn) || !JSON_NODE_HOLDS_OBJECT(in) || !surface_text(status,16,FALSE) || !surface_text(reason,64,FALSE))return FALSE;
    const char *state=json_node_get_string(status),*text=json_node_get_string(reason);
    if(!g_str_equal(state,"Pending") && !g_str_equal(state,"Unknown") && !g_str_equal(state,"Committed") && !g_str_equal(state,"Refused"))return FALSE;
    if(!*text || *text<'a' || *text>'z')return FALSE;
    for(const char *p=text;*p;p++)if(!(*p>='a'&&*p<='z') && !(*p>='0'&&*p<='9') && *p!='-')return FALSE;
    JsonObject *bound=json_node_get_object(bn),*intent=json_node_get_object(in);const char *const bindings[]={"lifetime","session","frontend"},*const intents[]={"request","generation","source","destination","context"},*const contexts[]={"lifetime","epoch","output","revision"};
    if(!surface_fields(bound,bindings,3) || !surface_fields(intent,intents,5))return FALSE;
    for(guint i=0;i<3;i++)if(!admission_positive(bound,bindings[i]))return FALSE;
    if(!admission_positive(intent,"request") || !admission_positive(intent,"generation"))return FALSE;
    JsonNode *source=json_object_get_member(intent,"source"),*destination=json_object_get_member(intent,"destination"),*cn=json_object_get_member(intent,"context");
    if(!JSON_NODE_HOLDS_OBJECT(source) || !JSON_NODE_HOLDS_OBJECT(destination) || !JSON_NODE_HOLDS_OBJECT(cn) || !workspace_admission_row(json_node_get_object(source)) || !workspace_admission_row(json_node_get_object(destination)))return FALSE;
    JsonObject *context=json_node_get_object(cn);if(!surface_fields(context,contexts,4))return FALSE;
    for(guint i=0;i<4;i++)if(!admission_positive(context,contexts[i]))return FALSE;
    return g_str_equal(json_object_get_string_member(bound,"lifetime"),json_object_get_string_member(context,"lifetime")) && g_str_equal(json_object_get_string_member(bound,"frontend"),json_object_get_string_member(context,"epoch"));
}
static JsonNode *workspace_admission_record(JsonNode *request) {
    if(!request || !JSON_NODE_HOLDS_OBJECT(request))return NULL;
    JsonObject *object=json_node_get_object(request);const char *const fields[]={"protocolVersion","kind","workspaceProtocol","binding","intent"};
    if(!surface_fields(object,fields,5))return NULL;
    JsonNode *pv=json_object_get_member(object,"protocolVersion"),*wp=json_object_get_member(object,"workspaceProtocol"),*kind=json_object_get_member(object,"kind");
    if(json_node_get_value_type(pv)!=G_TYPE_INT64 || json_node_get_int(pv)!=3 || json_node_get_value_type(wp)!=G_TYPE_INT64 || json_node_get_int(wp)!=1 || !surface_text(kind,32,FALSE) || !g_str_equal(json_node_get_string(kind),"workspace-navigation"))return NULL;
    JsonObject *record=json_object_new();json_object_set_int_member(record,"schema",1);json_object_set_member(record,"binding",json_node_copy(json_object_get_member(object,"binding")));json_object_set_member(record,"intent",json_node_copy(json_object_get_member(object,"intent")));json_object_set_string_member(record,"status","Pending");json_object_set_string_member(record,"reason","admitted");
    JsonNode *result=json_node_new(JSON_NODE_OBJECT);json_node_take_object(result,record);
    if(!workspace_admission_record_valid(result)){json_node_unref(result);return NULL;}return result;
}
static JsonNode *workspace_admission_read_file(const char *name,gboolean *missing) {
    *missing=FALSE;int fd=openat(admission.directory,name,O_RDONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC);
    if(fd<0){*missing=errno==ENOENT;return NULL;}
    if(!admission_private(fd,FALSE)){close(fd);return NULL;}
    char raw[4097];ssize_t size=read(fd,raw,sizeof(raw));int closed=close(fd);
    if(size<=0 || size>4096 || closed<0)return NULL;
    g_autoptr(JsonParser) parser=json_parser_new();AdmissionJson seen={g_hash_table_new_full(g_str_hash,g_str_equal,g_free,NULL),FALSE};
    gulong handler=g_signal_connect(parser,"object-member",G_CALLBACK(admission_json_member),&seen);
    gboolean ok=json_parser_load_from_data(parser,raw,size,NULL);g_signal_handler_disconnect(parser,handler);g_hash_table_unref(seen.keys);
    return ok && !seen.duplicate?json_node_copy(json_parser_get_root(parser)):NULL;
}
static gboolean workspace_admission_load(JsonNode **value) {
    gboolean missing=FALSE,marker_missing=FALSE;
    *value=workspace_admission_read_file("workspace-navigation-v1.json",&missing);
    g_autoptr(JsonNode) marker=workspace_admission_read_file("workspace-navigation-v1.initialized",&marker_missing);
    if(missing && marker_missing)return TRUE; /* No navigation has existed. */
    if(!*value || !marker || !JSON_NODE_HOLDS_OBJECT(marker))return FALSE;
    JsonObject *m=json_node_get_object(marker);const char *const mf[]={"schema","lifetime","kind"};
    if(!surface_fields(m,mf,3) || json_node_get_value_type(json_object_get_member(m,"schema"))!=G_TYPE_INT64 || json_object_get_int_member(m,"schema")!=1 || !admission_positive(m,"lifetime") || !surface_text(json_object_get_member(m,"kind"),64,FALSE) || !g_str_equal(json_object_get_string_member(m,"kind"),"workspace-navigation-initialized") || !g_str_equal(json_object_get_string_member(m,"lifetime"),admission.lifetime))return FALSE;
    return JSON_NODE_HOLDS_NULL(*value) || (workspace_admission_record_valid(*value) && g_str_equal(json_object_get_string_member(json_object_get_object_member(json_node_get_object(*value),"binding"),"lifetime"),admission.lifetime));
}
static gboolean workspace_admission_available(void) {
    g_autoptr(JsonNode) value=NULL;if(!workspace_admission_load(&value))return FALSE;
    if(!value || JSON_NODE_HOLDS_NULL(value))return TRUE;
    const char *status=json_object_get_string_member(json_node_get_object(value),"status");return g_str_equal(status,"Committed") || g_str_equal(status,"Refused");
}
static gboolean workspace_admission_write(JsonNode *record) {
    if(!admission_mutation_lock())return FALSE;
    guint count=0;g_autoptr(JsonNode) previous=NULL;gboolean ok=workspace_admission_load(&previous) && workspace_admission_available() && admission_scan(NULL,&count) && count==0;
    if(ok && previous && !JSON_NODE_HOLDS_NULL(previous)){
        JsonObject *old=json_object_get_object_member(json_node_get_object(previous),"intent"),*next=json_object_get_object_member(json_node_get_object(record),"intent");guint64 a,b,c,d;
        ok=surface_uint(json_object_get_member(old,"request"),&a) && surface_uint(json_object_get_member(next,"request"),&b) && surface_uint(json_object_get_member(old,"generation"),&c) && surface_uint(json_object_get_member(next,"generation"),&d) && b>a && d>c;
    }
    g_autofree char *raw=json_to_string(record,FALSE),*uuid=g_uuid_string_random(),*name=g_strconcat("workspace-host-pending-",uuid,NULL);gsize size=strlen(raw),offset=0;int fd=-1;
    if(size>4096)ok=FALSE;
    if(ok){fd=openat(admission.directory,name,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);ok=fd>=0;}
    while(ok && offset<size){ssize_t written=write(fd,raw+offset,size-offset);if(written<0 && errno==EINTR)continue;if(written<=0){ok=FALSE;break;}offset+=(gsize)written;}
    if(ok)ok=fsync(fd)==0;
    if(fd>=0 && close(fd)<0)ok=FALSE;
    if(ok)ok=renameat(admission.directory,name,admission.directory,"workspace-navigation-v1.json")==0;
    if(ok)ok=fsync(admission.directory)==0;
    unlinkat(admission.directory,name,0);flock(admission.lock,LOCK_UN);
    if(ok){g_print("host-workspace-intent-durable: %s\n",raw);fflush(stdout);}return ok;
}
static gboolean admission_write(JsonNode *record) {
    if(!admission_mutation_lock())return FALSE;
    guint count=0;gboolean ok=workspace_admission_available() && admission_scan(record,&count) && count<64;
    g_autofree char *key=admission_key(record),*target=g_strconcat(key,".json",NULL),*raw=json_to_string(record,FALSE),*uuid=g_uuid_string_random(),*name=g_strconcat("host-pending-",uuid,NULL);
    gsize size=strlen(raw),offset=0;int fd=-1;if(size>4096)ok=FALSE;
    if(ok){fd=openat(admission.entries,name,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);ok=fd>=0;}
    while(ok && offset<size){ssize_t written=write(fd,raw+offset,size-offset);if(written<0 && errno==EINTR)continue;if(written<=0){ok=FALSE;break;}offset+=(gsize)written;}
    if(ok)ok=fsync(fd)==0;
    if(fd>=0 && close(fd)<0)ok=FALSE;
    if(ok)ok=renameat(admission.entries,name,admission.entries,target)==0;
    if(ok)ok=fsync(admission.entries)==0;
    unlinkat(admission.entries,name,0);flock(admission.lock,LOCK_UN);
    if(ok){g_print("host-intent-durable: %s\n",raw);fflush(stdout);}return ok;
}
static gboolean admission_retire(JsonNode *terminal) {
    g_autoptr(JsonNode) wanted=admission_normalize(terminal,TRUE);
    if(!wanted || !admission.lifetime || !g_str_equal(json_object_get_string_member(json_object_get_object_member(json_node_get_object(wanted),"binding"),"lifetime"),admission.lifetime) || !admission_mutation_lock())return FALSE;
    g_autofree char *key=admission_key(wanted),*name=g_strconcat(key,".json",NULL);struct stat st;
    gboolean ok=TRUE;
    if(fstatat(admission.entries,name,&st,AT_SYMLINK_NOFOLLOW)<0){ok=errno==ENOENT;}else {
        g_autoptr(JsonNode) stored=admission_read_entry(name);ok=stored && json_node_equal(stored,wanted);
        if(ok)ok=unlinkat(admission.entries,name,0)==0;
    }
    if(ok)ok=fsync(admission.entries)==0;
    flock(admission.lock,LOCK_UN);return ok;
}
static gboolean admission_batch(JsonArray *requests,JsonNode *bound) {
    admission_storage_failed=FALSE;JsonNode *selected=NULL;gboolean workspace=FALSE;
    for(guint i=0;i<json_array_get_length(requests);i++) {
        JsonNode *request=json_array_get_element(requests,i);
        if (!JSON_NODE_HOLDS_OBJECT(request)) continue;
        JsonNode *kind=json_object_get_member(json_node_get_object(request),"kind");
        if(!surface_text(kind,32,FALSE))continue;
        const char *name=json_node_get_string(kind);
        if(!g_str_equal(name,"window-effect") && !g_str_equal(name,"workspace-navigation"))continue;
        if(selected){json_node_unref(selected);return FALSE;}
        workspace=g_str_equal(name,"workspace-navigation");
        selected=workspace?workspace_admission_record(request):admission_record(request);if(!selected)return FALSE;
        JsonNode *record_binding=json_object_get_member(json_node_get_object(selected),"binding");
        if(!bound || !json_node_equal(record_binding,bound)){json_node_unref(selected);return FALSE;}
    }
    if(!selected)return TRUE;
    gboolean ok=workspace?workspace_admission_write(selected):admission_write(selected);admission_storage_failed=!ok;json_node_unref(selected);return ok;
}
