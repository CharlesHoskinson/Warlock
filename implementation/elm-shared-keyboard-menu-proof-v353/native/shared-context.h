/* One native proof, always scoped to a live ID/generation and engine. */
typedef struct {
    GtkWidget *source;
    guint64 publication,lease,epoch,view_id,view_generation;
    gint64 captured;
    double px,py,x,y;
    guint key;
    gboolean pointer,pressed,available,released;
} ContextProof;
static ContextProof context_proof;
static guint held_context_keys;
static guint64 context_epoch;
static guint64 context_anchor_view,context_anchor_generation,context_anchor_epoch;
static ContextKeySource popup_context_keys;
static JsonNode *terminal_navigation;
static ContextProof terminal_proof;
static void terminal_cancel(void) {
    if(terminal_navigation)json_node_unref(terminal_navigation);
    terminal_navigation=NULL;
}
static void terminal_release(GtkWidget *widget,guint key);
static void shared_context_cancel(void) {
    terminal_cancel();
    if(context_epoch<G_MAXUINT64) context_epoch++;
    context_proof.available=FALSE;context_proof.pressed=FALSE;has_context_anchor=FALSE;
    /* Held keys and per-engine replay watermarks survive presentation retirement. */
}
static OutputView *context_engine(GtkWidget *widget) {
    if(widget==GTK_WIDGET(popup_view)) return popup_owner && popup_owner->active ? popup_owner : NULL;
    for(guint i=0;output_views && i<output_views->len;i++) {
        OutputView *row=g_ptr_array_index(output_views,i);
        if(row->active && widget==GTK_WIDGET(row->engine)) return row;
    }
    return NULL;
}
static int context_key_admit(GtkWidget *widget,GdkEventKey *key) {
    OutputView *row=context_engine(widget);
    if(!row || !key || (key->type!=GDK_KEY_PRESS && key->type!=GDK_KEY_RELEASE)) return 0;
    ContextKeySignature signature={.type=(uint32_t)key->type,.time=key->time,.hardware=key->hardware_keycode,
        .keyval=key->keyval,.state=key->state,.group=key->group,.window=(uintptr_t)key->window,
        .device=(uintptr_t)gdk_event_get_device((GdkEvent *)key)};
    return context_keys_admit(widget==GTK_WIDGET(popup_view)?&popup_context_keys:&row->context_keys,&signature);
}
static guint context_key_bit(guint key) {
    switch (key) {
        case GDK_KEY_Menu:return 1;case GDK_KEY_F10:return 2;case GDK_KEY_Escape:return 4;
        case GDK_KEY_Up:return 8;case GDK_KEY_Down:return 16;case GDK_KEY_Home:return 32;
        case GDK_KEY_End:return 64;case GDK_KEY_Return:return 128;default:return 0;
    }
}
static gboolean shared_context_event(GtkWidget *widget,GdkEvent *event,gpointer unused) {
    (void)unused;
    OutputView *origin=context_engine(widget);
    if(!origin) return FALSE;
    if (context_epoch==G_MAXUINT64) return FALSE;
    if (event->any.send_event) {shared_context_cancel();return FALSE;}
    // WebKit asynchronously replays unhandled keys through GTK. A replay must
    // neither overwrite a newer physical proof nor clear its held-key state.
    if (event->type==GDK_KEY_PRESS || event->type==GDK_KEY_RELEASE) {
        int admission=context_key_admit(widget,(GdkEventKey *)event);
        if(admission<=0){
            if(admission<0){
                context_epoch++;context_proof.available=FALSE;context_proof.pressed=FALSE;
                if(event->type==GDK_KEY_PRESS) held_context_keys|=context_key_bit(((GdkEventKey *)event)->keyval);
            }
            return FALSE;
        }
    }
    if (event->type==GDK_BUTTON_PRESS || event->type==GDK_KEY_PRESS || event->type==GDK_SCROLL || event->type==GDK_FOCUS_CHANGE || event->type==GDK_GRAB_BROKEN) {context_epoch++;has_context_anchor=FALSE;}
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
        guint released=((GdkEventKey *)event)->keyval;
        gboolean was_held=(held_context_keys&context_key_bit(released))!=0;
        if(was_held && context_proof.source==widget && !context_proof.pointer && context_proof.key==released)
            context_proof.released=TRUE;
        held_context_keys&=~context_key_bit(released);
        terminal_release(widget,released);
    } else if (event->type==GDK_SCROLL || event->type==GDK_FOCUS_CHANGE || event->type==GDK_GRAB_BROKEN) {
        context_proof.available=FALSE;context_proof.pressed=FALSE;/* Keep held keys until an admitted physical release. */
    }
    if(context_proof.source==widget) {context_proof.view_id=origin->id;context_proof.view_generation=origin->generation;}
    return FALSE;
}
typedef struct {JsonNode *message;ContextProof proof;gboolean popup;GObject *engine;} ContextCheck;
static gboolean context_current(const ContextProof *proof,gboolean popup) {
    OutputView *origin=context_engine(proof->source);
    gint64 age=g_get_monotonic_time()-proof->captured;
    return !shutting_down && context_epoch!=G_MAXUINT64 && origin && origin->id==proof->view_id && origin->generation==proof->view_generation
        && proof->epoch==context_epoch && proof->publication==surface_gate.publication && proof->lease==surface_gate.lease
        && proof->captured>0 && age>=0 && age<=500000
        && ((popup && proof->source==GTK_WIDGET(popup_view) && origin==popup_owner && surface_popup_ready())
            || (!popup && proof->source==GTK_WIDGET(origin->engine)));
}
/* Terminal navigation must retain the popup until the admitted physical
 * release. Otherwise teardown loses that release and leaves repeat guards held.
 * The original proof deadline/scope/publication are never renewed here. */
static gboolean terminal_store(JsonNode *message,const ContextProof *proof) {
    gboolean held=(held_context_keys&context_key_bit(proof->key))!=0;
    if(terminal_navigation || !context_current(proof,TRUE) ||
       (proof->key!=GDK_KEY_Escape && proof->key!=GDK_KEY_Return) ||
       (held==proof->released))return FALSE;
    terminal_navigation=json_node_copy(message);terminal_proof=*proof;return TRUE;
}
static JsonNode *terminal_take(GtkWidget *widget,guint key) {
    if(!terminal_navigation || terminal_proof.source!=widget || terminal_proof.key!=key)return NULL;
    JsonNode *message=terminal_navigation;terminal_navigation=NULL;
    if(!context_current(&terminal_proof,TRUE) || (held_context_keys&context_key_bit(key))) {
        json_node_unref(message);return NULL;
    }
    return message;
}
static void terminal_release(GtkWidget *widget,guint key) {
    JsonNode *message=terminal_take(widget,key);
    if(!message)return;
    g_print("surface-terminal-released: key=%u view=%" G_GUINT64_FORMAT " generation=%" G_GUINT64_FORMAT "\n",key,terminal_proof.view_id,terminal_proof.view_generation);fflush(stdout);
    shared_context_forward(popup_owner,message,TRUE);json_node_unref(message);
}
static gboolean context_finish_allowed(const ContextProof *proof,gboolean popup,GObject *object,gboolean dom_verified) {
    return dom_verified && object==G_OBJECT(proof->source) && context_current(proof,popup);
}
static void context_checked(GObject *object,GAsyncResult *result,gpointer data) {
    ContextCheck *check=data;GError *error=NULL;
    JSCValue *value=webkit_web_view_evaluate_javascript_finish(WEBKIT_WEB_VIEW(object),result,&error);
    gboolean dom_verified=!error && value && jsc_value_is_boolean(value) && jsc_value_to_boolean(value);
    gboolean admitted=context_finish_allowed(&check->proof,check->popup,object,dom_verified);
    if(admitted) {
        if(check->proof.pointer && !check->popup) {
            double zoom=webkit_web_view_get_zoom_level(WEBKIT_WEB_VIEW(check->proof.source));
            context_anchor_view=check->proof.view_id;context_anchor_generation=check->proof.view_generation;context_anchor_epoch=context_epoch;
            context_anchor=(GdkRectangle){(int)(check->proof.x*zoom),(int)(check->proof.y*zoom),1,1};has_context_anchor=TRUE;
        } else has_context_anchor=FALSE;
        OutputView *origin=context_engine(check->proof.source);
        g_print("surface-context-admitted: view=%" G_GUINT64_FORMAT " generation=%" G_GUINT64_FORMAT " origin=%s trigger=%s publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT "\n",
            origin->id,origin->generation,check->popup?"popup":"bar",check->proof.pointer?"pointer":"keyboard",check->proof.publication,check->proof.lease);fflush(stdout);
        shared_context_forward(origin,check->message,check->popup);
    } else {g_print("surface-context-refused: verification-or-stale\n");fflush(stdout);}
    if(error) g_error_free(error);
    if(value) g_object_unref(value);
    json_node_unref(check->message);g_object_unref(check->engine);g_free(check);
}
static gboolean context_admit(WebKitUserContentManager *manager,JsonNode *root,ContextProof *admitted,gboolean *is_popup) {
    if (!root || !JSON_NODE_HOLDS_OBJECT(root) || !surface_snapshot) return FALSE;
    JsonObject *o=json_node_get_object(root);guint64 publication,lease;
    const char *const fields[]={"surfaceProtocol","kind","surface","publication","lease","id","trigger","x","y"};
    gboolean popup=manager==popup_manager;
    OutputView *origin=popup?popup_owner:manager_lookup(manager);
    if(!origin || !origin->active || context_proof.source!=GTK_WIDGET(popup?popup_view:origin->engine) || origin->id!=context_proof.view_id || origin->generation!=context_proof.view_generation) return FALSE;
    if ((!manager_lookup(manager) && !popup) || !surface_fields(o,fields,9)
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
    *admitted=context_proof;*is_popup=popup;return TRUE;
}
static gboolean context_consume(const ContextProof *proof,gboolean popup) {
    if(!context_proof.available || !context_current(proof,popup) || proof->source!=context_proof.source || proof->epoch!=context_proof.epoch) return FALSE;
    context_proof.available=FALSE;return TRUE;
}
static gboolean shared_context_receive(WebKitUserContentManager *manager,JsonNode *root) {
    ContextProof proof;gboolean popup;
    if(!context_admit(manager,root,&proof,&popup) || !context_consume(&proof,popup)) return FALSE;
    ContextCheck *check=g_new0(ContextCheck,1);check->message=json_node_copy(root);check->proof=proof;check->popup=popup;check->engine=g_object_ref(G_OBJECT(proof.source));
    context_proof.available=FALSE;
    g_autofree char *wire=json_to_string(root,FALSE);
    g_autofree char *script=NULL;
    if (proof.pointer) script=g_strdup_printf("(()=>{const c=%s,n=document.querySelector('.surface-%s'),hit=(x,y)=>document.elementFromPoint(x,y)?.closest('[data-surface-control]');if(!n||n.dataset.publication!==c.publication||n.dataset.lease!==c.lease)return false;const a=hit(%.17g,%.17g),b=hit(c.x,c.y);return !!a&&!!b&&n.contains(a)&&n.contains(b)&&!a.disabled&&!b.disabled&&a.dataset.surfaceControl===c.id&&b.dataset.surfaceControl===c.id;})()",wire,popup?"popup":"bar",check->proof.px,check->proof.py);
    else script=g_strdup_printf("(()=>{const c=%s,n=document.querySelector('.surface-%s'),a=document.activeElement?.closest('[data-surface-control]');return !!n&&!!a&&n.dataset.publication===c.publication&&n.dataset.lease===c.lease&&n.contains(a)&&!a.disabled&&a.dataset.surfaceControl===c.id;})()",wire,popup?"popup":"bar");
    webkit_web_view_evaluate_javascript(WEBKIT_WEB_VIEW(proof.source),script,-1,NULL,NULL,NULL,context_checked,check);
    return TRUE;
}
static gboolean shared_navigation_key(guint key,const char *name) {
    const char *names[]={"Escape","ArrowUp","ArrowDown","Home","End","Enter","Close"};
    const guint keys[]={GDK_KEY_Escape,GDK_KEY_Up,GDK_KEY_Down,GDK_KEY_Home,GDK_KEY_End,GDK_KEY_Return,GDK_KEY_Return};
    for(guint i=0;i<G_N_ELEMENTS(names);i++)if(g_strcmp0(name,names[i])==0 && key==keys[i])return TRUE;
    return FALSE;
}
static gboolean shared_navigation_receive(WebKitUserContentManager *manager,JsonNode *root) {
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
    if(!shared_navigation_key(context_proof.key,json_object_get_string_member(o,"key")))return FALSE;
    if(context_proof.key==GDK_KEY_Escape || context_proof.key==GDK_KEY_Return) {
        if(!terminal_store(root,&context_proof))return FALSE;
        context_proof.available=FALSE;
        /* The admitted release may precede asynchronous WebKit keydown. */
        if(context_proof.released)terminal_release(context_proof.source,context_proof.key);
        return TRUE;
    }
    context_proof.available=FALSE;shared_context_forward(popup_owner,root,TRUE);return TRUE;
}

static gboolean shared_anchor_for(const OutputView *owner,JsonNode *frame) {
    return owner && owner->active && has_context_anchor && context_anchor_epoch==context_epoch
        && owner->id==context_anchor_view && owner->generation==context_anchor_generation
        && frame && JSON_NODE_HOLDS_OBJECT(frame)
        && g_strcmp0(json_object_get_string_member(json_node_get_object(frame),"mode"),"menu")==0;
}
