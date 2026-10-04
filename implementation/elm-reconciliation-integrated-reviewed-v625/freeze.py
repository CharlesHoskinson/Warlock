#!/usr/bin/python3
"""One-shot owned packet freeze after explicit root terminal notification."""
import argparse,json,time
from pathlib import Path
from review import HERE,REPO,sha,load,review,inventory

def main():
 a=argparse.ArgumentParser();a.add_argument('--review',required=True);a.add_argument('--config',default=str(HERE/'candidate.json'));a.add_argument('--terminal-attestation',required=True);args=a.parse_args()
 manifest=HERE/'component-manifest.json'
 if manifest.exists():raise SystemExit('Frozen manifest exists; do not overwrite')
 if args.terminal_attestation!='root627-terminal-135-pass-cleanup-true':raise SystemExit('Explicit root627 terminal attestation required')
 config=Path(args.config);old=load(Path(args.review));current=review(load(config))
 if not old['reviewPassed'] or not current['reviewPassed']:raise SystemExit('Independent review failed')
 if old['configSHA256']!=sha(config):raise SystemExit('Config drift')
 if old['inventories']!=current['inventories']:raise SystemExit('Component inventory drift after accepted review')
 out=HERE/'qa'/('final-review-'+str(time.time_ns()));out.mkdir(parents=True);current['configSHA256']=sha(config);current['terminalAttestation']=args.terminal_attestation;(out/'report.json').write_text(json.dumps(current,indent=2)+'\n')
 roots=dict(current['inventories']);roots[str(HERE.relative_to(REPO))]=inventory(HERE)
 files={};special={}
 for root,inv in roots.items():
  for rel,v in inv['files'].items():files[root+'/'+rel]=v
  for rel,v in inv['special'].items():special[root+'/'+rel]=v
 d={'schema':1,'component':HERE.name,'sourceHeld':True,'independentReviewPassed':True,'selectedProduction':'implementation/elm-reconciliation-startup-order-v626','productionWired':True,'durableReconciliationNativeAccepted':True,'durableReconciliationNativeScope':'Original135 v627 current compiled frontend/retirement normal correlated path on core205/AQ155/native594 only','releaseDeliveryLossNativeAccepted':False,'scalableHistoryAccepted':False,'full473NewTupleAccepted':False,'fullRelease':False,'mainDesktopActivated':False,'completedRequirementIds':[],'terminalAttestation':args.terminal_attestation,'review':str((out/'report.json').relative_to(REPO)),'reviewSHA256':sha(out/'report.json'),'priorReview':str(Path(args.review).relative_to(REPO)),'priorReviewSHA256':sha(Path(args.review)),'configSHA256':sha(config),'nativeReports':current['native'],'componentManifestPins':{k:v['sha256'] for k,v in current['manifests'].items()},'files':dict(sorted(files.items())),'excludedOrSpecial':dict(sorted(special.items())),'selfExcluded':str(manifest.relative_to(REPO))}
 manifest.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'manifest':str(manifest),'sha256':sha(manifest),'regularFiles':len(files),'specialOrExcluded':len(special),'review':str(out/'report.json')}))
if __name__=='__main__':main()
