"""Preserve full failed native campaign and bounded real receipt observation."""
import hashlib
import json
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
CANDIDATE=REPO/'implementation/elm-geometry-family-menu-receipt-cleanup-native-v100'
REPORT=CANDIDATE/'qa/native-1791110259133139744/report.json'
MANIFEST=CANDIDATE/'qa/held-source-manifest.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    out=ROOT/'qa'/('freeze-'+str(time.time_ns()));out.mkdir()
    result={'passed':False,'nativeCampaignPassed':False,'fullRoadmapAccepted':False}
    try:
        assert digest(MANIFEST)=='7a7c0ed9c3559afea1140ffb51fdc6baafaa25a5b8334d42a3e84a9b7ef479f5'
        source=json.loads(MANIFEST.read_text())
        for relative,row in source['files'].items():
            path=CANDIDATE/relative
            assert not path.is_symlink() and digest(path)==row['sha256'] and path.stat().st_size==row['size']
        campaign=json.loads(REPORT.read_text())
        assert campaign['passed'] is False and campaign['cleanupPassed'] is True
        assert campaign['scenarios']==['GEOMETRY-MENU-'+str(n).zfill(2) for n in range(1,10)]
        assert len(campaign['checks'])==159 and all(row['passed'] for row in campaign['checks'])
        assert 'line 301' in campaign['traceback'] and campaign['error']=="RuntimeError('Whole-transition absolute six-second deadline')"
        held=campaign['receiptHold09']
        assert held['finishedBeforeDeadline'] and held['deadlineSeconds']==6
        assert held['held']['receipt']==held['receipt'] and held['receipt']['status']=='Committed'
        assert held['issued']['binding']==held['receipt']['binding'] and held['issued']['intent']==held['receipt']['intent']
        assert held['notification']['kind']=='host-refresh'
        assert held['pending']['transaction']=='Pending' and held['pending']['outstanding']==held['pending']['registry']==1
        assert held['observerFacts']['binding']['session']!=held['issued']['binding']['session']
        paths=[REPORT,MANIFEST,Path(__file__)]
        for relative,expected in campaign['artifacts'].items():
            path=REPORT.parent/relative
            assert not path.is_symlink() and path.resolve().is_relative_to(REPORT.parent.resolve()) and digest(path)==expected
            paths.append(path)
        packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeCampaignPassed':False,
                'boundedRealHeldReceiptObserved':True,'cleanupPassed':True,'fullMenuAccepted':False,
                'fullRoadmapAccepted':False,'mandatoryUnresolvedScenario':'GEOMETRY-MENU-10',
                'scope':'Full failed original ten-scenario campaign retained; real held receipt scenario09 observed before unchanged deadline',
                'files':[{'path':str(p.relative_to(REPO)),'sha256':digest(p),'size':p.stat().st_size} for p in paths]}
        (ROOT/'component-manifest.json').write_text(json.dumps(packet,indent=2)+'\n')
        result.update(passed=True,files=len(paths),boundedRealHeldReceiptObserved=True)
    except Exception as error:
        result['error']=repr(error)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'report':str(out/'report.json'),**result}));return not result['passed']

if __name__=='__main__':raise SystemExit(main())
