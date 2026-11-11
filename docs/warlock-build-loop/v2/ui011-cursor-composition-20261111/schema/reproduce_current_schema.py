#!/usr/bin/python3
"""Fixed CPU-only current schema reproducibility. No action on import."""
from pathlib import Path
import hashlib,json,os,stat,subprocess,tempfile,time
MANIFEST=Path('/home/hoskinson/warlock-loop-review-20261109T142956Z/next-product-action/ux024-popup-focus-containment/real-window-producer/runtime-producer/backend-integration/next-ui011-observed-opener-closure/native-opener-closure-preparation/watch-bookkeeping-glib-schema-preparation/inputs.json')
MANIFEST_SHA='8bd0109564d850826246cf9a62369f70e6fe880f474c965717c3269229f5cb6f'
OUTPUT=Path('/home/hoskinson/warlock-loop-review-20261109T142956Z/next-product-action/ux024-popup-focus-containment/real-window-producer/runtime-producer/backend-integration/next-ui011-observed-opener-closure/native-opener-closure-preparation/watch-bookkeeping-glib-schema-preparation/actual-root')
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(m):
    source=Path(m['sourceDirectory'])
    current={str(p):digest(p) for p in sorted(source.iterdir()) if p.is_file() and p.name!='gschemas.compiled'}
    if current!=m['sourceFiles']:raise ValueError('exact schema source set or bytes changed')
    for row in (m['compiler'],m['installedCompiled']):
        p=Path(row['path']);s=p.stat()
        if not stat.S_ISREG(s.st_mode) or s.st_mode&0o022 or digest(p)!=row['sha256']:raise ValueError('compiler/cache pin changed')
def main():
    if digest(MANIFEST)!=MANIFEST_SHA:raise ValueError('manifest pin changed')
    m=json.loads(MANIFEST.read_text());verify(m)
    OUTPUT.mkdir(mode=0o700,exist_ok=False)
    target=OUTPUT/'recompiled';target.mkdir(mode=0o700)
    argv=[m['compiler']['path'],'--strict','--targetdir='+str(target),m['sourceDirectory']]
    started=time.monotonic_ns()
    result=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={'PATH':'/usr/bin','LANG':'C','LC_ALL':'C'},timeout=20,check=False)
    (OUTPUT/'compile.stdout').write_bytes(result.stdout);(OUTPUT/'compile.stderr').write_bytes(result.stderr)
    verify(m)
    built=target/'gschemas.compiled';actual=digest(built) if built.is_file() else None
    passed=result.returncode==0 and actual==m['installedCompiled']['sha256']
    report={'schema':1,'passed':passed,'kind':'current-glib-schema-reproducibility','inputManifestSha256':MANIFEST_SHA,'compiler':m['compiler'],'sourceFileCount':len(m['sourceFiles']),'command':argv,'exitCode':result.returncode,'elapsedNs':time.monotonic_ns()-started,'historicalCompiledSha256':m['historicalCompiledSha256'],'currentInstalledSha256':m['installedCompiled']['sha256'],'reproducedSha256':actual,'exactCurrentBytesReproduced':passed,'inputsUnchanged':True,'nativeExecuted':False,'historicalSemanticEquivalenceClaimed':False}
    (OUTPUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,sort_keys=True));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
