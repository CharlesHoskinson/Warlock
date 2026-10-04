import pathlib,json,hashlib,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
models=sorted((ROOT/'qa').glob('model-*/report.json'));compiled=sorted((ROOT/'qa').glob('compiled-*/report.json'))
m=json.loads(models[-1].read_text());c=json.loads(compiled[-1].read_text())
assert m['passed'] and c['passed']
assert m['modelSHA256']==sha(ROOT/'spec/registry.qnt')
assert c['sourceSHA256']==sha(ROOT/'native/grant-registry.hpp')
history=ROOT/'history/exact-mutation';old=json.loads((history/'packet-manifest.json').read_text())
for rel,row in old['files'].items():assert sha(history/rel)==row['sha256'] and (history/rel).stat().st_size==row['size']
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
manifest={'sourceHeld':True,'cpuAccepted':True,'nativeAcceptance':False,'kernelAuthenticationAccepted':False,'durableReservationReleaseAccepted':False,'lifetimeEntropyAccepted':False,'fullRoadmapAccepted':False,'modelReport':str(models[-1].relative_to(ROOT)),'compiledReport':str(compiled[-1].relative_to(ROOT)),'quintNamedScenarios':len(m['namedScenarios']),'quintInvariantSamples':m['invariantSamples'],'quintMaxSteps':m['maxSteps'],'quintMutationControls':m['mutantsRejected'],'compiledChecks':c['compiledResult']['checks'],'typedCompiledMutationControls':c['typedCompiledMutationControls'],'scope':'Standalone exact native grant mutation and read-only classification; one serialized registry owner per native lifetime','files':files}
(ROOT/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'manifest':str(ROOT/'component-manifest.json'),'nativeAcceptance':False}))
