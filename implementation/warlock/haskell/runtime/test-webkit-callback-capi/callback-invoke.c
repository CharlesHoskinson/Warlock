#include <glib-object.h>

void warlock_fixture_notify(GClosureNotify callback, gpointer data, GClosure *closure)
{
    callback(data, closure);
}

void warlock_fixture_callback(GCallback callback)
{
    callback();
}

void warlock_fixture_marshal(GClosureMarshal callback, GClosure *closure,
                             GValue *result, guint count, const GValue *values,
                             gpointer hint, gpointer data)
{
    callback(closure, result, count, values, hint, data);
}

int warlock_fixture_valid_marshal(GClosureMarshal callback)
{
    if (callback == NULL)
        return 0;

    GClosure *closure = g_closure_new_simple(sizeof(GClosure), NULL);
    if (closure == NULL)
        return 0;
    g_closure_ref(closure);
    g_closure_sink(closure);

    GValue argument = G_VALUE_INIT;
    GValue result = G_VALUE_INIT;
    g_value_init(&argument, G_TYPE_INT);
    g_value_set_int(&argument, 42);
    g_value_init(&result, G_TYPE_INT);
    callback(closure, &result, 1, &argument, NULL, NULL);
    g_value_unset(&result);
    g_value_unset(&argument);
    g_closure_unref(closure);
    return 1;
}
