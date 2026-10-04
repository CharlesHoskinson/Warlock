"""Protected CPU build, actual private policy tests and rejected guard mutations."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    sys.path.insert(0, '/home/hoskinson/window-integration-qa')
    from qa_launch import require_qa_scope
    scope = require_qa_scope()
    out = ROOT / 'qa' / ('placement-test-' + str(time.time_ns()))
    out.mkdir(mode=0o700)
    inputs = out / 'inputs'
    inputs.mkdir(mode=0o700)
    paths = [ROOT / 'candidate/PlacementPolicy.hpp', ROOT / 'qa/placement-policy-test.cpp', Path(__file__).resolve()]
    hashes = {str(path): digest(path) for path in paths}
    for path in paths:
        target = inputs / path.name
        shutil.copy2(path, target)
        target.chmod(0o400)
    report = {'passed': False, 'scope': 'Private native placement policy prototype CPU only; no plugin mutation, native geometry acceptance, or Quint claim',
              'qaScope': scope, 'sources': hashes, 'checks': [], 'mutants': []}
    compiler = Path('/usr/bin/c++').resolve()
    report['compiler'] = {'path': str(compiler), 'sha256': digest(compiler)}
    report['contracts'] = {str(path): digest(path) for path in [REPO / 'docs/elm-roadmap/RIGHT-CLICK.md', REPO / 'docs/elm-roadmap/delivery/WINDOW-GEOMETRY-NEXT.md']}

    def command(name, args, expected):
        result = subprocess.run(args, cwd=out, capture_output=True, text=True, timeout=60)
        (out / (name + '.stdout')).write_text(result.stdout)
        (out / (name + '.stderr')).write_text(result.stderr)
        row = {'name': name, 'command': list(map(str, args)), 'exitCode': result.returncode, 'expectedExitCode': expected,
               'passed': result.returncode == expected}
        report['checks'].append(row)
        if not row['passed']:
            raise RuntimeError('Unexpected command result: ' + name)
        return result

    def compile_case(name, include, binary, dependencies=False):
        args = [str(compiler), '-std=c++20', '-O2', '-Wall', '-Wextra', '-Werror', '-I' + str(include)]
        dependency_path = out / 'policy.d' if dependencies else include / 'policy.d'
        args += ['-MD', '-MF', str(dependency_path)]
        args += [str(include / 'placement-policy-test.cpp'), '-o', str(binary)]
        command(name, args, 0)
        if str(include / 'PlacementPolicy.hpp') not in dependency_path.read_text():
            raise RuntimeError('Compiler did not select tested header: ' + name)

    text = (inputs / 'PlacementPolicy.hpp').read_text()
    mutants = [
        ('ignore-native-lifetime', 'a.lifetime_ == b.lifetime_', 'true'),
        ('ignore-incarnation', 'a.incarnation_ == b.incarnation_', 'true'),
        ('ignore-current-native-identity', 'if (!owningLiveIdentity || !(requested == *owningLiveIdentity))', 'if (!owningLiveIdentity)'),
        ('overwrite-first-original', 'for (const auto& entry : entries_) if (entry && entry->identity == requested) return Capture::Duplicate;',
         'for (auto& entry : entries_) if (entry && entry->identity == requested) { entry->original = original; return Capture::Duplicate; }'),
        ('evict-at-capacity', 'if (size_ == capacity) return Capture::Capacity;',
         'if (size_ == capacity) { entries_[0] = Entry{requested, scope, original}; return Capture::Captured; }'),
        ('ignore-workspace-id', 'a.workspace_ == b.workspace_', 'true'),
        ('ignore-workspace-generation', 'a.workspaceGeneration_ == b.workspaceGeneration_', 'true'),
        ('ignore-output-id', 'a.output_ == b.output_', 'true'),
        ('ignore-output-generation', 'a.outputGeneration_ == b.outputGeneration_', 'true'),
        ('admit-invalid-original', 'if (!original.logical.valid() || !original.visual.valid())', 'if (false)'),
        ('ignore-visual-validity', 'if (!original.logical.valid() || !original.visual.valid())', 'if (!original.logical.valid())'),
        ('retire-wrong-identity', 'entry->identity == identity', '(static_cast<void>(identity), true)'),
        ('invent-external-original', 'return std::nullopt; // Externally maximized or unknown original: explicit absence.',
         'return Original{{0,0,1,1},{0,0,1,1}}; // Unsafe invented original.'),
    ]
    try:
        command('compiler-version', [str(compiler), '--version'], 0)
        binary = out / 'placement-policy-test'
        compile_case('actual-header-compile', inputs, binary, True)
        result = command('actual-policy-tests', [str(binary)], 0)
        names = [line[5:] for line in result.stdout.splitlines() if line.startswith('PASS ')]
        if len(names) != 21 or len(set(names)) != 21 or 'CHECKS 21' not in result.stdout:
            raise RuntimeError('Expected 21 distinct actual policy witnesses')
        report['witnesses'] = names
        dependency_text = (out / 'policy.d').read_text().replace('\\\n', ' ')
        dependencies = dependency_text.split(':', 1)[1].split()
        report['dependencies'] = {str(Path(path).resolve()): digest(path) for path in sorted(set(dependencies))}
        for name, old, new in mutants:
            count = text.count(old)
            expected_count = 2 if name == 'ignore-current-native-identity' else 1
            if count != expected_count:
                raise RuntimeError('Mutation anchor changed: ' + name)
            directory = out / ('mutant-' + name)
            directory.mkdir(mode=0o700)
            header = directory / 'PlacementPolicy.hpp'
            header.write_text(text.replace(old, new))
            header.chmod(0o400)
            fixture = directory / 'placement-policy-test.cpp'
            shutil.copy2(inputs / 'placement-policy-test.cpp', fixture)
            fixture.chmod(0o400)
            mutant_binary = directory / 'placement-policy-test'
            compile_case(name + '-compile', directory, mutant_binary)
            failed = command(name + '-unsafe-rejected', [str(mutant_binary)], 1)
            failure = [line for line in failed.stdout.splitlines() if line.startswith('FAIL ')]
            if len(failure) != 1:
                raise RuntimeError('Unsafe mutant lacks explicit violated witness: ' + name)
            report['mutants'].append({'name': name, 'sourceSHA256': digest(header), 'fixtureSHA256': digest(fixture), 'selectedHeaderDependencySHA256': digest(directory / 'policy.d'), 'exitCode': 1, 'violatedWitness': failure[0]})
        for path, expected in hashes.items():
            if digest(path) != expected:
                raise RuntimeError('Live source changed during CPU evidence: ' + path)
        report['passed'] = len(report['mutants']) == 13 and all(row['passed'] for row in report['checks'])
    except Exception as error:
        report['error'] = repr(error)
    report['artifacts'] = {str(path.relative_to(out)): digest(path) for path in sorted(out.rglob('*')) if path.is_file()}
    target = out / 'report.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'witnesses': len(report.get('witnesses', [])), 'rejectedMutants': len(report['mutants']), 'report': str(target), 'error': report.get('error')}), flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
