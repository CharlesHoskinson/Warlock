#define ELM_SHARED_HOST_MAIN warlock_qa_unused_shared_main
#include "../native/shared-host.c"

/* Exercise the actual host queue/flush against the real persistent C/JSC driver.
 * No GTK/WebKit function is invoked by this bounded CPU fixture. */
gboolean warlock_qa_host_input_pressure(WarlockPolicyDriver *driver,guint64 epoch,const char *snapshot,char **result,GError **error) {
    if(result)*result=NULL;
    if(!driver || !epoch || !snapshot || !result || controlled_driver || !g_queue_is_empty(&controlled_pending))return FALSE;
    controlled_driver=driver;controlled_epoch=epoch;qa_controlled_preview=TRUE;
    controlled_queue(g_strdup(snapshot),TRUE);
    ControlledInput *original=g_queue_peek_head(&controlled_pending);char *exact=original->wire;
    GError *pressure=NULL;
    gboolean admitted=controlled_flush(&pressure);
    gboolean retained=!admitted && pressure && g_error_matches(pressure,G_IO_ERROR,G_IO_ERROR_WOULD_BLOCK) &&
        g_queue_get_length(&controlled_pending)==1 && g_queue_peek_head(&controlled_pending)==original && original->wire==exact && g_str_equal(exact,snapshot) && controlled_pending_bytes==strlen(snapshot);
    g_clear_error(&pressure);
    if(!retained)goto fail;
    gboolean progressed=FALSE;
    if(!warlock_policy_driver_step(driver,&progressed,error) || !progressed)goto fail;
    if(!controlled_flush(error) || !g_queue_is_empty(&controlled_pending) || controlled_pending_bytes)goto fail;
    *result=g_strdup("{\"retainedExactInput\":true,\"wouldBlock\":true,\"driverProgressWhileProducerPaused\":true,\"admittedOriginalInputAfterProgress\":true,\"hostQueueDrained\":true,\"nativeGrantResets\":0,\"actualGUI\":false}");
    controlled_driver=NULL;controlled_epoch=0;qa_controlled_preview=FALSE;return TRUE;
fail:
    /* Preserve failed live custody; the labeled fixture makes no normal-close claim. */
    if(error && !*error)g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Original controlled host input pressure oracle failed");
    return FALSE;
}
