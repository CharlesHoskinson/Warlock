/* Synthetic engine/manager identities exercise the actual production guards.
 * This test does not call DOM evaluation, GTK input, or any compositor. */
#define G_DISABLE_CAST_CHECKS
#define ELM_SHARED_HOST_MAIN archived_shared_main
#include "shared-host.c"
static guint checks;
#define CHECK(name,expr) do{checks++;if(!(expr)){g_printerr("failed %u: %s\n",checks,name);return 1;}}while(0)
static const char *context_wire="{\"surfaceProtocol\":2,\"kind\":\"surface-context\",\"surface\":\"bar\",\"publication\":\"10\",\"lease\":\"2\",\"id\":\"bar:group:application:org.a\",\"trigger\":\"keyboard\",\"x\":0,\"y\":0}";
static void proof(OutputView *row,gboolean popup) {
    context_proof=(ContextProof){.source=(GtkWidget*)(popup?popup_view:row->engine),.view_id=row->id,.view_generation=row->generation,
        .epoch=context_epoch,.publication=10,.lease=2,.captured=g_get_monotonic_time(),.key=GDK_KEY_Menu,.available=TRUE};
}
int main(void) {
    OutputView one={.id=1,.generation=1,.engine=(WebKitWebView*)11,.manager=(WebKitUserContentManager*)21,.active=TRUE};
    OutputView two={.id=2,.generation=1,.engine=(WebKitWebView*)12,.manager=(WebKitUserContentManager*)22,.active=TRUE};
    output_views=g_ptr_array_new();g_ptr_array_add(output_views,&one);g_ptr_array_add(output_views,&two);
    popup_view=(WebKitWebView*)13;popup_manager=(WebKitUserContentManager*)23;primary_manager=(WebKitUserContentManager*)24;popup_owner=&one;
    surface_gate=(SurfaceGate){10,2,0};context_epoch=1;
    surface_snapshot=test_json("{\"surfaceProtocol\":2,\"publication\":\"10\",\"lease\":\"2\",\"mode\":\"closed\",\"status\":\"Ready\",\"bar\":[{\"id\":\"bar:group:application:org.a\",\"domId\":\"group:a\",\"label\":\"A\",\"ariaLabel\":\"A\",\"detail\":\"1\",\"enabled\":true}],\"popup\":[]}");
    guint64 pub,lease;gboolean opened;CHECK("actual native frame validates",surface_frame(surface_snapshot,&pub,&lease,&opened));
    JsonNode *request=test_json(context_wire);ContextProof admitted;gboolean popup;
    proof(&one,FALSE);CHECK("matching first engine receives proof",context_admit(one.manager,request,&admitted,&popup)&&!popup&&admitted.view_id==1);
    CHECK("other manager cannot claim first engine",!context_admit(two.manager,request,&admitted,&popup));
    CHECK("hidden controller has no input proof",!context_admit(primary_manager,request,&admitted,&popup));
    CHECK("unregistered manager refused",!context_admit((WebKitUserContentManager*)25,request,&admitted,&popup));
    proof(&two,FALSE);CHECK("second view proof retains its own scope",context_admit(two.manager,request,&admitted,&popup)&&admitted.view_id==2);
    CHECK("single use consumption succeeds",context_consume(&admitted,FALSE));CHECK("duplicate proof cannot consume",!context_consume(&admitted,FALSE));
    CHECK("copy can finish after single-use consumption",context_finish_allowed(&admitted,FALSE,(GObject*)two.engine,TRUE));
    CHECK("DOM verification required",!context_finish_allowed(&admitted,FALSE,(GObject*)two.engine,FALSE));
    CHECK("other async callback engine refused",!context_finish_allowed(&admitted,FALSE,(GObject*)one.engine,TRUE));
    two.active=FALSE;CHECK("retired engine completion refused",!context_finish_allowed(&admitted,FALSE,(GObject*)two.engine,TRUE));two.active=TRUE;
    two.generation=2;CHECK("replacement generation completion refused",!context_finish_allowed(&admitted,FALSE,(GObject*)two.engine,TRUE));two.generation=1;
    two.id=3;CHECK("replacement view identity completion refused",!context_finish_allowed(&admitted,FALSE,(GObject*)two.engine,TRUE));two.id=2;
    ContextProof saved=admitted;context_epoch++;CHECK("later physical event retires asynchronous proof",!context_current(&saved,FALSE));context_epoch--;
    surface_gate.publication++;CHECK("new presentation retires proof",!context_current(&saved,FALSE));surface_gate.publication--;
    surface_gate.lease++;CHECK("new popup lease retires proof",!context_current(&saved,FALSE));surface_gate.lease--;
    saved.captured=g_get_monotonic_time()-500001;CHECK("native proof deadline preserved",!context_current(&saved,FALSE));saved.captured=g_get_monotonic_time()+1000000;CHECK("future capture cannot qualify",!context_current(&saved,FALSE));saved.captured=0;CHECK("missing clock refused",!context_current(&saved,FALSE));
    proof(&one,FALSE);held_context_keys=3;one.context_keys=(ContextKeySource){.initialized=1,.watermark=123,.count=1};saved=context_proof;shared_context_cancel();
    CHECK("retirement cancels available pointer/key receipt",!context_proof.available&&!context_proof.pressed);
    CHECK("retirement keeps held key suppression",held_context_keys==3);CHECK("retirement keeps source timestamp signatures",one.context_keys.watermark==123&&one.context_keys.count==1);CHECK("retirement rejects saved completion",!context_current(&saved,FALSE));
    proof(&one,FALSE);context_epoch=G_MAXUINT64;CHECK("epoch exhaustion refuses proof",!context_current(&context_proof,FALSE));shared_context_cancel();CHECK("epoch never wraps",context_epoch==G_MAXUINT64);context_epoch=2;
    const char *names[]={"surfaceProtocol","kind","surface","publication","lease","id","trigger","x","y"};
    for(guint i=0;i<G_N_ELEMENTS(names);i++) {JsonNode *bad=test_json(context_wire);json_object_remove_member(json_node_get_object(bad),names[i]);proof(&one,FALSE);CHECK("every missing wire member refused",!context_admit(one.manager,bad,&admitted,&popup));json_node_unref(bad);}
    JsonObject *o=json_node_get_object(request);json_object_set_string_member(o,"extra","execute");proof(&one,FALSE);CHECK("extra context field refused",!context_admit(one.manager,request,&admitted,&popup));json_object_remove_member(o,"extra");
    json_object_set_boolean_member(o,"surfaceProtocol",TRUE);CHECK("Boolean protocol refused",!context_admit(one.manager,request,&admitted,&popup));json_object_set_int_member(o,"surfaceProtocol",2);
    json_object_set_string_member(o,"trigger","pointer");proof(&one,FALSE);CHECK("keyboard cannot masquerade as pointer",!context_admit(one.manager,request,&admitted,&popup));context_proof.pointer=TRUE;context_proof.x=context_proof.y=0;CHECK("matching pointer release can qualify",context_admit(one.manager,request,&admitted,&popup));
    json_object_set_int_member(o,"x",3);CHECK("pointer release displacement refused",!context_admit(one.manager,request,&admitted,&popup));json_object_set_int_member(o,"x",0);json_object_set_string_member(o,"trigger","keyboard");proof(&one,FALSE);
    json_object_set_string_member(o,"id","bar:execute");CHECK("unpublished control refused",!context_admit(one.manager,request,&admitted,&popup));json_object_set_string_member(o,"id","bar:group:application:org.a");
    JsonObject *control=json_array_get_object_element(json_object_get_array_member(json_node_get_object(surface_snapshot),"bar"),0);json_object_set_boolean_member(control,"enabled",FALSE);CHECK("disabled control cannot acquire context proof",!context_admit(one.manager,request,&admitted,&popup));json_object_set_boolean_member(control,"enabled",TRUE);
    proof(&one,TRUE);CHECK("bar source cannot reuse popup proof",!context_admit(one.manager,request,&admitted,&popup));CHECK("popup needs configured and applied surface",!context_current(&context_proof,TRUE));
    popup_active=grab_ready=keyboard_ready=TRUE;configured_lease=applied_lease=2;applied_publication=10;CHECK("exact live popup owner proof qualifies",context_current(&context_proof,TRUE));popup_owner=&two;CHECK("popup relocation invalidates old owner proof",!context_current(&context_proof,TRUE));popup_owner=&one;
    shutting_down=TRUE;CHECK("shutdown rejects native proof",!context_current(&context_proof,TRUE));shutting_down=FALSE;
    JsonNode *menu=test_json("{\"mode\":\"menu\"}");
    context_anchor_view=one.id;context_anchor_generation=one.generation;context_anchor_epoch=context_epoch;has_context_anchor=TRUE;
    CHECK("pointer anchor belongs to its actual view",shared_anchor_for(&one,menu));
    CHECK("other output cannot reuse pointer anchor",!shared_anchor_for(&two,menu));
    one.generation++;CHECK("replacement generation cannot reuse anchor",!shared_anchor_for(&one,menu));one.generation--;
    context_epoch++;CHECK("later native event invalidates anchor",!shared_anchor_for(&one,menu));context_epoch--;
    json_object_set_string_member(json_node_get_object(menu),"mode","applications");CHECK("application popup does not reuse menu anchor",!shared_anchor_for(&one,menu));
    held_context_keys=3;ContextProof before=context_proof;GdkEvent synthetic={0};synthetic.any.send_event=TRUE;synthetic.type=GDK_KEY_PRESS;
    shared_context_event((GtkWidget*)one.engine,&synthetic,NULL);CHECK("synthetic native event cannot create proof",!context_proof.available && context_epoch!=before.epoch);CHECK("synthetic event preserves held-key suppression",held_context_keys==3);CHECK("synthetic event invalidates pointer anchor",!has_context_anchor);
    JsonNode *nav=test_json("{\"surfaceProtocol\":2,\"kind\":\"surface-menu-navigation\",\"surface\":\"popup\",\"publication\":\"10\",\"lease\":\"2\",\"key\":\"Escape\"}");
    proof(&one,TRUE);context_proof.key=GDK_KEY_Escape;held_context_keys=4;
    CHECK("terminal navigation stores exact live press",terminal_store(nav,&context_proof));
    CHECK("terminal duplicate cannot overwrite press",!terminal_store(nav,&context_proof));
    CHECK("other key release cannot consume terminal",terminal_take((GtkWidget*)popup_view,GDK_KEY_Return)==NULL && terminal_navigation);
    CHECK("other source release cannot consume terminal",terminal_take((GtkWidget*)one.engine,GDK_KEY_Escape)==NULL && terminal_navigation);
    held_context_keys=0;JsonNode *taken=terminal_take((GtkWidget*)popup_view,GDK_KEY_Escape);
    CHECK("matching physical release consumes once",taken && !terminal_navigation);if(taken)json_node_unref(taken);
    CHECK("duplicate release cannot replay terminal",!terminal_take((GtkWidget*)popup_view,GDK_KEY_Escape));
    held_context_keys=4;proof(&one,TRUE);context_proof.key=GDK_KEY_Escape;CHECK("second live terminal can prepare",terminal_store(nav,&context_proof));
    shared_context_cancel();CHECK("retirement cancels pending terminal",!terminal_navigation && held_context_keys==4);
    proof(&one,TRUE);context_proof.key=GDK_KEY_Escape;CHECK("live terminal stores before publication change",terminal_store(nav,&context_proof));
    surface_gate.publication++;held_context_keys=0;CHECK("changed publication refuses and consumes terminal",!terminal_take((GtkWidget*)popup_view,GDK_KEY_Escape) && !terminal_navigation);surface_gate.publication--;
    proof(&one,TRUE);context_proof.key=GDK_KEY_Escape;held_context_keys=4;CHECK("live terminal stores before expiry",terminal_store(nav,&context_proof));
    terminal_proof.captured=g_get_monotonic_time()-500001;held_context_keys=0;CHECK("original deadline is never renewed at release",!terminal_take((GtkWidget*)popup_view,GDK_KEY_Escape) && !terminal_navigation);
    proof(&one,TRUE);context_proof.key=GDK_KEY_Escape;held_context_keys=0;CHECK("terminal cannot store without held physical press",!terminal_store(nav,&context_proof));
    context_proof.released=TRUE;CHECK("admitted early release qualifies unchanged proof",terminal_store(nav,&context_proof));
    taken=terminal_take((GtkWidget*)popup_view,GDK_KEY_Escape);CHECK("early release consumes once without new proof",taken && !terminal_navigation);if(taken)json_node_unref(taken);
    CHECK("early release cannot replay consumed terminal",!terminal_take((GtkWidget*)popup_view,GDK_KEY_Escape));
    held_context_keys=4;CHECK("released proof contradicting held state refused",!terminal_store(nav,&context_proof));
    held_context_keys=0;context_proof.captured=g_get_monotonic_time()-500001;CHECK("early release cannot renew expired capture",!terminal_store(nav,&context_proof));
    CHECK("Close requires physical Return key",shared_navigation_key(GDK_KEY_Return,"Close"));
    CHECK("Escape cannot forge Return Close activation",!shared_navigation_key(GDK_KEY_Escape,"Close"));
    CHECK("unknown navigation name refused",!shared_navigation_key(GDK_KEY_Return,"Activate"));

    proof(&one,TRUE);context_proof.key=GDK_KEY_Escape;applied_publication=9;
    CHECK("pending render cannot qualify ordinary popup proof",!context_current(&context_proof,TRUE));
    CHECK("Escape dismissal qualifies pending render with native grab",context_terminal_current(&context_proof));
    held_context_keys=4;CHECK("pending render Escape stores physical press",terminal_store(nav,&context_proof));
    held_context_keys=0;taken=terminal_take((GtkWidget*)popup_view,GDK_KEY_Escape);CHECK("pending render Escape consumes original release",taken && !terminal_navigation);if(taken)json_node_unref(taken);
    context_proof.key=GDK_KEY_Return;CHECK("Enter cannot bypass pending render",!context_terminal_current(&context_proof));
    context_proof.key=GDK_KEY_Down;CHECK("selection cannot bypass pending render",!context_terminal_current(&context_proof));
    context_proof.key=GDK_KEY_Escape;grab_ready=FALSE;CHECK("dismissal requires native grab",!context_terminal_current(&context_proof));grab_ready=TRUE;
    keyboard_ready=FALSE;CHECK("dismissal requires native keyboard focus",!context_terminal_current(&context_proof));keyboard_ready=TRUE;
    configured_lease=1;CHECK("dismissal requires current native configuration",!context_terminal_current(&context_proof));configured_lease=2;
    surface_gate.closed=2;CHECK("dismissal refuses retired lease",!context_terminal_current(&context_proof));surface_gate.closed=0;
    surface_gate.publication++;CHECK("pending render dismissal refuses newer publication",!context_terminal_current(&context_proof));surface_gate.publication--;
    context_epoch++;CHECK("pending render dismissal refuses later input",!context_terminal_current(&context_proof));context_epoch--;
    one.generation++;CHECK("pending render dismissal refuses replacement view",!context_terminal_current(&context_proof));one.generation--;
    context_proof.captured=g_get_monotonic_time()-500001;CHECK("pending render dismissal preserves original500ms",!context_terminal_current(&context_proof));applied_publication=10;

    /* Real production helper with synthetic identities only: no GTK delivery
     * or compositor acceptance is implied by these refinement checks. */
    json_object_set_string_member(json_node_get_object(surface_snapshot),"mode","menu");
    proof(&one,TRUE);context_proof.key=GDK_KEY_Escape;held_context_keys=4;applied_publication=9;
    gint64 original_capture=context_proof.captured;
    CHECK("native Escape stores before old DOM acknowledgement",shared_native_escape_press((GtkWidget*)popup_view));
    CHECK("native Escape waits for release and consumes availability",terminal_navigation && !context_proof.available);
    CHECK("native Escape retains immutable capture and scope",terminal_proof.captured==original_capture && terminal_proof.epoch==context_epoch && terminal_proof.view_id==one.id && terminal_proof.view_generation==one.generation);
    JsonObject *intent=json_node_get_object(terminal_navigation);
    CHECK("native Escape intent carries physical proof stamp",g_str_equal(json_object_get_string_member(intent,"publication"),"10") && g_str_equal(json_object_get_string_member(intent,"lease"),"2") && g_str_equal(json_object_get_string_member(intent,"key"),"Escape"));
    CHECK("native Escape intent is protocol-valid effectless navigation",surface_fields(intent,(const char*[]){"surfaceProtocol","kind","surface","publication","lease","key"},6) && json_object_get_int_member(intent,"surfaceProtocol")==2 && g_str_equal(json_object_get_string_member(intent,"kind"),"surface-menu-navigation") && g_str_equal(json_object_get_string_member(intent,"surface"),"popup"));
    JsonNode *old_nav=json_node_copy(nav);json_object_set_string_member(json_node_get_object(old_nav),"publication","9");
    CHECK("old DOM callback remains refused after native intent",!shared_navigation_receive(popup_manager,old_nav));
    CHECK("current callback cannot duplicate consumed native press",!shared_navigation_receive(popup_manager,nav));
    CHECK("repeat helper cannot overwrite pending terminal",!shared_native_escape_press((GtkWidget*)popup_view) && terminal_proof.captured==original_capture);
    CHECK("wrong release leaves native Escape pending",!terminal_take((GtkWidget*)one.engine,GDK_KEY_Escape) && !terminal_take((GtkWidget*)popup_view,GDK_KEY_Return) && terminal_navigation);
    held_context_keys=0;taken=terminal_take((GtkWidget*)popup_view,GDK_KEY_Escape);
    CHECK("one native Escape releases one intent",taken && !terminal_navigation);if(taken)json_node_unref(taken);
    CHECK("native Escape duplicate release is inert",!terminal_take((GtkWidget*)popup_view,GDK_KEY_Escape));
    json_node_unref(old_nav);

    for(guint fault=0;fault<24;fault++) {
        terminal_cancel();proof(&one,TRUE);context_proof.key=GDK_KEY_Escape;held_context_keys=4;
        switch(fault) {
            case 0:context_proof.available=FALSE;break;
            case 1:context_proof.pointer=TRUE;break;
            case 2:context_proof.released=TRUE;break;
            case 3:context_proof.key=GDK_KEY_Return;break;
            case 4:context_proof.source=(GtkWidget*)one.engine;break;
            case 5:held_context_keys=0;break;
            case 6:context_proof.view_id++;break;
            case 7:context_proof.view_generation++;break;
            case 8:context_proof.epoch++;break;
            case 9:context_proof.publication++;break;
            case 10:context_proof.lease++;break;
            case 11:context_proof.captured=g_get_monotonic_time()-500001;break;
            case 12:context_proof.captured=g_get_monotonic_time()+1000000;break;
            case 13:context_proof.captured=0;break;
            case 14:popup_active=FALSE;break;
            case 15:grab_ready=FALSE;break;
            case 16:keyboard_ready=FALSE;break;
            case 17:configured_lease=1;break;
            case 18:surface_gate.closed=2;break;
            case 19:one.active=FALSE;break;
            case 20:shutting_down=TRUE;break;
            case 21:json_object_set_string_member(json_node_get_object(surface_snapshot),"mode","applications");break;
            case 22:json_object_set_string_member(json_node_get_object(surface_snapshot),"publication","9");break;
            case 23:json_object_set_string_member(json_node_get_object(surface_snapshot),"lease","1");break;
        }
        gint64 fault_capture=context_proof.captured;
        CHECK("invalid native Escape press never creates an intent",!shared_native_escape_press((GtkWidget*)popup_view) && !terminal_navigation);
        CHECK("refused native press never renews its capture",context_proof.captured==fault_capture);
        popup_active=grab_ready=keyboard_ready=one.active=TRUE;configured_lease=2;surface_gate.closed=0;shutting_down=FALSE;
        json_object_set_string_member(json_node_get_object(surface_snapshot),"mode","menu");
        json_object_set_string_member(json_node_get_object(surface_snapshot),"publication","10");
        json_object_set_string_member(json_node_get_object(surface_snapshot),"lease","2");
    }
    for(guint change=0;change<8;change++) {
        proof(&one,TRUE);context_proof.key=GDK_KEY_Escape;held_context_keys=4;
        CHECK("native Escape prepares before scope change",shared_native_escape_press((GtkWidget*)popup_view));
        switch(change) {
            case 0:context_epoch++;break;
            case 1:surface_gate.publication++;break;
            case 2:surface_gate.lease++;break;
            case 3:one.generation++;break;
            case 4:one.active=FALSE;break;
            case 5:terminal_proof.captured=g_get_monotonic_time()-500001;break;
            case 6:shared_context_cancel();break;
            case 7:keyboard_ready=FALSE;break;
        }
        held_context_keys=0;
        CHECK("scope change cancels terminal without forwarding",!terminal_take((GtkWidget*)popup_view,GDK_KEY_Escape) && !terminal_navigation);
        if(change==0)context_epoch--;
        if(change==1)surface_gate.publication--;
        if(change==2)surface_gate.lease--;
        if(change==3)one.generation--;
        one.active=keyboard_ready=TRUE;
    }
    proof(&one,TRUE);context_proof.key=GDK_KEY_Return;held_context_keys=128;
    CHECK("native Escape helper cannot admit Enter before DOM ready",!shared_native_escape_press((GtkWidget*)popup_view) && !context_terminal_current(&context_proof));
    held_context_keys=0;applied_publication=10;
    json_node_unref(nav);
    json_node_unref(menu);
    json_node_unref(request);json_node_unref(surface_snapshot);surface_snapshot=NULL;g_ptr_array_unref(output_views);output_views=NULL;
    g_print("shared-context-checks: %u\n",checks);return 0;
}
