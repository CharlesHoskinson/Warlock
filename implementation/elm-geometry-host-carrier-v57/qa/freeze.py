"""Protected append-only isolated host carrier evidence freeze; no GUI."""
import hashlib,json,pathlib,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def main():
 sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
 scope=require_qa_scope();target=ROOT/'component-manifest.json';assert not target.exists()
 report_path=ROOT/'qa/build-1791103261154112126/report.json';report=json.loads(report_path.read_text());assert report['passed'] is True and report['carrierChecks']==34 and report['originalHostTests']==9
 assert len(report['mutants'])==3 and all(m['rejected'] is True and m['exitCode']==1 for m in report['mutants'])
 for relative,value in report['inputs'].items():assert digest(ROOT/relative)==value,relative
 for section in ['dependencies','tools']:
  for path,value in report[section].items():assert digest(path)==value,path
 for relative,value in report['artifacts'].items():assert digest(report_path.parent/relative)==value,relative
 assert digest(report['binary'])==report['binarySHA256']
 sources=[*(ROOT/'native').iterdir(),ROOT/'qa/build.py',pathlib.Path(__file__).resolve(),ROOT/'upstream.json']
 source_files={str(p.relative_to(ROOT)):digest(p) for p in sources if p.is_file()}
 files={str(p.relative_to(ROOT)):digest(p) for p in ROOT.rglob('*') if p.is_file()}
 packet={'schema':1,'passed':True,'nativeAcceptance':False,'releaseAcceptance':False,'scope':'Isolated V8 derivative geometry observation carrier CPU qualification only','qaScope':scope,'frozenUTCUnixNs':time.time_ns(),'sourceFiles':source_files,'files':files,'buildReport':str(report_path),'buildReportSHA256':digest(report_path),'binary':report['binary'],'binarySHA256':report['binarySHA256'],'carrierChecks':34,'originalHostTests':9,'mutantsRejected':3,'queueBound':16,'controlByteBound':4096,'bindingValidation':'canonical identity and counters downstream; strict host envelope types/keys and raw duplicate carrier detection'}
 with target.open('x') as stream:stream.write(json.dumps(packet,indent=2)+'\n')
 for relative,value in files.items():assert digest(ROOT/relative)==value,relative
 print(json.dumps({'passed':True,'manifest':str(target),'manifestSHA256':digest(target),'sourceFiles':source_files,'inventoryEntries':len(files)}),flush=True)
if __name__=='__main__':main()
