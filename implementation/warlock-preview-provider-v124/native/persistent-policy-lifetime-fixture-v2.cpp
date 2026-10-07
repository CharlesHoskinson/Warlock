#include "elm-preview-policy.h"
#include <json-glib/json-glib.h>
#include <fstream>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>

struct Call {
    WarlockPreviewPolicy* owner;
    const char* input;
    bool close;
    bool visual{};
    gboolean ok{};
    char* output{};
    GError* error{};
};
static gpointer foreign(gpointer data) {
    auto& call = *static_cast<Call*>(data);
    call.ok = call.close ? warlock_preview_policy_close(call.owner, &call.error)
                        : call.visual ? warlock_preview_policy_visual_projection(call.owner, &call.output, &call.error)
                        : warlock_preview_policy_invoke(call.owner, call.input, &call.output, &call.error);
    return nullptr;
}
static void reply(gboolean ok, GError* error, const char* output, bool held) {
    auto* object = json_object_new();
    json_object_set_boolean_member(object, "ok", ok);
    json_object_set_int_member(object, "code", error ? error->code : 0);
    json_object_set_boolean_member(object, "held", held);
    if (output) {
        g_autoptr(JsonParser) parser = json_parser_new();
        if (!json_parser_load_from_data(parser, output, -1, nullptr)) std::abort();
        json_object_set_member(object, "projection", json_node_copy(json_parser_get_root(parser)));
    }
    g_autoptr(JsonNode) node = json_node_new(JSON_NODE_OBJECT);
    json_node_take_object(node, object);
    g_autoptr(JsonGenerator) generator = json_generator_new();
    json_generator_set_root(generator, node);
    g_autofree char* wire = json_generator_to_data(generator, nullptr);
    std::cout << wire << std::endl;
}
int main(int argc, char** argv) {
    if (argc < 2 || argc > 3) return 2;
    std::ifstream stream(argv[1]); std::ostringstream bytes; bytes << stream.rdbuf();
    const auto source = bytes.str();
    GError* error = nullptr;
    auto* policy = warlock_preview_policy_new(source.data(), source.size(), &error);
    if (argc == 3 && std::string(argv[2]) == "construct") {
        reply(policy != nullptr, error, nullptr, policy != nullptr); g_clear_error(&error);
        if (policy && !warlock_preview_policy_close(policy, &error)) {
            g_clear_error(&error); return 3;
        }
        return 0;
    }
    if (!policy) { reply(FALSE, error, nullptr, false); g_clear_error(&error); return 3; }
    std::string line;
    while (std::getline(std::cin, line)) {
        g_autoptr(JsonParser) parser = json_parser_new();
        if (!json_parser_load_from_data(parser, line.c_str(), -1, nullptr)) return 4;
        auto* object = json_node_get_object(json_parser_get_root(parser));
        const std::string op = json_object_get_string_member(object, "op");
        const char* input = json_object_has_member(object, "input") ? json_object_get_string_member(object, "input") : nullptr;
        gboolean ok = FALSE; char* output = nullptr;
        if (op == "close") {
            ok = warlock_preview_policy_close(policy, &error);
            if (ok) policy = nullptr;
        } else if (op == "foreign-invoke" || op == "foreign-close" || op == "foreign-visual") {
            Call call{policy, input, op == "foreign-close", op == "foreign-visual"};
            auto* thread = g_thread_new("policy-foreign-creator", foreign, &call);
            g_thread_join(thread); ok = call.ok; output = call.output; error = call.error;
            if (call.close && ok) policy = nullptr;
        } else if (op == "invoke") {
            ok = warlock_preview_policy_invoke(policy, input, &output, &error);
        } else if (op == "visual") {
            ok = warlock_preview_policy_visual_projection(policy, &output, &error);
        } else if (op == "visual-copy") {
            char* first = nullptr;
            ok = warlock_preview_policy_visual_projection(policy, &first, &error);
            if (ok) {
                const std::string original(first);
                std::memset(first, '!', original.size());
                ok = warlock_preview_policy_visual_projection(policy, &output, &error);
                if (!ok || !output || original != output || first == output) std::abort();
            }
            g_free(first);
        } else if (op == "missing-visual-output") {
            ok = warlock_preview_policy_visual_projection(policy, nullptr, &error);
        } else if (op == "missing-output") {
            ok = warlock_preview_policy_invoke(policy, input, nullptr, &error);
        } else return 4;
        reply(ok, error, output, policy != nullptr);
        g_free(output); g_clear_error(&error);
    }
    // Every successful trace must destroy its owner normally; process exit is
    // never substituted for the close guard or an unknown policy's retirement.
    return policy ? 5 : 0;
}
