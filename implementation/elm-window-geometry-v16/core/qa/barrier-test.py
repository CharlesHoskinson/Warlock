"""Actual extracted request/callback lifecycle, with fake Wayland transport only."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'qa/xdg-max-client.c'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    sys.path.insert(0, '/home/hoskinson/window-integration-qa')
    from qa_launch import require_qa_scope
    qa_scope = require_qa_scope()
    out = ROOT / 'qa' / ('barrier-test-' + str(time.time_ns()))
    out.mkdir(mode=0o700)
    inputs = out / 'inputs'
    inputs.mkdir(mode=0o700)
    hashes = {str(path): digest(path) for path in [SOURCE, Path(__file__).resolve()]}
    for path in hashes:
        target = inputs / Path(path).name
        shutil.copy2(path, target)
        target.chmod(0o400)
    source = (inputs / SOURCE.name).read_text()
    types = source[source.index('struct client;'):source.index('static uint64_t stamp(')]
    events = source[source.index('static uint64_t stamp('):source.index('static void remove_buffer(')]
    logic = source[source.index('static void remove_barrier('):source.index('static void stdin_ready(')]
    teardown = 'while (client.barriers) remove_barrier(client.barriers);'
    if source.count(teardown) != 1:
        raise RuntimeError('Actual teardown anchor changed')
    mock = r'''
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
struct wl_callback;
struct wl_callback_listener { void (*done)(void*, struct wl_callback*, uint32_t); };
struct wl_callback { const struct wl_callback_listener *listener; void *data; bool destroyed; };
static struct wl_callback callbacks[64];
static unsigned creates, destroys, mutations, doubles;
struct wl_callback *wl_display_sync(struct wl_display *display);
void wl_callback_destroy(struct wl_callback *callback);
int wl_callback_add_listener(struct wl_callback *callback, const struct wl_callback_listener *listener, void *data);
void xdg_toplevel_set_maximized(struct xdg_toplevel *toplevel);
void xdg_toplevel_unset_maximized(struct xdg_toplevel *toplevel);
'''
    # Tags must be declared at file scope rather than only within prototypes.
    mock = mock.replace('struct wl_callback;\n', 'struct wl_display; struct xdg_toplevel;\nstruct wl_callback;\n')
    mock_functions = r'''
struct wl_callback *wl_display_sync(struct wl_display *display) {
    (void)display;
    if (creates >= 64) return NULL;
    return &callbacks[creates++];
}
void wl_callback_destroy(struct wl_callback *callback) {
    if (callback->destroyed) { ++doubles; return; }
    callback->destroyed = true; ++destroys;
}
int wl_callback_add_listener(struct wl_callback *callback, const struct wl_callback_listener *listener, void *data) {
    callback->listener = listener; callback->data = data; return 0;
}
void xdg_toplevel_set_maximized(struct xdg_toplevel *toplevel) { (void)toplevel; ++mutations; }
void xdg_toplevel_unset_maximized(struct xdg_toplevel *toplevel) { (void)toplevel; ++mutations; }
static void begin(const char *name) {
    memset(callbacks, 0, sizeof callbacks); creates = destroys = mutations = doubles = 0;
    printf("{\"case\":\"%s\"}\n", name);
}
static void summary(struct client *client, const char *phase) {
    unsigned linked = 0; for (struct barrier *entry = client->barriers; entry; entry = entry->next) ++linked;
    printf("{\"summary\":\"%s\",\"creates\":%u,\"destroys\":%u,\"mutations\":%u,\"doubles\":%u,\"outstanding\":%u,\"linked\":%u,\"quit\":%s,\"failed\":%s}\n",
           phase, creates, destroys, mutations, doubles, client->outstanding_barriers, linked,
           client->quit ? "true" : "false", client->failed ? "true" : "false");
}
static void complete(unsigned index) {
    struct wl_callback *callback = &callbacks[index];
    if (callback->destroyed || !callback->listener) { ++doubles; return; }
    callback->listener->done(callback->data, callback, 1000 + index);
}
'''
    harness = r'''
static void cleanup(struct client *client) { TEARDOWN }
int main(void) {
    begin("multiple-out-of-order");
    struct client first = {.ready=true,.serial=101,.acked=101,.width=320,.height=180};
    execute(&first, "maximize");
    first.serial = 202; execute(&first, "unmaximize");
    first.serial = 303; execute(&first, "sync");
    summary(&first, "before-completion");
    first.serial = 999;
    complete(2); complete(0); complete(1);
    summary(&first, "after-completion");
    cleanup(&first); summary(&first, "after-cleanup");

    begin("limit-before-ninth-mutation");
    struct client full = {.ready=true,.serial=88,.acked=88,.width=320,.height=180};
    for (unsigned index = 0; index < 8; ++index) execute(&full, "maximize");
    summary(&full, "at-eight");
    execute(&full, "unmaximize"); summary(&full, "after-ninth");
    cleanup(&full); summary(&full, "after-cleanup");

    begin("quit-teardown-once");
    struct client quit = {.ready=true,.serial=77,.acked=77,.width=320,.height=180};
    execute(&quit, "maximize"); execute(&quit, "unmaximize"); execute(&quit, "quit");
    cleanup(&quit); summary(&quit, "after-cleanup");
    cleanup(&quit); summary(&quit, "second-cleanup");

    begin("inspect-local-only");
    struct client local = {.ready=true,.serial=55,.acked=55,.width=320,.height=180};
    execute(&local, "inspect"); summary(&local, "after-inspect");
    cleanup(&local);
    return 0;
}
'''.replace('TEARDOWN', teardown.replace('client.', 'client->'))
    report = {'passed': False, 'scope': 'actual extracted client barrier lifecycle with mocked transport; no Wayland server/GUI or display claim',
              'qaScope': qa_scope, 'sources': hashes, 'checks': [], 'mutants': []}
    compiler = Path('/usr/bin/cc').resolve()
    report['compiler'] = {'path': str(compiler), 'sha256': digest(compiler)}
    report['extraction'] = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in [('types', types), ('events', events), ('logic', logic), ('teardown', teardown)]}

    def run_case(name, case_logic):
        directory = out / name
        directory.mkdir(mode=0o700)
        path = directory / 'actual-barrier-fixture.c'
        path.write_text(mock + types + events + mock_functions + case_logic + harness)
        path.chmod(0o400)
        binary = directory / 'barrier-fixture'
        command = [str(compiler), '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-MD', '-MF', str(directory / 'dependencies.d'), str(path), '-o', str(binary)]
        compiled = subprocess.run(command, capture_output=True, text=True, timeout=60)
        (directory / 'compile.stdout').write_text(compiled.stdout)
        (directory / 'compile.stderr').write_text(compiled.stderr)
        if compiled.returncode:
            raise RuntimeError(name + ' actual-extraction compile failed')
        result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
        (directory / 'run.stdout').write_text(result.stdout)
        (directory / 'run.stderr').write_text(result.stderr)
        if result.returncode:
            raise RuntimeError(name + ' fixture failed before external oracle')
        rows = [json.loads(line) for line in result.stdout.splitlines()]
        return rows

    def oracle(rows):
        cases, current = {}, None
        for row in rows:
            if 'case' in row:
                current = row['case']; cases[current] = []
            else:
                assert current is not None, 'orphan production event'
                cases[current].append(row)
        assert set(cases) == {'multiple-out-of-order', 'limit-before-ninth-mutation', 'quit-teardown-once', 'inspect-local-only'}, 'missing concrete lifecycle case'
        multiple = cases['multiple-out-of-order']
        before = next(index for index, row in enumerate(multiple) if row.get('summary') == 'before-completion')
        assert not any(row.get('event') == 'server-barrier' for row in multiple[:before]), 'local event falsely claims server callback'
        requests = [row for row in multiple if row.get('event') == 'request']
        barriers = [row for row in multiple if row.get('event') == 'server-barrier']
        assert [(row['sequence'], row['command'], row['serial']) for row in requests] == [(1, 'maximize', 101), (2, 'unmaximize', 202), (3, 'sync', 303)], 'exact request ownership lost'
        assert [(row['requestSequence'], row['command'], row['requestSerial'], row['callbackData']) for row in barriers] == [(3, 'sync', 303, 1002), (1, 'maximize', 101, 1000), (2, 'unmaximize', 202, 1001)], 'out-of-order callbacks lost original keys'
        assert all(row['serial'] == 999 for row in barriers), 'current serial was confused with original serial'
        summaries = {row['summary']: row for row in multiple if 'summary' in row}
        assert summaries['before-completion']['outstanding'] == 3 and summaries['before-completion']['mutations'] == 2, 'explicit sync mutated window or lost outstanding entries'
        for phase in ['after-completion', 'after-cleanup']:
            row = summaries[phase]
            assert row['destroys'] == 3 and row['outstanding'] == row['linked'] == row['doubles'] == 0, 'callback completion did not retire exactly once'
        full = cases['limit-before-ninth-mutation']
        after = next(row for row in full if row.get('summary') == 'after-ninth')
        assert after['mutations'] == after['creates'] == after['outstanding'] == after['linked'] == 8 and after['failed'] and after['quit'], 'ninth request mutated before refusal'
        assert len([row for row in full if row.get('event') == 'request']) == 8, 'ninth mutating request was dispatched'
        assert [row.get('reason') for row in full if row.get('event') == 'refused'] == ['eight-outstanding-barrier-limit'], 'capacity refusal missing'
        final = next(row for row in full if row.get('summary') == 'after-cleanup')
        assert final['destroys'] == 8 and final['outstanding'] == final['linked'] == final['doubles'] == 0, 'full teardown leaked or double-destroyed'
        quit_rows = cases['quit-teardown-once']
        assert not any(row.get('event') == 'server-barrier' for row in quit_rows), 'teardown invented server callback'
        for row in quit_rows:
            if 'summary' in row:
                assert row['destroys'] == row['creates'] == 2 and row['outstanding'] == row['linked'] == row['doubles'] == 0 and row['quit'], 'normal/second cleanup was not exactly once'
        local = cases['inspect-local-only']
        assert [row.get('event') for row in local if 'event' in row] == ['inspect'], 'inspect became server receipt'
        last = local[-1]
        assert last['creates'] == last['mutations'] == last['outstanding'] == 0, 'inspect created mutating request'
        return ['exact-multiple-ownership', 'out-of-order-original-keys', 'sync-nonmutating', 'no-local-server-receipt', 'capacity-before-ninth-mutation', 'completion-destroys-once', 'normal-teardown-destroys-once', 'inspect-local-only']

    mutants = [
        ('local-receipt', 'if (!client->failed) queue_barrier(client, known);', 'if (!client->failed) { event(client, "server-barrier", extra); queue_barrier(client, known); }'),
        ('removed-pre-dispatch-bound', 'if (client->outstanding_barriers >= 8) { refuse(client, "eight-outstanding-barrier-limit"); return; }', '/* unsafe: no pre-dispatch capacity guard */'),
        ('current-sequence-replaces-original', 'barrier->request_sequence, barrier->request_serial, barrier->command, callback_data', 'barrier->client->sequence, barrier->request_serial, barrier->command, callback_data'),
        ('callback-not-destroyed', 'wl_callback_destroy(barrier->callback);', '(void)barrier->callback;'),
    ]
    try:
        report['witnesses'] = oracle(run_case('actual', logic))
        for name, old, new in mutants:
            if logic.count(old) != 1:
                raise RuntimeError('Mutation anchor changed: ' + name)
            rows = run_case('mutant-' + name, logic.replace(old, new))
            try:
                oracle(rows)
            except AssertionError as rejected:
                report['mutants'].append({'name': name, 'rejectedByExternalOracle': True, 'violatedWitness': str(rejected)})
            else:
                raise RuntimeError('Unsafe mutation survived actual oracle: ' + name)
        for path, expected in hashes.items():
            if digest(path) != expected:
                raise RuntimeError('Held source changed: ' + path)
        report['passed'] = len(report['mutants']) == 4
    except Exception as error:
        report['error'] = repr(error)
    report['artifacts'] = {str(path.relative_to(out)): digest(path) for path in sorted(out.rglob('*')) if path.is_file()}
    target = out / 'report.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'witnesses': len(report.get('witnesses', [])), 'rejectedMutants': len(report['mutants']), 'report': str(target), 'error': report.get('error')}), flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
