/* Exercise the actual private controller-delay boundary without GTK surfaces. */
#define G_DISABLE_CAST_CHECKS
#define ELM_SHARED_HOST_MAIN archived_shared_main
#include "/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v48/native/shared-host.c"
static guint checks;
#define CHECK(name,expr) do{checks++;if(!(expr)){g_printerr("failed %u: %s\n",checks,name);return 1;}}while(0)
int main(int argc,char **argv) {
    g_test_init(&argc,&argv,NULL);
    OutputView one={.id=1,.generation=1,.active=TRUE};output_views=g_ptr_array_new();g_ptr_array_add(output_views,&one);issued_view=1;topology_revision=1;
    authority_binding=test_json("{}");surface_gate=(SurfaceGate){10,1,0};
    JsonNode *root=test_json("{\"viewProtocol\":1,\"kind\":\"view-commit\",\"projection\":{\"viewProtocol\":1,\"kind\":\"view-frame\",\"revision\":\"1\",\"views\":[{\"id\":\"1\",\"generation\":\"1\"}],\"popupOwner\":null,\"focusOwner\":{\"id\":\"1\",\"generation\":\"1\"},\"frame\":{\"surfaceProtocol\":2,\"publication\":\"11\",\"lease\":\"1\",\"mode\":\"closed\",\"status\":\"Ready\",\"bar\":[],\"popup\":[]}},\"requests\":[],\"focus\":[]}");
    g_autofree char *wire=json_to_string(root,FALSE);
    CHECK("ordinary delivery never delayed",!qa_delay_controller_commit(root,wire));
    qa_icon_reader_path="explicit-private";
    CHECK("private flag without held own job never delays",!qa_delay_controller_commit(root,wire));qa_held_icon_request=1;
    CHECK("strict packet accepted into private FIFO",qa_delay_controller_commit(root,wire));
    CHECK("exact one retained packet",g_queue_get_length(&qa_controller_commits)==1);
    QAControllerCommit *row=g_queue_peek_head(&qa_controller_commits);
    CHECK("original bytes retained",g_str_equal(row->wire,wire));CHECK("original node independently retained",row->root!=root && json_node_equal(row->root,root));
    CHECK("no surface admission fabricated",surface_gate.publication==10 && surface_snapshot==NULL);
    CHECK("no output batch certificate fabricated",g_queue_is_empty(&shared_batches));
    CHECK("no transport effect dispatched",g_queue_is_empty(&requests));
    client_concealed_written=TRUE;CHECK("actual completed concealment disables hold",!qa_delay_controller_commit(root,wire));client_concealed_written=FALSE;
    JsonNode *bad=json_node_copy(root);json_object_set_string_member(json_node_get_object(bad),"extra","execute");CHECK("extra fields refused",!qa_delay_controller_commit(bad,wire));json_node_unref(bad);
    bad=json_node_copy(root);json_object_set_boolean_member(json_node_get_object(bad),"viewProtocol",TRUE);CHECK("Boolean protocol refused",!qa_delay_controller_commit(bad,wire));json_node_unref(bad);
    bad=json_node_copy(root);json_object_set_string_member(json_node_get_object(bad),"kind","execute");CHECK("foreign kind refused",!qa_delay_controller_commit(bad,wire));json_node_unref(bad);
    g_autofree char *large=g_strnfill(131073,'x');CHECK("oversized original bytes refused",!qa_delay_controller_commit(root,large));
    bad=json_node_copy(root);JsonArray *effects=json_object_get_array_member(json_node_get_object(bad),"requests");json_array_add_element(effects,test_json("{\"protocolVersion\":3,\"kind\":\"projection-request\",\"binding\":{\"foreign\":true},\"requestId\":\"1\"}"));CHECK("foreign effect binding refused",!qa_delay_controller_commit(bad,wire));json_node_unref(bad);
    CHECK("invalid traffic did not consume FIFO capacity",g_queue_get_length(&qa_controller_commits)==1);
    CHECK("second original retained",qa_delay_controller_commit(root,wire));CHECK("third original retained",qa_delay_controller_commit(root,wire));CHECK("fourth original retained",qa_delay_controller_commit(root,wire));
    g_test_expect_message("Gtk",G_LOG_LEVEL_CRITICAL,"*gtk_main_quit*main_loops*NULL*");
    CHECK("fifth packet fails qualification",qa_delay_controller_commit(root,wire));g_test_assert_expected_messages();
    CHECK("failure keeps original four packets",failed && g_queue_get_length(&qa_controller_commits)==4);
    CHECK("failure keeps original authority and effect owners",surface_gate.publication==10 && g_queue_is_empty(&requests) && g_queue_is_empty(&shared_batches));
    g_queue_clear_full(&qa_controller_commits,(GDestroyNotify)qa_controller_commit_free);json_node_unref(root);json_node_unref(authority_binding);authority_binding=NULL;g_ptr_array_unref(output_views);
    g_print("controller-delay-result: {\"passed\":true,\"checks\":%u,\"nativeAcceptance\":false}\n",checks);return 0;
}
