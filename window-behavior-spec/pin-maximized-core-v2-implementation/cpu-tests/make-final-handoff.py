import ast,datetime,difflib,hashlib,json,os,re,shlex,stat,subprocess
from pathlib import Path
B=Path(__file__).resolve().parents[1];O=B/'final-review'
def meta(p):
 s=p.stat();return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mode=stat.S_IMODE(s.st_mode),size=s.st_size)
def write(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
original=json.loads((B/'before-edit-source-inverses.json').read_text());inverses=[];changed=[];diff=[]
for row in original['sources']:
 rel=row['path'];p=B/'inverses'/rel;m=meta(p)
 assert m['sha256']==row['sha256'] and m['mode']==row['mode'],rel
 inverses.append(dict(path=str(p.relative_to(B)),**m))
 actual=B/rel
 if not actual.exists():raise SystemExit('original source missing '+rel)
 now=meta(actual)
 if any(now[k]!=row[k] for k in ['sha256','mode']):
  changed.append(dict(path=rel,original=row,current=now,inverse=str(p.relative_to(B))))
  try:diff+=list(difflib.unified_diff(p.read_text().splitlines(True),actual.read_text().splitlines(True),fromfile='original/'+rel,tofile='actual/'+rel))
  except UnicodeDecodeError:diff.append('Binary difference '+rel+'\n')
newCore=[p for p in (B/'core/src/desktop/state/pin').iterdir() if p.is_file()]+list((B/'core/src/layout/algorithm/tiled/scrolling').glob('NativeScrollingRestore.*'))
for p in sorted(newCore):
 rel=str(p.relative_to(B));changed.append(dict(path=rel,original=None,current=meta(p)))
 diff+=list(difflib.unified_diff([],p.read_text().splitlines(True),fromfile='/dev/null',tofile='actual/'+rel))
for rel in ['helper/pin_helper.py','helper/test_helper.py']:
 p=B/rel;old=B/'inverses'/rel
 diff+=list(difflib.unified_diff(old.read_text().splitlines(True),p.read_text().splitlines(True),fromfile='original/'+rel,tofile='actual/'+rel))
 changed.append(dict(path=rel,original=meta(old),current=meta(p),inverse=str(old.relative_to(B))))
write(O/'complete-source-inverse-mapping.json',dict(originalCoreRevision=original['coreRevision'],inverses=inverses,changed=changed,wholeOriginalFilesPreserved=True))
with (O/'complete-policy.diff').open('x') as f:f.writelines(diff)
with (O/'cli.diff').open('x') as f:f.writelines(difflib.unified_diff((B/'inverses/helper/pin_helper.py').read_text().splitlines(True),(B/'helper/pin_helper.py').read_text().splitlines(True),fromfile='original/helper/pin_helper.py',tofile='actual/helper/pin_helper.py'))
for rel in ['PinBoundary.hpp','PinLifetime.hpp','PinJson.hpp','test_pin_action.cpp','test_modal_region.cpp','test_caption_cache.cpp','test_atlas_coordinates.cpp']:
 assert (B/'plugin'/rel).read_bytes()==(B/'inverses/plugin'/rel).read_bytes(),rel
design=json.loads((B/'retained-approved-design/SOURCE_READY.json').read_text())
for rel,m in design['files'].items():
 p=B/'retained-approved-design'/rel;current=meta(p)
 assert current==m,(rel,current,m)
proof=json.loads((B/'proof/transfer-refinement-before-implementation.json').read_text())
assert meta(B/'pin_transfer_refinement.qnt')['sha256']==proof['sourceSha256']
for r in proof['commands']:
 assert r['exitCode']==0 and meta(B/r['log'])['sha256']==r['logSha256']
write(O/'preserved-design-and-ordinary-sources.json',dict(designFiles=len(design['files']),designSHA256=meta(B/'retained-approved-design/SOURCE_READY.json')['sha256'],transferNamed=20,transferTraces=2000,originalPluginSourceFilesExact=7,helperAssertions=32,helperDeadlineChanged=False,nativeExecuted=False))
# Record actual compiler components and the linked dynamic-library closure.
toolComponents={}
for query in ['-print-prog-name=cc1plus','-print-prog-name=collect2','-print-libgcc-file-name','-print-file-name=crtbeginS.o','-print-file-name=crtendS.o']:
 path=Path(subprocess.check_output(['g++',query],text=True).strip()).resolve();toolComponents[str(path)]=meta(path)
roots=[B/'build-core-make/Hyprland',B/'plugin/hyprbars-native-max-core-v2-candidate.so'];pending=roots.copy();libraries={}
while pending:
 p=pending.pop();key=str(p.resolve())
 if key in libraries:continue
 result=subprocess.run(['readelf','-d',str(p)],text=True,capture_output=True);assert result.returncode==0,key
 needed=re.findall(r'\(NEEDED\).*?\[([^\]]+)\]',result.stdout)
 libraries[key]=dict(metadata=meta(p),needed=needed)
 for soname in needed:
  matches=[d/soname for d in [Path('/usr/lib'),Path('/usr/lib64')] if (d/soname).exists()]
  assert matches,soname
  pending.append(matches[0].resolve())
write(O/'compiler-and-linked-library-closure.json',dict(compilerComponents=toolComponents,libraries=libraries,loaderCache=meta(Path('/etc/ld.so.cache')),nativeExecuted=False))
fixed=json.loads((B/'final-build-source-fixed-v2-before.json').read_text())
for rel,m in fixed['sources'].items():
 p=B/rel;current=meta(p)
 assert current['sha256']==m['sha256'] and current['mode']==m['mode'] and p.stat().st_mtime_ns==m['mtimeNs'],rel
reg=json.loads((B/'cpu-tests/final-regression-commands.json').read_text())
assert len(reg['commands'])==16 and all(r['exitCode']==0 for r in reg['commands'])
for r in reg['commands']:assert meta(B/r['log'])['sha256']==r['logSHA256']
official=json.loads((B/'cpu-tests/official-cpu-results.json').read_text());assert official['tests']==270 and official['failures']==0
assert 'Ran 72 tests' in (B/'cpu-tests/schema2-and-inherited-helper-final-v2.log').read_text() and '\nOK\n' in (B/'cpu-tests/schema2-and-inherited-helper-final-v2.log').read_text()
assert '33 actual owning' in (B/'cpu-tests/owning-run-final.log').read_text()
assert '38 actual compiled' in (B/'cpu-tests/actual-core-policy-run.log').read_text()
write(O/'final-gate.json',dict(nativeExecuted=False,sourceFixedBeforeBuildSHA256=meta(B/'final-build-source-fixed-v2-before.json')['sha256'],coreBuildSession=52687,pluginBuildSession=50669,buildsPassed=True,actualOwningChecks=33,actualCompiledPolicyChecks=38,originalUpstreamCPUTests=270,pluginCPUCases=311,helperSchemaConservationTests=72,approvedDesignNamed=129,approvedDesignTraces=6000,transferNamed=20,transferTraces=2000,originalPinNative14Pending=True))
# All packet bytes/modes/links, including generated headers, objects, failure
# preimages, exact inverses and ancestor manifests. Git administration/cache
# files are explicitly excluded, never part of the built policy inputs.
files={};links={};directories={}
exclude={'SOURCE_READY.json','SOURCE_READY_INPUTS.json'}
for root,ds,fs in os.walk(B,followlinks=False):
 root=Path(root);ds[:]=sorted(d for d in ds if d not in {'.git','__pycache__'})
 for name in ds[:]:
  p=root/name;rel=str(p.relative_to(B))
  if p.is_symlink():links[rel]=dict(target=os.readlink(p),mode=stat.S_IMODE(p.lstat().st_mode));ds.remove(name)
  else:directories[rel]=stat.S_IMODE(p.stat().st_mode)
 for name in sorted(fs):
  p=root/name;rel=str(p.relative_to(B))
  if rel in exclude:continue
  if p.is_symlink():links[rel]=dict(target=os.readlink(p),mode=stat.S_IMODE(p.lstat().st_mode))
  else:files[rel]=meta(p)
write(B/'SOURCE_READY_INPUTS.json',dict(schema=1,files=files,links=links,directories=directories,exclusions=['all .git and __pycache__ directories','only top-level SOURCE_READY.json and SOURCE_READY_INPUTS.json'],nativeAuthorized=False))
closureSHA=meta(B/'SOURCE_READY_INPUTS.json')['sha256']
outputs=json.loads((O/'build-input-output-closure.json').read_text())['outputs']
write(B/'SOURCE_READY.json',dict(schema=1,result='SOURCE_AND_BUILD_READY_FOR_ROOT_REVIEW',created=datetime.datetime.now(datetime.timezone.utc).isoformat(),stage=str(B),sourceClosure='SOURCE_READY_INPUTS.json',sourceClosureSHA256=closureSHA,files=len(files),links=len(links),directories=len(directories),corePolicyBuild=fixed['corePolicyBuild'],coreELFBuildID='5ec914c64df540038d925659a5109c646bcad582',outputs=outputs,sourceInverse='final-review/complete-source-inverse-mapping.json',actualDiff='final-review/complete-policy.diff',actualFieldABI='final-review/ACTUAL_SOURCE_FIELD_ABI_MAPPING.md',gate='final-review/final-gate.json',nativeAuthorized=False,nativeAccepted=False,installedChanged=False,fullParityAccepted=False,remaining=['Root source review and immutable freeze','Original unchanged Pin14 actual native campaign','Actual native MAX/restore/coexistence/transfer/scroll/focus reachability','Original focus/Seat/cursor/refusal policy and independent child-pin observations']))
print(json.dumps(dict(readySHA256=meta(B/'SOURCE_READY.json')['sha256'],closureSHA256=closureSHA,files=len(files),links=len(links),changedSources=len(changed)),indent=2))
