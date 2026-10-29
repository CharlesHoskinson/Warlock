#!/usr/bin/env python3
"""Private UX-029 launcher search, qualified current tuple; root runs QA."""
import ast,hashlib,importlib.util,os,pathlib,resource,sys
HERE=pathlib.Path(__file__).resolve().parent
BASE=HERE.parent
FRAMEWORK=BASE/'taskbar-new-instance/compiled-runtime.py'
FRAMEWORK_SHA='bb12e30c5e59c653441e18e580f5404f89ddb34a7d6cdb26629c6a0f63af5f4e'
CANDIDATE=BASE/'launcher-pending-source-qualified-v1/fresh_candidate.py'
CANDIDATE_SHA='9047be2e62947e68621b1bb7fa32403dd930b97cba444d67c82e501a1c4b311f'
BRANCH=HERE/'search-branch.txt'
BRANCH_SHA='0a7cd9efd24eb3c0b79db441b84c585a60d1a3980ac29ca2508a8a963b308a90'
RECIPIENT=BASE/'launcher-refused-painted-v1/launch-recipient.py'
RECIPIENT_SHA='50d58e0c387c02c2db555405bff31132042e211854d8e4b19d6a5b4e9e97984a'
AT_GUARD=BASE/'at-prefix-host/guard-v3.py'
AT_GUARD_SHA='117e56afe2a72e686fa2fcaedd18204da593af51e8be495764cd7e75d500d148'
AT_ACTION=BASE/'taskbar-pin-semantics/at-action.py'
AT_ACTION_SHA='e4ce2c23b852a1bea40c27d0c47f68e810705531a8e41f8ae8ae046ce76cb157'
def checked(path,expected):
    cursor=pathlib.Path(path.anchor)
    for part in path.parts[1:]:
        cursor/=part
        if cursor.is_symlink():raise RuntimeError('reviewed path contains symlink')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected:raise RuntimeError('reviewed input changed: '+str(path))
    return raw
def one(source,old,new):
    if source.count(old)!=1:raise RuntimeError('missing or duplicated framework binding')
    return source.replace(old,new)
def transform(raw,branch):
    source=raw.decode()
    changes={
      "ACCESSIBILITY=True\n": "ACCESSIBILITY=True\n",
      "if sys.argv[1:] not in ([], ['--new-instance']):raise SystemExit('Only explicit new-instance mode is supported')\nsys.argv[1:]=['--new-instance']": "if sys.argv[1:] != ['--launcher-search']:raise SystemExit('Only --launcher-search is supported')",
      "adapter=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-qa/fresh_candidate.py')": "adapter=pathlib.Path("+repr(str(CANDIDATE))+")",
      "assert sha(adapter)=='cb29ebe89b051223037264a366b9616815284b88e3cc452bc18a8993680eb8ab'": "assert sha(adapter)=="+repr(CANDIDATE_SHA),
      "spec=importlib.util.spec_from_file_location('fresh_candidate',adapter);host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)": "adapter_bytes=adapter.read_bytes();assert hashlib.sha256(adapter_bytes).hexdigest()=="+repr(CANDIDATE_SHA)+";spec=importlib.util.spec_from_loader('fresh_candidate',loader=None);host=importlib.util.module_from_spec(spec);host.__file__=str(adapter);exec(compile(adapter_bytes,str(adapter),'exec'),host.__dict__)",
      "OUT=pathlib.Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance')/('native-primary-keyboard-'+str(time.time_ns()));OUT.mkdir(parents=True)": "OUT=LAUNCH_DIR/('native-launcher-'+LAUNCHER_MODE+'-'+str(time.time_ns()));OUT.mkdir(parents=True)",
      "desktop=catalog_root/'warlock-files.desktop';desktop.write_text('[Desktop Entry]\\nType=Application\\nName=Files\\nGenericName=File manager\\nKeywords=folders;documents;\\nExec=/usr/bin/true\\n')": "LAUNCH_EVENTS=OUTPUT/'launcher-recipient.jsonl';desktop=catalog_root/'warlock-files.desktop';desktop.write_text('[Desktop Entry]\\nType=Application\\nName=Files\\nGenericName=File manager\\nKeywords=folders;documents;\\nExec=/usr/bin/python3 -B '+str(LAUNCH_RECIPIENT)+' '+str(LAUNCH_EVENTS)+'\\n')",
      "if SEARCH:report.update(requirements=['ELM-UI-005','ELM-UX-029'],scenarios=['search-no-match','search-race','search-refused','launcher-refused'],scope='Actual current query and private catalog, native typing/Enter refusal and no duplicate launch; AT/IME and popup physical presentation acceptance remain pending',popupPresentationAccepted=False)": "if SEARCH:report.update(requirements=['ELM-UI-005'],scenarios=['search-refused'],scope='Current query and actual refusal with AT feedback and accessible retry; focus policy and painted evidence require review',popupPresentationAccepted=False,launcherAcceptance=False)"}
    for old,new in changes.items():source=one(source,old,new)
    anchor='    elif IME:\n';end='   elif DENSEPICKER:\n'
    if source.count(anchor)!=1 or source.count(end)!=1:raise RuntimeError('search branch scope changed')
    a=source.index(anchor);start=source.index('    else:\n     click(wait(lambda:(projection() or {}).get(\'openApplications\')));wait(',a);stop=source.index(end,start)
    if source.count(source[start:stop])!=1:raise RuntimeError('search branch identity ambiguous')
    source=source[:start]+branch.decode()+source[stop:]
    ast.parse(source)
    return source
def main():
    if sys.argv[1:] != ['--refused'] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':raise SystemExit('Use --refused in protected no-bytecode scope')
    mode=sys.argv[1][2:]
    sys.path.insert(0,'/home/charles/Warlock/window-integration-qa')
    from qa_launch import require_qa_scope
    require_qa_scope()
    if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('Core limit must be exactly (1,1)')
    checked(BASE/'launcher-refused-painted-v1/runner.py','9ccddba53213a1576394f02dff6adcaf98ecf48ce8e24f4ce24155d23b0c377d');checked(BASE/'launcher-refused-painted-v1/search-branch.txt','144d4c383b888591fdbea0f0f30e6dafb5d8da54c022bb8449c25d27c843206e')
    checked(BASE/'search-removed-current-v1/runner.py','6601df9cca0b8c752a40019ecab58d1bbf32344e4e845b928633017466b9c976');checked(BASE/'search-removed-current-v1/search-branch.txt','2c186ad96d74b21e41b1e27837b35c545c330a6787f7a8847cab19b5a720dbfa')
    checked(BASE/'search-removed-at-current-v1/runner.py','190cc7ff1b6b1499f8033bc84abc958ffa7b79467dc80beedeb3e18ed18dddda');checked(BASE/'search-removed-at-current-v1/search-branch.txt','5bbd4418364655db8dd1e490774dc21d64afe82f48fceb3f550f2a4f0e526098')
    checked(BASE/'launcher-refused-at-current-v1/runner.py','52fdf47dcb802d31fce425bbbe63ea1f6d41e36c0fbd000c0dc82870dd2639a7');checked(BASE/'launcher-refused-at-current-v1/search-branch.txt','b6da864b291c0a351c01aec36d17d38ace97906f08fb1de5be8eab26c0b9800d')
    raw=checked(FRAMEWORK,FRAMEWORK_SHA);checked(CANDIDATE,CANDIDATE_SHA);branch=checked(BRANCH,BRANCH_SHA);checked(RECIPIENT,RECIPIENT_SHA);checked(AT_ACTION,AT_ACTION_SHA)
    guard_raw=checked(AT_GUARD,AT_GUARD_SHA);spec=importlib.util.spec_from_loader('at_guard',loader=None);guard=importlib.util.module_from_spec(spec);guard.__file__=str(AT_GUARD);exec(compile(guard_raw,str(AT_GUARD),'exec'),guard.__dict__)
    if guard.PACKET_SHA256!='78016e94c06d11f71c5ba18694fadd876cd17d0d8643b361009733ba4ab57726':raise RuntimeError('unexpected AT provider packet')
    guard.validate()
    for path,digest in {
      '/home/charles/Warlock/implementation/warlock/qa/accessibility-session.py':'69bc3b33c2b99f0b9d54805e18afcb85ff02314dc9aa4d002f4df409a0e57524',
      '/home/charles/Warlock/implementation/warlock/qa/accessibility-inspector.py':'bc4fe7adba15c29f97137b91848971b65b994c1b8f6282109d7edf1e13bd5c27',
      '/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-primary-at/accessibility-reader.py':'9ce02ecb92a182cc5a21dbfea0680970a45b122402e35e387f40acc2a7b4699e'}.items():checked(pathlib.Path(path),digest)
    derived=transform(raw,branch)
    sys.argv=[str(FRAMEWORK),'--launcher-search']
    exec(compile(derived,str(FRAMEWORK),'exec'),{'__name__':'__main__','__file__':str(FRAMEWORK),'LAUNCHER_MODE':mode,'LAUNCH_DIR':HERE,'LAUNCH_RECIPIENT':RECIPIENT,'at_guard':guard,'AT_ACTION':AT_ACTION})
if __name__=='__main__':main()
