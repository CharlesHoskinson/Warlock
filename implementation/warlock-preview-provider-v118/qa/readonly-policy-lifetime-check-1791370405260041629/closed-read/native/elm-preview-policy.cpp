#include "elm-preview-policy.h"
#include <jsc/jsc.h>
#include <json-glib/json-glib.h>
#include <cstring>
#include <memory>
#include <cmath>
#include <unordered_map>
#include <string>

namespace {
constexpr gsize budget = 16 * 1024 * 1024;
GQuark domain() { return g_quark_from_static_string("warlock-preview-policy"); }
gboolean fail(GError** error, WarlockPolicyError code, const char* message) {
    g_set_error_literal(error, domain(), code, message); return FALSE;
}
bool exact(JsonObject* object, std::initializer_list<const char*> names) {
    if (!object || json_object_get_size(object) != names.size()) return false;
    for (const auto* name : names) if (!json_object_has_member(object, name)) return false;
    return true;
}
}

struct _WarlockPreviewPolicy {
    GThread* creator{g_thread_ref(g_thread_self())};
    JSCContext* context{jsc_context_new()};
    GMainContext* scheduling{g_main_context_new()};
    std::unordered_map<guint,GSource*> timers;
    guint timer_serial{};
    JSCValue* incoming{};
    JSCValue* unsubscribe{};
    JSCValue* sink{};
    std::string latest;
    unsigned outputs{};
    bool active{}, unknown{}, blocked{}, controlled{}, closed{}, empty{}, ingress_empty{};
    ~_WarlockPreviewPolicy() {
        for (auto& [id, source] : timers) { (void)id; g_source_destroy(source); g_source_unref(source); }
        g_clear_object(&incoming); g_clear_object(&unsubscribe);
        g_clear_object(&sink); g_clear_object(&context); g_thread_unref(creator);
        g_main_context_unref(scheduling);
    }
};

namespace {
struct Timer { WarlockPreviewPolicy* owner; guint id; JSCValue* callback; GSource* source; };
void timer_destroy(gpointer data) { auto* timer = static_cast<Timer*>(data); g_object_unref(timer->callback); delete timer; }
gboolean timer_fire(gpointer data) {
    auto& timer = *static_cast<Timer*>(data); auto& self = *timer.owner;
    self.timers.erase(timer.id); g_source_unref(timer.source);
    if (!self.active || self.creator != g_thread_self()) { self.unknown = true; return G_SOURCE_REMOVE; }
    g_autoptr(JSCValue) returned = jsc_value_function_callv(timer.callback, 0, nullptr);
    if (!returned || jsc_context_get_exception(self.context)) self.unknown = true;
    return G_SOURCE_REMOVE;
}
double schedule(JSCValue* callback, double delay, gpointer data) {
    auto& self = *static_cast<WarlockPreviewPolicy*>(data);
    if (!jsc_value_is_function(callback) || self.creator != g_thread_self() || !std::isfinite(delay) || delay > 3000 || self.timers.size() >= 32 || self.timer_serial == G_MAXUINT) {
        self.unknown = true; return 0;
    }
    const auto id = ++self.timer_serial;
    auto* source = g_timeout_source_new(static_cast<guint>(std::ceil(std::max(0.0, delay))));
    auto* timer = new Timer{&self,id,JSC_VALUE(g_object_ref(callback)),source};
    g_source_set_name(source, "warlock-native-policy-timer");
    g_source_set_callback(source,timer_fire,timer,timer_destroy);
    self.timers.emplace(id,source); g_source_attach(source,self.scheduling);
    return id;
}
void cancel_timer(double id, gpointer data) {
    auto& self = *static_cast<WarlockPreviewPolicy*>(data);
    if (self.creator != g_thread_self() || !std::isfinite(id) || id < 1 || id > G_MAXUINT || std::floor(id) != id) return;
    auto found = self.timers.find(static_cast<guint>(id)); if (found == self.timers.end()) return;
    auto* source = found->second; self.timers.erase(found); g_source_destroy(source); g_source_unref(source);
}
gboolean deadline_fire(gpointer data) { *static_cast<bool*>(data) = true; return G_SOURCE_REMOVE; }
void output(JSCValue* value, gpointer data) {
    auto& self = *static_cast<WarlockPreviewPolicy*>(data);
    if (!self.active || self.creator != g_thread_self() || ++self.outputs != 1) {
        self.unknown = true; return;
    }
    g_autofree char* wire = jsc_value_to_json(value, 0);
    if (!wire || std::strlen(wire) > budget) { self.unknown = true; return; }
    g_autoptr(JsonParser) parser = json_parser_new();
    if (!json_parser_load_from_data(parser, wire, -1, nullptr)) { self.unknown = true; return; }
    auto* root = json_parser_get_root(parser);
    if (!JSON_NODE_HOLDS_OBJECT(root)) { self.unknown = true; return; }
    auto* object = json_node_get_object(root);
    if (!exact(object, {"models", "commands", "realm", "metadata", "enrollment", "feedback", "visuals"})) { self.unknown = true; return; }
    auto* realm_node = json_object_get_member(object, "realm");
    auto* models = json_object_get_member(object, "models");
    if (!JSON_NODE_HOLDS_OBJECT(realm_node) || !JSON_NODE_HOLDS_ARRAY(models)) { self.unknown = true; return; }
    auto* realm = json_node_get_object(realm_node);
    for (const auto* name : {"inputBlocked", "controlled", "closed"}) {
        if (!json_object_has_member(realm, name)) { self.unknown = true; return; }
        auto* field = json_object_get_member(realm, name);
        if (!field || json_node_get_value_type(field) != G_TYPE_BOOLEAN) { self.unknown = true; return; }
    }
    self.latest = wire;
    self.blocked = json_object_get_boolean_member(realm, "inputBlocked");
    self.controlled = json_object_get_boolean_member(realm, "controlled");
    self.closed = json_object_get_boolean_member(realm, "closed");
    self.empty = json_array_get_length(json_node_get_array(models)) == 0;
    if (!json_object_has_member(realm, "deferred") || !json_object_has_member(realm, "ingress")) { self.unknown = true; return; }
    auto* deferred = json_object_get_member(realm, "deferred");
    if (json_node_get_value_type(deferred) != G_TYPE_INT64) { self.unknown = true; return; }
    const auto waiting = json_node_get_int(deferred);
    if (waiting < 0 || waiting > 2130) { self.unknown = true; return; }
    self.ingress_empty = waiting == 0;
    if (self.controlled) {
        auto* ingress = json_object_get_member(realm, "ingress");
        if (!JSON_NODE_HOLDS_OBJECT(ingress)) { self.unknown = true; return; }
        auto* queued = json_node_get_object(ingress);
        if (!exact(queued, {"pending", "capacity", "intents"})) { self.unknown = true; return; }
        auto* count = json_object_get_member(queued, "pending");
        if (json_node_get_value_type(count) != G_TYPE_INT64 || json_node_get_int(count) < 0 || json_node_get_int(count) > 1065) { self.unknown = true; return; }
        self.ingress_empty = self.ingress_empty && json_node_get_int(count) == 0;
    }
}
bool exception(WarlockPreviewPolicy& self) {
    if (!jsc_context_get_exception(self.context)) return false;
    self.unknown = true; return true;
}
}

gboolean warlock_preview_policy_invoke(WarlockPreviewPolicy* self, const char* input, char** result, GError** error) {
    if (result) *result = nullptr;
    if (!self || !result) return fail(error, WARLOCK_POLICY_INVALID_INPUT, "Owned policy and output required");
    if (self->creator != g_thread_self()) return fail(error, WARLOCK_POLICY_WRONG_THREAD, "Original policy creator thread required");
    if (self->unknown || self->active) return fail(error, WARLOCK_POLICY_PROCESSING_UNKNOWN, "Policy processing is uncertain or already active");
    if (!input || std::strlen(input) > budget) return fail(error, WARLOCK_POLICY_INVALID_INPUT, "Original bounded policy input required");
    g_autoptr(JsonParser) parser = json_parser_new();
    if (!json_parser_load_from_data(parser, input, -1, nullptr)) return fail(error, WARLOCK_POLICY_INVALID_INPUT, "Policy input must be JSON");
    auto* root = json_parser_get_root(parser);
    if (!JSON_NODE_HOLDS_OBJECT(root)) return fail(error, WARLOCK_POLICY_INVALID_INPUT, "Exact policy input object required");
    auto* object = json_node_get_object(root);
    if (!exact(object, {"kind", "value"})) return fail(error, WARLOCK_POLICY_INVALID_INPUT, "Exact policy input fields required");
    auto* kind = json_object_get_member(object, "kind");
    if (json_node_get_value_type(kind) != G_TYPE_STRING) return fail(error, WARLOCK_POLICY_INVALID_INPUT, "Typed policy input kind required");
    const std::string name = json_node_get_string(kind);
    const bool ordinary = name == "native" || name == "presentation" || name == "legacy";
    if (!ordinary && name != "grant" && name != "issued" && name != "quarantine" && name != "closed" && name != "retry" && name != "status")
        return fail(error, WARLOCK_POLICY_INVALID_INPUT, "Closed native policy input union required");
    if (ordinary && self->blocked) return fail(error, WARLOCK_POLICY_WOULD_BLOCK, "Retain original input until deferred policy output admits");
    g_autoptr(JSCValue) argument = jsc_value_new_from_json(self->context, input);
    if (!argument || exception(*self)) return fail(error, WARLOCK_POLICY_PROCESSING_UNKNOWN, "Policy input conversion is uncertain");
    self->active = true; self->outputs = 0;
    JSCValue* parameters[] = {argument};
    g_autoptr(JSCValue) returned = jsc_value_function_callv(self->incoming, 1, parameters);
    // Elm's port managers initialize via real asynchronous zero-delay tasks.
    // Use this owner's private native context, retaining the original replay's
    // three-second processing limit and never running the desktop default loop.
    bool timed_out = false;
    auto* deadline = g_timeout_source_new(3000);
    g_source_set_callback(deadline,deadline_fire,&timed_out,nullptr);
    g_source_attach(deadline,self->scheduling);
    while (returned && !exception(*self) && !self->unknown && (!self->outputs || !self->timers.empty()) && !timed_out)
        g_main_context_iteration(self->scheduling,TRUE);
    g_source_destroy(deadline); g_source_unref(deadline);
    if (timed_out) self->unknown = true;
    self->active = false;
    if (!self->timers.empty()) self->unknown = true;
    if (!returned || exception(*self) || self->unknown || self->outputs != 1)
        return fail(error, WARLOCK_POLICY_PROCESSING_UNKNOWN, "Original policy processing lacks its exact owned output");
    *result = g_strdup(self->latest.c_str()); return TRUE;
}

WarlockPreviewPolicy* warlock_preview_policy_new(const char* source, gsize length, GError** error) {
    if (!source || !length || length > budget || std::memchr(source, '\0', length) || !g_utf8_validate(source, length, nullptr)) {
        fail(error, WARLOCK_POLICY_INVALID_INPUT, "Held bounded compiled policy source required"); return nullptr;
    }
    auto self = std::make_unique<WarlockPreviewPolicy>();
    g_autoptr(JSCValue) timeout = jsc_value_new_function(self->context,"setTimeout",G_CALLBACK(schedule),self.get(),nullptr,G_TYPE_DOUBLE,2,JSC_TYPE_VALUE,G_TYPE_DOUBLE);
    g_autoptr(JSCValue) clear_timeout = jsc_value_new_function(self->context,"clearTimeout",G_CALLBACK(cancel_timer),self.get(),nullptr,G_TYPE_NONE,1,G_TYPE_DOUBLE);
    jsc_context_set_value(self->context,"setTimeout",timeout);
    jsc_context_set_value(self->context,"clearTimeout",clear_timeout);
    g_autoptr(JSCValue) evaluated = jsc_context_evaluate_with_source_uri(self->context, source, length, "warlock-native-preview-policy", 1);
    if (!evaluated || exception(*self)) { fail(error, WARLOCK_POLICY_INVALID_INPUT, "Held compiled policy cannot initialize"); return nullptr; }
    g_autoptr(JSCValue) elm = jsc_context_get_value(self->context, "Elm");
    if (!elm || !jsc_value_is_object(elm)) { fail(error, WARLOCK_POLICY_INVALID_INPUT, "Compiled Elm policy export required"); return nullptr; }
    g_autoptr(JSCValue) program = jsc_value_object_get_property(elm, "NativePreviewPolicy");
    if (!program || !jsc_value_is_object(program)) { fail(error, WARLOCK_POLICY_INVALID_INPUT, "Original NativePreviewPolicy export required"); return nullptr; }
    g_autoptr(JSCValue) init = jsc_value_object_get_property(program, "init");
    if (!init || !jsc_value_is_function(init)) { fail(error, WARLOCK_POLICY_INVALID_INPUT, "Compiled worker initializer required"); return nullptr; }
    g_autoptr(JSCValue) app = jsc_value_function_callv(init, 0, nullptr);
    if (!app || exception(*self) || !jsc_value_is_object(app)) {
        auto* detail = jsc_context_get_exception(self->context);
        const auto message = std::string("Original Elm worker initialization failed: ") + (detail ? jsc_exception_get_message(detail) : "missing application");
        fail(error, WARLOCK_POLICY_INVALID_INPUT, message.c_str()); return nullptr;
    }
    g_autoptr(JSCValue) ports = jsc_value_object_get_property(app, "ports");
    if (!ports || !jsc_value_is_object(ports)) { fail(error, WARLOCK_POLICY_INVALID_INPUT, "Original worker ports required"); return nullptr; }
    g_autoptr(JSCValue) incoming = jsc_value_object_get_property(ports, "incoming");
    g_autoptr(JSCValue) outgoing = jsc_value_object_get_property(ports, "outgoing");
    if (!incoming || !outgoing || !jsc_value_is_object(incoming) || !jsc_value_is_object(outgoing)) { fail(error, WARLOCK_POLICY_INVALID_INPUT, "Original worker channel objects required"); return nullptr; }
    self->incoming = jsc_value_object_get_property(incoming, "send");
    self->unsubscribe = jsc_value_object_get_property(outgoing, "unsubscribe");
    g_autoptr(JSCValue) subscribe = jsc_value_object_get_property(outgoing, "subscribe");
    if (exception(*self) || !jsc_value_is_function(self->incoming) || !jsc_value_is_function(self->unsubscribe) || !jsc_value_is_function(subscribe)) {
        fail(error, WARLOCK_POLICY_INVALID_INPUT, "Original worker native ports required"); return nullptr;
    }
    self->sink = jsc_value_new_function(self->context, "ownedPolicyOutput", G_CALLBACK(output), self.get(), nullptr, G_TYPE_NONE, 1, JSC_TYPE_VALUE);
    JSCValue* parameters[] = {self->sink};
    g_autoptr(JSCValue) subscribed = jsc_value_function_callv(subscribe, 1, parameters);
    g_autofree char* initial = nullptr;
    if (!subscribed || exception(*self) || !warlock_preview_policy_invoke(self.get(), "{\"kind\":\"status\",\"value\":null}", &initial, error)) return nullptr;
    return self.release();
}

gboolean warlock_preview_policy_visual_projection(WarlockPreviewPolicy* self, char** result, GError** error) {
    if (result) *result = nullptr;
    if (!self || !result) return fail(error, WARLOCK_POLICY_INVALID_INPUT, "Owned policy and visual output required");
    if (self->creator != g_thread_self()) return fail(error, WARLOCK_POLICY_WRONG_THREAD, "Original policy creator thread required");
    if (self->unknown || self->active) return fail(error, WARLOCK_POLICY_PROCESSING_UNKNOWN, "Uncertain or inflight policy has no current visual proof");
    if (!self->controlled) return fail(error, WARLOCK_POLICY_NO_VISUAL_AUTHORITY, "Original open native visual realm required");
    g_autoptr(JsonParser) parser = json_parser_new();
    if (!json_parser_load_from_data(parser, self->latest.c_str(), self->latest.size(), nullptr)) {
        self->unknown = true;
        return fail(error, WARLOCK_POLICY_PROCESSING_UNKNOWN, "Owned current visual custody is uncertain");
    }
    auto* root = json_parser_get_root(parser);
    auto* object = JSON_NODE_HOLDS_OBJECT(root) ? json_node_get_object(root) : nullptr;
    auto* visual = object ? json_object_get_member(object, "visuals") : nullptr;
    auto* fields = visual && JSON_NODE_HOLDS_OBJECT(visual) ? json_node_get_object(visual) : nullptr;
    if (!exact(fields, {"visualProtocol", "kind", "binding", "receiverEpoch", "surface", "previews"})) {
        self->unknown = true;
        return fail(error, WARLOCK_POLICY_PROCESSING_UNKNOWN, "Exact owned visual projection required");
    }
    // Serialize a detached native byte copy. Never expose the private diagnostic
    // models/commands/metadata or invoke ports while answering a readonly query.
    *result = json_to_string(visual, FALSE);
    return TRUE;
}

gboolean warlock_preview_policy_close(WarlockPreviewPolicy* self, GError** error) {
    if (!self) return fail(error, WARLOCK_POLICY_INVALID_INPUT, "Owned policy required");
    if (self->creator != g_thread_self()) return fail(error, WARLOCK_POLICY_WRONG_THREAD, "Original policy creator thread required");
    if (self->unknown || self->active) return fail(error, WARLOCK_POLICY_PROCESSING_UNKNOWN, "Uncertain policy cannot be reconstructed or discarded");
    if (!self->empty || !self->ingress_empty || !self->timers.empty() || self->blocked || (self->controlled && !self->closed))
        return fail(error, WARLOCK_POLICY_NOT_CLOSED, "Original policy requires empty ingress/membership and trusted native close");
    JSCValue* parameters[] = {self->sink};
    g_autoptr(JSCValue) unsubscribed = jsc_value_function_callv(self->unsubscribe, 1, parameters);
    if (!unsubscribed || exception(*self)) return fail(error, WARLOCK_POLICY_PROCESSING_UNKNOWN, "Original policy callback detachment is uncertain");
    delete self; return TRUE;
}
