"""Protected structural validation of the additive right-click candidate only.

This does not execute a GUI or establish implementation/native acceptance.
Run through the protected qa_run.py launcher after the author declares stability.
"""
import datetime
import hashlib
import json
import os
import re
import resource
import subprocess
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
CHANGE = REPO / 'openspec/changes/elm-right-click'
REPORT = ROOT / 'delivery/right-click-validation.json'
IDENTITY = r'ELM-RC-\d{3}'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(text):
    return ' '.join(text.split())


def main():
    assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    def requirements(text, source):
        headings = list(re.finditer(r'^### Requirement: (' + IDENTITY + r')(?:\s+[^\n]*)?$', text, re.M))
        result = {}
        for index, heading in enumerate(headings):
            identity = heading.group(1)
            check(identity not in result, source + ': duplicate requirement ' + identity)
            body = text[heading.end():headings[index+1].start() if index+1 < len(headings) else len(text)]
            scenarios = list(re.finditer(r'^#### Scenario: (' + IDENTITY + r') ([^\n]+)$', body, re.M))
            normative = normalized(body[:scenarios[0].start()] if scenarios else body)
            check('SHALL' in normative, identity + ': missing normative SHALL statement')
            check(bool(scenarios), identity + ': no acceptance scenarios')
            cases = {}
            for number, scenario in enumerate(scenarios):
                owner, name = scenario.groups()
                check(owner == identity, source + ': scenario under wrong requirement ' + owner + ' ' + name)
                key = owner + ' ' + name.strip()
                check(key not in cases, source + ': duplicate scenario ' + key)
                content = body[scenario.end():scenarios[number+1].start() if number+1 < len(scenarios) else len(body)]
                markers = list(re.finditer(r'^- (GIVEN|WHEN|THEN) (.*)$', content, re.M))
                check([marker.group(1) for marker in markers] == ['GIVEN', 'WHEN', 'THEN'], source + ': invalid Given/When/Then ' + key)
                values = {}
                for n, marker in enumerate(markers):
                    value = normalized(content[marker.start(2):markers[n+1].start() if n+1 < len(markers) else len(content)])
                    check(bool(value), source + ': empty scenario clause ' + key)
                    values[marker.group(1)] = value
                cases[key] = values
            result[identity] = {'normative': normative, 'scenarios': cases}
        check(bool(result), source + ': no ELM-RC requirements')
        return result

    files = [ROOT/'RIGHT-CLICK.md', CHANGE/'proposal.md', CHANGE/'tasks.md', *sorted((CHANGE/'specs').glob('*/spec.md')), Path(__file__)]
    before = {}
    cli = {}
    doc = {}
    specs = {}
    mappings = {}
    links = 0
    try:
        for file in files:
            check(file.is_file(), 'Missing input ' + str(file.relative_to(REPO)))
        check(len(list((CHANGE/'specs').glob('*/spec.md'))) > 0, 'Missing OpenSpec requirement files')
        if errors:
            raise ValueError('Required inputs are incomplete')
        before = {str(file.relative_to(REPO)): sha(file) for file in files}
        doc = requirements((ROOT/'RIGHT-CLICK.md').read_text(), 'RIGHT-CLICK.md')
        for file in sorted((CHANGE/'specs').glob('*/spec.md')):
            parsed = requirements(file.read_text(), str(file.relative_to(REPO)))
            check(not (set(specs) & set(parsed)), 'Duplicate ELM-RC requirement across specification files')
            specs.update(parsed)
        check(set(doc) == set(specs), 'Roadmap/OpenSpec requirement IDs differ')
        for identity in sorted(set(doc) & set(specs)):
            check(doc[identity] == specs[identity], identity + ': normative statement or acceptance scenarios diverge')
        case_ids = [case for requirement in specs.values() for case in requirement['scenarios']]
        check(len(case_ids) == len(set(case_ids)), 'Duplicate acceptance scenario identities')
        tasks = (CHANGE/'tasks.md').read_text()
        declared_stages = set(re.findall(r'^- \[[ x]\] (RC-P\d+):', tasks, re.M))
        check(bool(declared_stages), 'No implementation task stages')
        # Requirement-to-stage table is separate from the human-readable stage tasks.
        for row in re.findall(r'^\|\s*(' + IDENTITY + r')\s*\|([^\n]+)$', tasks, re.M):
            identity, content = row
            check(identity not in mappings, 'Duplicate task mapping for ' + identity)
            stages = re.findall(r'\bRC-P\d+\b', content)
            check(bool(stages) and set(stages) <= declared_stages, identity + ': missing/unknown mapped task stages')
            mappings[identity] = stages
        check(set(mappings) == set(specs), 'Task mappings do not cover exactly the ELM-RC requirements')
        for file in files:
            if file.suffix != '.md':
                continue
            for link in re.findall(r'\]\(([^)]+)\)', file.read_text()):
                if '://' in link or link.startswith('#'):
                    continue
                target = unquote(link.split('#', 1)[0].strip('<>'))
                check(bool(target) and (file.parent/target).exists(), str(file.relative_to(REPO)) + ': broken local link ' + link)
                links += 1
        command = ['npm', 'exec', '--yes', '--package=@fission-ai/openspec@1.14.0', '--', 'openspec', 'validate', 'elm-right-click', '--type', 'change', '--strict', '--json', '--no-interactive']
        env = dict(os.environ, OPENSPEC_TELEMETRY='0', DO_NOT_TRACK='1', CI='true')
        process = subprocess.run(command, cwd=REPO, env=env, capture_output=True, text=True, timeout=180)
        cli = {'command': command, 'exitCode': process.returncode, 'stdout': process.stdout, 'stderr': process.stderr}
        check(process.returncode == 0, 'OpenSpec strict validation failed')
        try:
            cli['json'] = json.loads(process.stdout)
        except json.JSONDecodeError:
            errors.append('OpenSpec did not return valid JSON')
        for file in files:
            check(sha(file) == before[str(file.relative_to(REPO))], 'Input changed during validation: ' + str(file.relative_to(REPO)))
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        errors.append(type(error).__name__ + ': ' + str(error))
    report = {
        'observedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Additive right-click planning structure, exact requirement/scenario mirrors, task mapping and local links; no implementation/native acceptance',
        'baselineLedgerModified': False,
        'requirements': len(specs),
        'acceptanceScenarios': sum(len(requirement['scenarios']) for requirement in specs.values()),
        'taskMappings': mappings,
        'localLinksChecked': links,
        'inputs': before,
        'openspec': cli,
        'errors': errors,
        'passed': not errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
