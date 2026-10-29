#!/usr/bin/env python3
"""Focused compiled Elm launcher replay; no native acceptance."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO = Path('/home/charles/Warlock')
PRODUCT = REPO / 'implementation/warlock'
HELD = REPO / 'implementation/warlock-preview-provider-v143'
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope

PINS = {'src/Desktop.elm':'a503d926599b5aa194956a1208fdc0004fb829442cd523c5372d41fd1fab0404',
        'src/Surface.elm':'a660a4641a9f834c6198bce1e8049b3dd0be40cb74be1cfe1d5e14cfd0cdaa1d',
        'src/Launch.elm':'dcd7260248ccb0b5bc6001c49319dd51af8c2fae98888919a308ac025ed273a2',
        'src/Catalog.elm':'3eadb76212a66986ef2d76292a2f33595f7cd7d47dc90c8982435195f9ea3f02',
        'qa/NativePointerFixture.elm':'b674baa48a0d0197d32e6bc400412465e3a83934d3a749ebc7cbba35e82c4124',
        'elm.json':'48651a8950f9d4df5502f541d0262f83c579b54fe0dcd623a186992cb72d8208'}
MANIFEST = 'fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa'


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(argv, cwd, env, report, timeout):
    result = subprocess.run([str(x) for x in argv], cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    report['commands'].append({'argv':[str(x) for x in argv], 'exit':result.returncode, 'stdout':result.stdout, 'stderr':result.stderr})
    if result.returncode: raise RuntimeError('command failed: ' + str(argv[0]))
    return result.stdout


def main():
    report = {'passed':False,'requirement':'ELM-UI-005','scenarios':['search-refused','search-race'],
              'scope':'Compiled Elm Desktop and Surface replay via worker port; no physical keyboard, native launcher, GUI, or requirement acceptance.', 'commands':[]}
    try:
        report['protectedScope'] = require_qa_scope()
        assert sha(HELD/'qa/toolchain.json') == MANIFEST
        toolchain = json.loads((HELD/'qa/toolchain.json').read_text())
        assert len(toolchain['heldFiles']) == 111
        def verify_toolchain():
            for name, expected in toolchain['heldFiles'].items():
                path=HELD/name
                assert path.is_file() and path.stat().st_size==expected['size'] and sha(path)==expected['sha256'], name
        verify_toolchain()
        compiler=HELD/toolchain['compiler']; assert sha(compiler)==toolchain['compilerSHA256']
        node=shutil.which('node'); assert node
        assert sha(HERE/'LauncherVisibilityReplay.elm')=='80b1531d437d6bb74dfdaa3cf931429556a53f75bc8a09712f2f8f5814f2e8a5'
        assert sha(HERE/'launcher-visibility-replay.cjs')=='befe7c16029950532e49bcc8a74e58ce1cebbe533da5e2d69815cc5aeee05c5d'
        for name, digest in PINS.items(): assert sha(PRODUCT/name)==digest, name
        sources={str(p):sha(p) for p in sorted((PRODUCT/'src').rglob('*.elm'))}
        for p in (PRODUCT/'elm.json',PRODUCT/'qa/NativePointerFixture.elm',HERE/'LauncherVisibilityReplay.elm',HERE/'launcher-visibility-replay.cjs',Path(__file__).resolve()): sources[str(p)]=sha(p)
        report.update(sourceHashes=sources,toolchainManifestSHA256=MANIFEST,compilerSHA256=sha(compiler),node=str(Path(node).resolve()),nodeSHA256=sha(Path(node).resolve()))
        with tempfile.TemporaryDirectory(prefix='warlock-launcher-outcome-') as temp:
            temp=Path(temp); workspace=temp/'workspace'; workspace.mkdir()
            (workspace/'src').symlink_to(PRODUCT/'src',target_is_directory=True)
            (workspace/'qa').mkdir()
            shutil.copyfile(PRODUCT/'qa/NativePointerFixture.elm',workspace/'qa/NativePointerFixture.elm')
            shutil.copyfile(HERE/'LauncherVisibilityReplay.elm',workspace/'qa/LauncherVisibilityReplay.elm')
            elm=json.loads((PRODUCT/'elm.json').read_text()); elm['source-directories']=['src','qa']
            (workspace/'elm.json').write_text(json.dumps(elm))
            home=temp/'elm-home'; shutil.copytree(HELD/toolchain['elmHome'],home)
            env={**os.environ,'ELM_HOME':str(home),'PYTHONDONTWRITEBYTECODE':'1'}
            compiled=temp/'launcher.js'
            run([compiler,'make','qa/LauncherVisibilityReplay.elm','--optimize','--output='+str(compiled)],workspace,env,report,240)
            report['compiledSHA256']=sha(compiled)
            output=run([node,HERE/'launcher-visibility-replay.cjs',compiled],workspace,env,report,10)
            actual=json.loads(output); report['replay']=actual
            assert len(actual['checks'])==16 and all(value is True for value in actual['checks'].values())
            assert actual['nativeAcceptance'] is False
            assert actual['acceptedStatus']=='Launch submitted.' and actual['refusedStatus']=='Launch refused. Refresh applications and choose again.'
            assert all(sha(p)==digest for p,digest in sources.items())
            assert sha(HELD/'qa/toolchain.json')==MANIFEST
            verify_toolchain()
        report['passed']=True
    except Exception as error:
        report['error']=repr(error)
    print(json.dumps(report,indent=2))
    if not report['passed']: raise SystemExit(1)


if __name__=='__main__': main()
