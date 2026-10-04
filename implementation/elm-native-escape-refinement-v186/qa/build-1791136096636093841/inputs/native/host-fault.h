/* One-shot protected QA can interrupt admission-to-broker delivery precisely. */
#include <sys/resource.h>
static gboolean host_fault_held;
static gboolean host_fault_hold(GSubprocess *child,const char *request) {
    if(host_fault_held)return TRUE;
    if(!qa_exit || g_strcmp0(g_getenv("ELM_WINDOW_RECOVERY_FAULT"),"before-effect-write")!=0)return FALSE;
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!json_parser_load_from_data(parser,request,-1,NULL) || !JSON_NODE_HOLDS_OBJECT(json_parser_get_root(parser)))return FALSE;
    JsonNode *root=json_parser_get_root(parser);JsonNode *kind=json_object_get_member(json_node_get_object(root),"kind");
    if(!surface_text(kind,32,FALSE) || !g_str_equal(json_node_get_string(kind),"window-effect"))return FALSE;
    struct rlimit limit;g_autofree char *group=NULL;
    if(getrlimit(RLIMIT_CORE,&limit)!=0 || limit.rlim_cur!=1 || limit.rlim_max!=1 || !g_file_get_contents("/proc/self/cgroup",&group,NULL,NULL) || !g_regex_match_simple("/qa-harness\\.slice/qa-harness-[A-Za-z0-9_-]+\\.scope",group,0,0))return TRUE;
    int arm=openat(admission.directory,"host-before-write-arm",O_RDONLY|O_NOFOLLOW|O_CLOEXEC);
    if(arm<0)return errno==ENOENT?FALSE:TRUE;
    char text[32];ssize_t count=read(arm,text,sizeof(text));gboolean armed=admission_private(arm,FALSE) && count==20 && memcmp(text,"before-effect-write\n",20)==0;close(arm);
    if(!armed)return TRUE;
    int marker=openat(admission.directory,"host-before-write-marker.json",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
    if(marker<0)return errno==EEXIST?FALSE:TRUE;
    JsonObject *o=json_object_new();json_object_set_int_member(o,"hostPID",getpid());json_object_set_string_member(o,"brokerPID",g_subprocess_get_identifier(child));json_object_set_string_member(o,"stage","after-durable-admission-and-publication-before-broker-write");json_object_set_member(o,"request",json_node_copy(root));
    g_autoptr(JsonNode) node=json_node_new(JSON_NODE_OBJECT);json_node_take_object(node,o);g_autofree char *raw=json_to_string(node,FALSE);
    gsize size=strlen(raw),offset=0;gboolean ok=TRUE;
    while(offset<size){ssize_t wrote=write(marker,raw+offset,size-offset);if(wrote<0 && errno==EINTR)continue;if(wrote<=0){ok=FALSE;break;}offset+=(gsize)wrote;}
    if(ok)ok=fsync(marker)==0;
    if(close(marker)<0)ok=FALSE;
    if(ok)ok=fsync(admission.directory)==0;
    host_fault_held=TRUE;g_print("host-before-write-held: durable-marker=%d\n",ok);fflush(stdout);return TRUE;
}
