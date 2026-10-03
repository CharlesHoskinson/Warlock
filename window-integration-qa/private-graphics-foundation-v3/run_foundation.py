#!/usr/bin/env python3
"""Actual private Intel GL/DMA-BUF and nested-Hyprland foundation; no GUI input."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

BASE=Path(__file__).resolve().parent
QA=BASE.parent
HOST=QA/'private-weston-aq-host-v2'
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
import observations

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def private_json(path,row):
    path.write_text(json.dumps(row,indent=2)+'\n');path.chmod(0o600)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    manifest=json.loads((BASE/'frozen-inputs.json').read_text())
    for path,value in manifest['inputs'].items():assert digest(path)==value,path
    spec=importlib.util.spec_from_file_location('reviewed_foundation_host',HOST/'weston_host.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    staged=module.ReviewedWestonHost(BASE/'not-created',{},320,240);staged.verify()
    if not args.execute:
        print(json.dumps({'preflight':'pass','toolInputs':len(manifest['inputs']),'hostManifestVerified':True,'nativeLaunched':False}))
        return 0
    scope=require_qa_scope();os.umask(0o077)
    output=args.output.resolve();assert output.parent==BASE and output.name.startswith('attempt-')
    output.mkdir(mode=0o700)
    before=observations.capture(output/'main-before')
    main_env=dict(os.environ)
    report={'scope':'actual private Intel GL host + DMA-BUF feedback + nested Wayland backend bootstrap; no input/producer/windows/cadence/physical-output claim','checks':[],'nativeHostAccepted':False,'mainGUIWrites':False,'mainRestorationWrites':False,'qaScope':scope,'result':'pending'}
    session=None
    def check(name,value,**details):
        report['checks'].append({'name':name,'passed':bool(value),**details})
        assert value,name
    try:
        with module.PrivateHyprSession(output=output/'private-session',main_env=main_env,width=320,height=240,nested_lua=(BASE/'nested-foundation.lua').read_bytes(),dri_prime='pci-0000_00_02_0',mesa_vendor=True) as session:
            report['privateSession']=session.evidence
            config_errors=session.ctl('configerrors')
            check('nested config valid',not config_errors.strip(),actualConfigErrors=config_errors)
            monitors=session.data('monitors')
            check('only exact private untransformed output',len(monitors)==1 and monitors[0]['name']=='WAYLAND-1' and all(monitors[0][k]==v for k,v in {'width':320,'height':240,'scale':1,'x':0,'y':0,'transform':0}.items()),monitors=monitors)
            check('Xwayland actually disabled',session.data('getoption','xwayland:enabled').get('bool') is False,option=session.data('getoption','xwayland:enabled'))
            check('no private native clients',session.data('clients')==[])
            check('no private plugins',session.data('plugin','list')==[])
            dma=session.evidence['actualDmabuf']
            check('real complete Intel DMA-BUF feedback',dma['defaultFeedbackComplete'] is True and dma['renderNode']=='/dev/dri/renderD129' and dma['driver'] in ('i915','xe') and dma['formatTableBytes']>0 and dma['formatTableBytes']%16==0 and dma['primeCaps']&2,actual=dma)
            log=(output/'private-session/weston-renderer.log').read_text()
            strings={key:re.findall(re.escape(key)+r': ([^\n]+)',log)[-1] if re.findall(re.escape(key)+r': ([^\n]+)',log) else None for key in ('GL renderer','GL vendor','GL version','EGL vendor','EGL version')}
            check('actual hardware Intel Mesa renderer strings',strings['GL renderer'] and 'Intel' in strings['GL renderer'] and strings['EGL vendor']=='Mesa Project' and not re.search(r'llvmpipe|softpipe|swrast',str(strings),re.I),strings=strings)
            for owner in ('westonMaps','hyprlandMaps'):
                files=session.evidence[owner]['files']
                check(owner+' actual EGL/GBM/DRI mappings',any('libEGL_mesa.so' in p for p in files) and any('libgbm.so' in p for p in files) and any('iris_dri.so' in p or 'libgallium-' in p for p in files),files=files)
            actual=session.evidence['hyprlandMaps']['files']
            library=session.evidence['privateAquamarine']
            check('actual exact private Aquamarine mapping',actual.get(library['path'])==library['sha256'] and not any(p.startswith('/usr/lib/libaquamarine') for p in actual),privateLibrary=library)
            check('exact live private parent peer',session.evidence['parentSocket']['pid']==session.evidence['weston']['pid'])
            check('private output contains no main monitor',all(m['name']!='eDP-2' for m in monitors))
    except Exception as error:
        report.update(result='fail',error=repr(error))
    finally:
        if session:report['privateSession']=session.evidence
        elif 'staged' in locals():report['preflightHost']=staged.evidence
    # A failed __enter__ leaves no assigned session; collect its archived evidence.
    host_evidence=output/'private-session/host-evidence.json'
    if host_evidence.exists():report['privateSession']=json.loads(host_evidence.read_text())
    evidence=report.get('privateSession',{})
    cleanup=not evidence.get('cleanupErrors') and evidence.get('remainingDescendants')==[] and evidence.get('runtimeGone') is True and evidence.get('unexpectedInnerDescendants')==[]
    report['checks'].append({'name':'normal private host cleanup, no survivors','passed':bool(cleanup)})
    try:
        checks,details=observations.compare(before,output/'main-after')
        report['preservation']=checks;private_json(output/'preservation-details.json',details)
    except Exception as error:
        report['preservationError']=repr(error);report['preservation']={}
    unchanged=all(digest(p)==v for p,v in manifest['inputs'].items())
    try:staged.verify();host_unchanged=True
    except Exception as error:host_unchanged=False;report['hostFreezeError']=repr(error)
    report.update(frozenSourcesUnchanged=unchanged,hostInputsUnchanged=host_unchanged)
    accepted=not report.get('error') and all(c['passed'] for c in report['checks']) and bool(report['preservation']) and all(report['preservation'].values()) and unchanged and host_unchanged
    report.update(result='pass' if accepted else 'fail',nativeHostAccepted=bool(accepted))
    private_json(output/'report.json',report)
    print(json.dumps({'result':report['result'],'checks':len(report['checks']),'preservationPassed':sum(report['preservation'].values()),'preservationTotal':len(report['preservation']),'error':report.get('error'),'reportSHA256':digest(output/'report.json')}))
    return int(not accepted)

if __name__=='__main__':raise SystemExit(main())
