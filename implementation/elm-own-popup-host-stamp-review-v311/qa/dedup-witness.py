import hashlib, json, resource, subprocess, time
from pathlib import Path

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
root = Path(__file__).resolve().parents[1]
source = root / 'qa/preliminary/first-build-popup-native-stamp.h'
text = source.read_text()
start = text.index('    if (native_popup_stamp && native_popup_mapped_lease')
end = text.index('\n    if (native_popup_mapped_lease', start)
body = text[start:end]
out = root / 'qa' / ('dedup-' + str(time.time_ns()))
out.mkdir()
fixture = r'''
#include <glib.h>
#include <json-glib/json-glib.h>
#include "identity.h"
static JsonNode *native_popup_stamp;
static guint64 native_popup_mapped_lease=4;
static int emitted;
static gboolean surface_uint(JsonNode *node,guint64 *value) {
 *value=g_ascii_strtoull(json_node_get_string(node),NULL,10); return TRUE;
}
static void observe(PopupNativeIdentity identity) {
BODY
 ++emitted;
}
int main(void) {
 JsonObject *object=json_object_new();
 json_object_set_string_member(object,"publication","9");
 json_object_set_int_member(object,"popupSurface",37);
 json_object_set_int_member(object,"rootSurface",34);
 json_object_set_string_member(object,"topology","1");
 native_popup_stamp=json_node_new(JSON_NODE_OBJECT);json_node_take_object(native_popup_stamp,object);
 PopupNativeIdentity identity={.lease=4,.publication=9,.popup=37,.root=34,.topology=1};
 observe(identity);g_assert_cmpint(emitted,==,0);
 identity.topology=2;observe(identity);g_assert_cmpint(emitted,==,0);
 identity.root=38;observe(identity);g_assert_cmpint(emitted,==,0);
 identity.view=5;observe(identity);g_assert_cmpint(emitted,==,0);
 identity.publication=10;observe(identity);g_assert_cmpint(emitted,==,1);
 identity.publication=9;identity.lease=5;observe(identity);g_assert_cmpint(emitted,==,2);
 json_node_unref(native_popup_stamp);
 return 0;
}
'''.replace('BODY', body)
(out / 'fixture.c').write_text(fixture)
(out / 'identity.h').write_bytes((root / 'qa/preliminary/first-build-popup-native-identity.h').read_bytes())
flags = subprocess.check_output(['/usr/bin/pkg-config', '--cflags', '--libs', 'json-glib-1.0'], text=True).split()
compile_result = subprocess.run(['/usr/bin/cc', '-std=c11', '-Wall', str(out / 'fixture.c'), '-o', str(out / 'witness'), *flags], capture_output=True)
(out / 'compile.stderr').write_bytes(compile_result.stderr)
assert compile_result.returncode == 0
result = subprocess.run([str(out / 'witness')], capture_output=True)
(out / 'witness.stderr').write_bytes(result.stderr)
assert result.returncode == 0
report = {'passed': True, 'unsafeHistoricalDedupWitness': True, 'nativeAcceptance': False,
          'sourceSHA256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'scope': 'Actual first-build dedup block with real JSON/GLib; scope-change emission suppressed for topology/root/view; lease/publication controls emit. GTK lifecycle mocked.'}
(out / 'report.json').write_text(json.dumps(report, indent=2))
print(out / 'report.json')
