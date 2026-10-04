"""Verify actual held source delta and preserved real212 failure; no native launch."""
import hashlib
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    out=ROOT/'qa'/('derivation-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'checks':[],'inputs':{}}
    def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
    try:
        original=(ROOT/'original/qa/native.py').read_text()
        expected=original.replace("('zero-scale1','zero-scale2','origin-scale1','origin-scale2')","('zero-scale2','origin-scale2')").replace('Four-profile screenshot subset: zero buffer1/2 ordinary/MAX/restore, nonzero buffer1/2 ordinary diagnostic; no full22, GTK, pointer or full menu acceptance','Remaining two-profile bufferScale2 screenshot subset: zero ordinary/MAX/restore, nonzero ordinary diagnostic; prior212 failed, no full4/full22 acceptance').replace("report['full22Coverage']=False","report['full22Coverage']=False\n        report['fullFourProfileCoverage']=False\n        report['prior212Failed']=True")
        check('native-exact-original-except-selection-and-scope',expected==(ROOT/'qa/native.py').read_text())
        check('pixels-byte-identical',sha(ROOT/'qa/pixels.py')==sha(ROOT/'original/qa/pixels.py'))
        origin=json.loads((ROOT/'origin.json').read_text());base=Path(origin['base']);manifest=base/'component-manifest.json'
        check('original212-manifest-identity',sha(manifest)==origin['componentManifestSHA256'])
        failure=Path(origin['failedNativeReport']);check('original-native-failure-identity',sha(failure)==origin['failedNativeReportSHA256'])
        packet=json.loads(failure.read_text())
        check('genuine-original-failure-preserved',packet['passed'] is False and packet['cleanupPassed'] is True and packet['primaryProfile']=='origin-scale1')
        captures=packet['pixelCaptures']
        check('scale1-three-positive-one-negative',[(x['owner']['name'],x['passed']) for x in captures]==[('zero-scale1',True)]*3+[('origin-scale1',False)])
        for relative,value in packet['artifacts'].items():
            path=failure.parent/relative;assert sha(path)==value,str(path);report['inputs'][str(path)]=value
        report['inputs'].update({str(p):sha(p) for p in (Path(__file__),ROOT/'origin.json',ROOT/'qa/native.py',ROOT/'qa/pixels.py',failure,manifest)})
        report['passed']=True
    except Exception as error:report['error']=repr(error)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
