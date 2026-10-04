import hashlib, json, resource, shlex, shutil, subprocess, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa' / ('test-' + str(time.time_ns()))
OUT.mkdir()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r = {'passed': False, 'nativeAcceptance': False, 'scope': 'Compiled production CensusBudget bounds and real libwayland resource identity controls; no owning compositor/grab execution', 'commands': [], 'mutants': []}
def run(name, args):
    p = subprocess.run(args, capture_output=True, timeout=60)
    (OUT / (name + '.stdout')).write_bytes(p.stdout)
    (OUT / (name + '.stderr')).write_bytes(p.stderr)
    r['commands'].append({'name': name, 'args': args, 'exitCode': p.returncode})
    return p.returncode
try:
    inputs = [ROOT/'native/census-budget.hpp', ROOT/'qa/budget-test.cpp', Path(__file__)]
    for p in inputs: shutil.copy2(p, OUT/p.name)
    r['inputs'] = {str(p): sha(p) for p in inputs}
    flags = shlex.split(subprocess.check_output(['/usr/bin/pkg-config', '--cflags', '--libs', 'wayland-server'], text=True))
    base = ['/usr/bin/c++', '-std=c++23', '-Wall', '-Wextra', '-Werror', '-I', str(OUT), str(OUT/'budget-test.cpp'), *flags]
    assert run('compile', [*base, '-o', str(OUT/'test')]) == 0
    assert run('actual', [str(OUT/'test')]) == 0
    original = (OUT/'census-budget.hpp').read_text()
    for name, old, new in [('duplicate', '!seen.emplace(client, id).second', '(seen.emplace(client, id), false)'), ('surface-bound', 'seen.size() >= 4096', 'seen.size() > 4096'), ('member-bound', '++memberCount > 256', '++memberCount > 257'), ('output-bound', 'bytes > 60000', 'bytes > 60001')]:
        assert original.count(old) == 1
        (OUT/'census-budget.hpp').write_text(original.replace(old, new))
        assert run(name+'-compile', [*base, '-o', str(OUT/name)]) == 0
        code = run(name+'-witness', [str(OUT/name)])
        assert code != 0
        r['mutants'].append({'name': name, 'exitCode': code, 'killed': True})
    (OUT/'census-budget.hpp').write_text(original)
    for p, digest in r['inputs'].items(): assert sha(p) == digest
    deps = subprocess.check_output(['/usr/bin/ldd', str(OUT/'test')], text=True)
    assert 'not found' not in deps
    r['linkedLibraries'] = {str(Path(w).resolve()): sha(Path(w).resolve()) for line in deps.splitlines() for w in line.split() if w.startswith('/') and Path(w).is_file()}
    r['tools'] = {str(Path(p).resolve()): sha(Path(p).resolve()) for p in ['/usr/bin/c++', '/usr/bin/pkg-config', '/usr/bin/ldd']}
    r['passed'] = True
except Exception as e: r['error'] = repr(e)
r['artifacts'] = {str(p.relative_to(OUT)): sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r, indent=2)+'\n')
print(json.dumps({'passed': r['passed'], 'report': str(OUT/'report.json'), 'error': r.get('error')}))
raise SystemExit(not r['passed'])
