#include "context-keys.h"
static guint context_key_bit(guint key) {
    switch (key) {
        case GDK_KEY_Menu:return 1;case GDK_KEY_F10:return 2;case GDK_KEY_Escape:return 4;
        case GDK_KEY_Up:return 8;case GDK_KEY_Down:return 16;case GDK_KEY_Home:return 32;
        case GDK_KEY_End:return 64;case GDK_KEY_Return:return 128;default:return 0;
    }
}
static gboolean context_event(GtkWidget *widget,GdkEvent *event,gpointer unused) {
    (void)unused;
    if (context_epoch==G_MAXUINT64) return FALSE;
    if (event->any.send_event) {context_proof.available=FALSE;context_proof.pressed=FALSE;return FALSE;}
    // WebKit asynchronously replays unhandled keys through GTK. A replay must
    // neither overwrite a newer physical proof nor clear its held-key state.
    if ((event->type==GDK_KEY_PRESS || event->type==GDK_KEY_RELEASE)
        && !context_key_admit(widget,(GdkEventKey *)event)) return FALSE;
    if (event->type==GDK_BUTTON_PRESS || event->type==GDK_KEY_PRESS || event->type==GDK_SCROLL || event->type==GDK_FOCUS_CHANGE || event->type==GDK_GRAB_BROKEN) context_epoch++;
    double zoom=webkit_web_view_get_zoom_level(WEBKIT_WEB_VIEW(widget));
    if (zoom<=0) return FALSE;
    guint forbidden=GDK_CONTROL_MASK|GDK_MOD1_MASK|GDK_SUPER_MASK|GDK_META_MASK;
    if (event->type==GDK_BUTTON_PRESS) {
        GdkEventButton *button=(GdkEventButton *)event;
        context_proof=(ContextProof){.source=widget,.epoch=context_epoch,.publication=surface_gate.publication,.lease=surface_gate.lease,
            .captured=g_get_monotonic_time(),.pointer=TRUE,.px=button->x/zoom,.py=button->y/zoom};
        context_proof.pressed=button->button==3 && !(button->state&(GDK_BUTTON1_MASK|GDK_BUTTON2_MASK|GDK_BUTTON4_MASK|GDK_BUTTON5_MASK));
    } else if (event->type==GDK_MOTION_NOTIFY && context_proof.pressed) {
        GdkEventMotion *motion=(GdkEventMotion *)event;
        double dx=motion->x/zoom-context_proof.px,dy=motion->y/zoom-context_proof.py;
        if (widget!=context_proof.source || dx*dx+dy*dy>25) context_proof.pressed=FALSE;
    } else if (event->type==GDK_BUTTON_RELEASE) {
        GdkEventButton *button=(GdkEventButton *)event;
        double dx=button->x/zoom-context_proof.px,dy=button->y/zoom-context_proof.py;
        gboolean matched=context_proof.pressed && context_proof.source==widget && button->button==3
            && !(button->state&(GDK_BUTTON1_MASK|GDK_BUTTON2_MASK|GDK_BUTTON4_MASK|GDK_BUTTON5_MASK))
            && context_proof.publication==surface_gate.publication && context_proof.lease==surface_gate.lease && dx*dx+dy*dy<=25;
        context_proof.pressed=FALSE;context_proof.available=matched;
        context_proof.x=button->x/zoom;context_proof.y=button->y/zoom;context_proof.captured=g_get_monotonic_time();
    } else if (event->type==GDK_KEY_PRESS) {
        GdkEventKey *key=(GdkEventKey *)event;
        gboolean context=key->keyval==GDK_KEY_Menu || (key->keyval==GDK_KEY_F10 && (key->state&GDK_SHIFT_MASK));
        gboolean navigation=key->keyval==GDK_KEY_Escape || key->keyval==GDK_KEY_Up || key->keyval==GDK_KEY_Down
            || key->keyval==GDK_KEY_Home || key->keyval==GDK_KEY_End || key->keyval==GDK_KEY_Return;
        guint bit=context_key_bit(key->keyval);
        gboolean fresh=!(held_context_keys&bit);
        held_context_keys|=bit;
        context_proof=(ContextProof){.source=widget,.epoch=context_epoch,.publication=surface_gate.publication,.lease=surface_gate.lease,
            .captured=g_get_monotonic_time(),.key=key->keyval,.available=(context||navigation)&&fresh&&!(key->state&forbidden)};
        if(qa_exit){g_print("context-key-report: key=%u state=%u hardware=%u time=%u fresh=%d available=%d popup=%d\n",key->keyval,key->state,key->hardware_keycode,key->time,fresh,context_proof.available,widget==GTK_WIDGET(popup_view));fflush(stdout);}
    } else if (event->type==GDK_KEY_RELEASE) {
        held_context_keys&=~context_key_bit(((GdkEventKey *)event)->keyval);
    } else if (event->type==GDK_SCROLL || event->type==GDK_FOCUS_CHANGE || event->type==GDK_GRAB_BROKEN) {
        context_proof.available=FALSE;context_proof.pressed=FALSE;held_context_keys=0;
    }
    return FALSE;
}
typedef struct {JsonNode *message;ContextProof proof;gboolean popup;} ContextCheck;
static gboolean context_current(ContextProof *proof,gboolean popup) {
    return !shutting_down && proof->epoch==context_epoch && proof->publication==surface_gate.publication && proof->lease==surface_gate.lease
        && g_get_monotonic_time()-proof->captured<=500000
        && proof->source==GTK_WIDGET(popup?popup_view:view) && (!popup || surface_popup_ready());
}
static void context_checked(GObject *object,GAsyncResult *result,gpointer data) {
    ContextCheck *check=data;GError *error=NULL;
    JSCValue *value=webkit_web_view_evaluate_javascript_finish(WEBKIT_WEB_VIEW(object),result,&error);
    gboolean admitted=!error && value && jsc_value_is_boolean(value) && jsc_value_to_boolean(value)
        && context_current(&check->proof,check->popup);
    if (admitted) {
        if (check->proof.pointer && !check->popup) {
            double zoom=webkit_web_view_get_zoom_level(WEBKIT_WEB_VIEW(check->proof.source));
            context_anchor=(GdkRectangle){(int)(check->proof.x*zoom),(int)(check->proof.y*zoom),1,1};has_context_anchor=TRUE;
        } else has_context_anchor=FALSE;
        g_print("surface-context-admitted: origin=%s trigger=%s publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT "\n",
            check->popup?"popup":"bar",check->proof.pointer?"pointer":"keyboard",check->proof.publication,check->proof.lease);fflush(stdout);
        surface_eval(view,"receiveAction",check->message);
    } else {g_print("surface-context-refused: verification-or-stale\n");fflush(stdout);}
    if (error) g_error_free(error);
    if (value) g_object_unref(value);
    json_node_unref(check->message);g_free(check);
}
static gboolean context_receive(WebKitUserContentManager *manager,JsonNode *root) {
    if (!root || !JSON_NODE_HOLDS_OBJECT(root) || !surface_snapshot) return FALSE;
    JsonObject *o=json_node_get_object(root);guint64 publication,lease;
    const char *const fields[]={"surfaceProtocol","kind","surface","publication","lease","id","trigger","x","y"};
    gboolean popup=manager==popup_manager;
    if ((manager!=primary_manager && !popup) || !surface_fields(o,fields,9)
        || json_node_get_value_type(json_object_get_member(o,"surfaceProtocol"))!=G_TYPE_INT64 || json_object_get_int_member(o,"surfaceProtocol")!=2
        || !surface_text(json_object_get_member(o,"kind"),32,FALSE) || !g_str_equal(json_object_get_string_member(o,"kind"),"surface-context")
        || !surface_text(json_object_get_member(o,"surface"),16,FALSE) || !g_str_equal(json_object_get_string_member(o,"surface"),popup?"popup":"bar")
        || !surface_uint(json_object_get_member(o,"publication"),&publication) || publication!=surface_gate.publication
        || !surface_uint(json_object_get_member(o,"lease"),&lease) || lease!=surface_gate.lease
        || !surface_text(json_object_get_member(o,"id"),512,FALSE) || !surface_text(json_object_get_member(o,"trigger"),16,FALSE)
        || json_node_get_value_type(json_object_get_member(o,"x"))!=G_TYPE_INT64 || json_node_get_value_type(json_object_get_member(o,"y"))!=G_TYPE_INT64) return FALSE;
    const char *trigger=json_object_get_string_member(o,"trigger");
    gboolean pointer=g_str_equal(trigger,"pointer"),keyboard=g_str_equal(trigger,"keyboard");
    if ((!pointer&&!keyboard) || !context_proof.available || context_proof.pointer!=pointer || !context_current(&context_proof,popup)
        || (keyboard && context_proof.key!=GDK_KEY_Menu && context_proof.key!=GDK_KEY_F10)) return FALSE;
    gint64 x=json_object_get_int_member(o,"x"),y=json_object_get_int_member(o,"y");
    double dx=(double)x-context_proof.x,dy=(double)y-context_proof.y;
    if (pointer && (dx*dx+dy*dy>2 || x<0 || y<0)) return FALSE;
    if (keyboard && (x!=0 || y!=0)) return FALSE;
    JsonArray *controls=json_object_get_array_member(json_node_get_object(surface_snapshot),popup?"popup":"bar");
    gboolean found=FALSE;
    for (guint i=0;i<json_array_get_length(controls);i++) {
        JsonObject *control=json_array_get_object_element(controls,i);
        if (g_str_equal(json_object_get_string_member(control,"id"),json_object_get_string_member(o,"id")) && json_object_get_boolean_member(control,"enabled")) found=TRUE;
    }
    if (!found) return FALSE;
    ContextCheck *check=g_new0(ContextCheck,1);check->message=json_node_copy(root);check->proof=context_proof;check->popup=popup;
    context_proof.available=FALSE;
    g_autofree char *wire=json_to_string(root,FALSE);
    g_autofree char *script=NULL;
    if (pointer) script=g_strdup_printf("(()=>{const c=%s,n=document.querySelector('.surface-%s'),hit=(x,y)=>document.elementFromPoint(x,y)?.closest('[data-surface-control]');if(!n||n.dataset.publication!==c.publication||n.dataset.lease!==c.lease)return false;const a=hit(%.17g,%.17g),b=hit(c.x,c.y);return !!a&&!!b&&n.contains(a)&&n.contains(b)&&!a.disabled&&!b.disabled&&a.dataset.surfaceControl===c.id&&b.dataset.surfaceControl===c.id;})()",wire,popup?"popup":"bar",check->proof.px,check->proof.py);
    else script=g_strdup_printf("(()=>{const c=%s,n=document.querySelector('.surface-%s'),a=document.activeElement?.closest('[data-surface-control]');return !!n&&!!a&&n.dataset.publication===c.publication&&n.dataset.lease===c.lease&&n.contains(a)&&!a.disabled&&a.dataset.surfaceControl===c.id;})()",wire,popup?"popup":"bar");
    webkit_web_view_evaluate_javascript(popup?popup_view:view,script,-1,NULL,NULL,NULL,context_checked,check);
    return TRUE;
}
static gboolean navigation_receive(WebKitUserContentManager *manager,JsonNode *root) {
    if (manager!=popup_manager || !surface_popup_ready() || !surface_snapshot || !JSON_NODE_HOLDS_OBJECT(root)) return FALSE;
    if (!g_str_equal(json_object_get_string_member(json_node_get_object(surface_snapshot),"mode"),"menu")) return FALSE;
    JsonObject *o=json_node_get_object(root);guint64 publication,lease;
    const char *const fields[]={"surfaceProtocol","kind","surface","publication","lease","key"};
    if (!surface_fields(o,fields,6) || json_node_get_value_type(json_object_get_member(o,"surfaceProtocol"))!=G_TYPE_INT64 || json_object_get_int_member(o,"surfaceProtocol")!=2
        || !surface_text(json_object_get_member(o,"kind"),32,FALSE) || !g_str_equal(json_object_get_string_member(o,"kind"),"surface-menu-navigation")
        || !surface_text(json_object_get_member(o,"surface"),16,FALSE) || !g_str_equal(json_object_get_string_member(o,"surface"),"popup")
        || !surface_uint(json_object_get_member(o,"publication"),&publication) || publication!=surface_gate.publication
        || !surface_uint(json_object_get_member(o,"lease"),&lease) || lease!=surface_gate.lease || !surface_text(json_object_get_member(o,"key"),16,FALSE)
        || !context_proof.available || context_proof.pointer || !context_current(&context_proof,TRUE)) return FALSE;
    const char *names[]={"Escape","ArrowUp","ArrowDown","Home","End","Enter"};
    const guint keys[]={GDK_KEY_Escape,GDK_KEY_Up,GDK_KEY_Down,GDK_KEY_Home,GDK_KEY_End,GDK_KEY_Return};
    gboolean matched=FALSE;
    for (guint i=0;i<G_N_ELEMENTS(names);i++) if (g_str_equal(json_object_get_string_member(o,"key"),names[i]) && context_proof.key==keys[i]) matched=TRUE;
    if (!matched) return FALSE;
    context_proof.available=FALSE;surface_eval(view,"receiveAction",root);return TRUE;
}
