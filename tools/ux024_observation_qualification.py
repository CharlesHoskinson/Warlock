"""Closed private source qualification for the reviewed observation component.
No command interface, endpoint, production adoption or native acceptance.
"""
import hashlib
import json
import os
from pathlib import Path
import stat

PREFIX='.warlock-contributor/evidence/nextloop-20261106/ux024-observation-component-source-v3'
MANIFEST_SHA='027e50a0fdba6556426c691d2c7738ea14bbdda6c84a7cbc5e760041c8f4bdc8'
POSTS={'implementation/warlock/haskell/protocol/src/Warlock/Protocol/Desktop.hs': ('production', 'ebb4db24c652d8e55b7000616c10a96149a124af7be110ba8c8828a7e5d579a3', '8182a5532aae6dd252a3c02c74d0e86b40969ac4bffb335b2c43e793cb1e4c54'), 'implementation/warlock/haskell/runtime/runtime.cabal': ('production', 'c1c1af0649b3630e8927f51673f9b4f499164b9f8aabe04aec0b324f10d9f6c2', 'd82311075cb8ad80284fde52d3293a1dfbaa9a71b5819e23f762bae0a3882645'), 'implementation/warlock/haskell/runtime/src/Warlock/Backend/WindowObservation.hs': ('production', None, 'bc812f057b7573558b491dceae9c97f5cc4a31d8c98ea1dfc45ca3950a38eb7c'), 'implementation/warlock/haskell/runtime/src/Warlock/Backend.hs': ('production', '08f72cbb79c60b05cd39b4c45ff66e16cbaf64016c9866b089b2f2d3147bf7b4', 'f079377b94ae56ddfd7b67d3f72f94bcf708fa87029fdb064082d9bf460c87ed'), 'implementation/warlock/src/Desktop.elm': ('production', '8385e34a3ecf122bf51a6ca4e4fe2df302a955fe35575dca8b2e419302f6fd56', '23b5ef3c0224754ffac5bf884ace75b922b3e76dc8c03b95f251bbe401225b0d'), 'implementation/warlock/src/MenuBridge.elm': ('production', 'ec8f531b9437e493f9b29fe1e16d678cd388f560a83ca873448630bbde459b25', '0aca150c48310e712bc67a2bd2d3977c03ba3934666e10848b57e7c7ae3b3424'), 'implementation/warlock/src/OutputController.elm': ('production', 'fdf7b44483ec9312182a1b50bb2bbb5d52b804538e5c4d4ce5a4a8479e9af6ae', 'bfd7a7087abcd8456dac3793fba21708386b63171a6a6deaac306ab75bccf808'), 'implementation/warlock/src/Shell.elm': ('production', '4ef1ceaf83a5d306d8d51fc0af4e56877eefdfa66f076fef6acf18d46b23bf73', '58c0f888f890841d77f8068f50baf1024040987e2129eecbbc7c0660ac030aea'), 'implementation/warlock/src/Surface.elm': ('production', 'b1d6eea10f44bfa627f0912d79a5670f2642ccd638de844d89270151f140a179', '2b7f117be337b7f169413f897c82049dd765ca08b472c5ee44c3fa1b84c74a6d'), 'implementation/warlock/src/TaskbarShell.elm': ('production', 'eeb91d15cab97c94bf12ef3d1e25f513ac6c037774bef5150867eb01c6f86c26', '4085ed27b18358331b7a3e74e51ffa6c6f66daaa9dab48f16dc570365ce58612'), 'implementation/warlock/src/WindowObservation.elm': ('production', None, '428c78de7dc136969594e6a5f32cb5b985d69563bbdc91df964b82d4abb89b23'), 'implementation/warlock/haskell/protocol/test-desktop/Main.hs': ('fixture', '2b6b5eb8b292a8c84958a571070fbaeee5b65536746953f0b5edc1c344a669dc', '4a541243aa88166c97b6373b07b480a3b8e65b0e51e371d6361a22418a15bc02'), 'implementation/warlock/haskell/runtime/test-ui-mvp/Main.hs': ('fixture', 'e2411ba16012e8a4c7ca657199b92427e23e73ccadc5792bcb50c4eb6c4742bd', '6aedbbb534d37f3214bbe6328682e6e7b688c09ee07d9e53e36c1b9a7cb57e49'), 'implementation/warlock/qa/Ux024ObservedWindowMenuReplay.elm': ('fixture', None, '98fd760afe5abd770577d509ee2e4f3871a09afe7bc66762f67b5ad713c29ec1'), 'implementation/warlock/qa/ux024-observed-window-menu.cjs': ('fixture', None, '5839bff7dd5626fbbc21da75d29aa5f8493e8043b2d0689446a9afa76dee9966')}
ELM_NAMES=['attachment-is-application-only', 'capability-emits-one-bound-read', 'read-only-does-not-enable-native-actions', 'actual-observed-group-is-inspectable', 'actual-context-opens-inspection-menu', 'inspection-shows-real-title', 'inspection-shows-real-appid', 'inspection-has-refresh-and-close', 'inspection-no-enabled-native-effect', 'keyboard-open-focuses-current-close', 'pointer-open-does-not-focus', 'escape-closes-and-reads-once', 'fresh-exact-incarnation-restores-once', 'same-application-replacement-cannot-restore', 'removed-origin-cannot-restore', 'unknown-cannot-restore', 'pending-read-disables-inspection', 'wrong-request-cannot-settle', 'foreign-binding-cannot-publish', 'foreign-owner-generation-cannot-publish', 'detached-reply-cannot-revive', 'transport-refusal-cannot-open', 'reconciliation-full-cannot-open', 'retired-presentation-view-cannot-restore', 'absent-capability-remains-unavailable', 'empty-capability-remains-unavailable', 'malformed-capability-grants-nothing', 'all-routes-preserve-no-effects', 'inspection-declared-keyboard-order', 'inspection-information-cannot-activate']
ELM_SETUP=['actual-presentation-view-one', 'baseline-local-attachment-valid', 'no-fabricated-catalog']

def sha_bytes(body):
    return hashlib.sha256(body).hexdigest()

def read_regular(path):
    path=Path(path)
    if path.resolve()!=path or path.is_symlink():raise ValueError('qualification alias refused')
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as stream:
        before=os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size>4*1024*1024:raise ValueError('bounded regular qualification input required')
        body=stream.read(before.st_size+1);after=os.fstat(stream.fileno())
    ident=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    if ident(before)!=ident(after) or len(body)!=before.st_size:raise ValueError('qualification input changed')
    return body

def require_variant(variant):
    if variant not in ('baseline','candidate'):raise ValueError('closed baseline or candidate qualification only')

def load(root,variant):
    require_variant(variant);root=Path(root)
    manifest_name=PREFIX+'/manifest.json';body=read_regular(root/manifest_name)
    if sha_bytes(body)!=MANIFEST_SHA:raise ValueError('reviewed candidate manifest differs')
    manifest=json.loads(body);rows=manifest['posts']
    actual={row['path']:(row['kind'],row['beforeSha256'],row['postimage']['sha256']) for row in rows}
    if len(rows)!=15 or actual!=POSTS:raise ValueError('closed fifteen-post scope differs')
    inputs={manifest_name:MANIFEST_SHA};selected=[]
    for name,(kind,before,after) in POSTS.items():
        post_name=PREFIX+'/postimages/'+name;post=root/post_name
        if sha_bytes(read_regular(post))!=after:raise ValueError('frozen post differs: '+name)
        live=root/name
        if before is None:
            if live.exists() or live.is_symlink():raise ValueError('new candidate source already exists: '+name)
        elif sha_bytes(read_regular(live))!=before:raise ValueError('live baseline differs: '+name)
        else:inputs[name]=before
        inputs[post_name]=after
        selected.append({'path':name,'kind':kind,'beforeSha256':before,'postSha256':after,'postPath':str(post)})
    return {'variant':variant,'inputs':inputs,'rows':selected,'sourceManifestSha256':MANIFEST_SHA}

def selected_rows(data):
    require_variant(data['variant'])
    return [row for row in data['rows'] if data['variant']=='candidate' or row['kind']=='fixture']

def projected(data,baseline,prefix):
    result=dict(baseline)
    for row in selected_rows(data):
        if row['path'].startswith(prefix):result[row['path'][len(prefix):]]=row['postSha256']
    return result

def stage_rows(data,stage,prefix):
    stage=Path(stage);expected={}
    for row in selected_rows(data):
        if not row['path'].startswith(prefix):continue
        relative=row['path'][len(prefix):];target=stage/relative
        if '..' in Path(relative).parts or Path(relative).is_absolute() or target.resolve()!=target:raise ValueError('private stage escape')
        if row['beforeSha256'] is None:
            if target.exists() or target.is_symlink():raise ValueError('new stage input exists')
        elif sha_bytes(read_regular(target))!=row['beforeSha256']:raise ValueError('staged baseline differs')
        body=read_regular(row['postPath'])
        if sha_bytes(body)!=row['postSha256']:raise ValueError('post changed before staging')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
        if sha_bytes(read_regular(target))!=row['postSha256']:raise ValueError('staged candidate differs')
        expected[relative]=row['postSha256']
    return expected

def validate_elm_result(value,image_sha,fixture_sha):
    if (value.get('schema')!=1 or value.get('passed') is not True or value.get('nativeAcceptance') is not False
        or value.get('providerAcceptance') is not False or value.get('classification')!='component-pass'
        or value.get('caseCount')!=30 or value.get('seedSampleCount')!=32 or value.get('failures')!=[] or value.get('seedFailures')!=[]
        or value.get('imageSha256')!=image_sha or value.get('fixtureSha256')!=fixture_sha
        or value.get('checks')!=[{'name':name,'passed':True} for name in ELM_NAMES]):raise ValueError('fixed observation replay result differs')
    observed=value.get('observed',{});seeded=observed.get('seeded',{})
    if observed.get('preconditions')!=dict.fromkeys(ELM_SETUP,True) or seeded.get('seeds')!=list(range(32)):raise ValueError('observation setup or seeds differ')
    samples=seeded.get('samples')
    if not isinstance(samples,list) or len(samples)!=32:raise ValueError('observation seed samples absent')
    for n,sample in enumerate(samples):
        if (sample.get('seed')!=n or sample.get('variant')!=n%8 or sample.get('eligibleGroup') is not (n%8==0)
            or sample.get('noMutation') is not True or sample.get('noFocus') is not True or sample.get('nativeAvailable') is not False):raise ValueError('observation seeded witness differs')
