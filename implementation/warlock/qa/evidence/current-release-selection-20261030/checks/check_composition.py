#!/usr/bin/env python3
"""Protected local composition checks, without changing frozen native inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import shutil
import sys
import time
import traceback

ROOT=Path('/home/charles/Warlock')
PRODUCT=ROOT/'implementation/warlock'
BASE=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
sys.path.insert(0,str(PRODUCT/'adapter'))
import current_build as frontend
import current_native as native

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['capture','test'],required=True)
    ap.add_argument('--frontend-report',required=True,type=Path)
    ap.add_argument('--frontend-sha256',required=True)
    ap.add_argument('--lock',type=Path)
    ap.add_argument('--sha256')
    args=ap.parse_args()
    scope=frontend.require_scope()
    out=BASE/('current-native-'+args.mode+'-'+str(time.time_ns())); out.mkdir(mode=0o700)
    inputs={}
    for source,label in [(Path(__file__).resolve(),'executed-check.py'),(PRODUCT/'adapter/current_native.py','executed-current-native.py'),(PRODUCT/'adapter/current_build.py','executed-current-build.py')]:
        inputs[str(source)]=frontend.sha(source); shutil.copyfile(source,out/label)
    report=dict(passed=False,nativeAcceptance=False,releaseAccepted=False,scope=scope,inputs=inputs,checks=[],seed=20261030,
                limit='Read-only original/current role validation and fixed/seeded declared-lock mutations; frozen host/object/provider/ABI inputs are never modified. No native code is loaded.')
    def yes(name,condition):
        report['checks'].append(dict(name=name,passed=bool(condition)))
        if not condition:raise AssertionError(name)
    def rejects(name,call):
        try:call()
        except (frontend.ChangedInput,OSError,ValueError,KeyError,TypeError,RuntimeError) as error:
            report['checks'].append(dict(name=name,passed=True,error=str(error)))
        else:yes(name,False)
    try:
        if args.mode=='capture':
            value=native.observe(args.frontend_report,args.frontend_sha256)
            path=out/'native-lock.json'; frontend.write(path,value)
            yes('Current frontend and unchanged native role observation succeeds',value['nativeAcceptance'] is False and value['releaseAccepted'] is False)
            yes('All original preflight and source deltas retained',len(value['preflightDeltas'])==15 and len(value['historicalSourceDeltas'])==13)
            yes('Historical seven and current two additions explicit',len(value['frontendChanges'])==7 and len(value['frontendAdditions'])==2)
            yes('One reviewed static asset delta explicit',set(value['frontendStaticChanges'])=={str(PRODUCT/'assets/popup-adapter.js')})
            yes('One reviewed release adapter delta explicit',set(value['adapterChanges'])=={str(PRODUCT/'adapter/release_tuple.py')})
            report['proposedLock']=dict(path=str(path),sha256=frontend.sha(path))
        else:
            if not args.lock or not args.sha256:raise ValueError('Reviewed native lock required')
            value=native.validate_composition(args.frontend_report,args.frontend_sha256,args.lock,args.sha256)
            yes('Reviewed production composition validates',value['nativeAcceptance'] is False and value['installable'] is False)
            report['reviewedLock']=dict(path=str(args.lock),sha256=args.sha256)
            def changed(name,alter):
                candidate=json.loads(json.dumps(value)); alter(candidate)
                path=out/(str(len(report['checks']))+'-changed-lock.json'); frontend.write(path,candidate)
                rejects(name,lambda:native.validate_composition(args.frontend_report,args.frontend_sha256,path,frontend.sha(path)))
            rejects('Wrong reviewed native lock digest refused',lambda:native.validate_composition(args.frontend_report,args.frontend_sha256,args.lock,'0'*64))
            rejects('Wrong frontend receipt refused',lambda:native.validate_composition(args.frontend_report,'0'*64,args.lock,args.sha256))
            changed('Raised native acceptance refused',lambda v:v.update(nativeAcceptance=True))
            changed('Raised release acceptance refused',lambda v:v.update(releaseAccepted=True))
            changed('Installable claim refused',lambda v:v.update(installable=True))
            changed('Unknown native lock schema refused',lambda v:v.update(schema=99))
            for name,path in [('Host',value['slots']['host']['path']),('Core',value['slots']['core']['path']),('Authority',value['slots']['authority']['path']),('Aquamarine',value['slots']['aquamarine']['path']),('Native source',next(iter(value['nativeSources']))),('Retained object',next(iter(value['retainedObjects']))),('Provider',next(iter(value['providers']))),('Dependency',next(iter(value['freshDependencies'])))]:
                changed('Wrong declared '+name+' hash refused',lambda v,p=path:v['inputs'].update({p:'0'*64}))
            alias=next(p for p in value['aliases'] if p.endswith('libaquamarine.so.14'))
            changed('Wrong declared AQ alias refused',lambda v:v['aliases'].update({alias:'foreign.so'}))
            core=value['slots']['core']['path']
            changed('Wrong resolved core path refused',lambda v:v['resolutions'].update({core:'/foreign/core'}))
            changed('Missing new frontend module refused',lambda v:v['frontendAdditions'].pop(next(iter(v['frontendAdditions']))))
            changed('Wrong historical source role refused',lambda v:v['frontendChanges'][next(iter(v['frontendChanges']))].update(old='0'*64))
            changed('Missing runtime static delta refused',lambda v:v.pop('frontendStaticChanges'))
            changed('Wrong historical static digest refused',lambda v:v['frontendStaticChanges'][str(PRODUCT/'assets/popup-adapter.js')].update(old='0'*64))
            changed('Wrong current static digest refused',lambda v:v['frontendStaticChanges'][str(PRODUCT/'assets/popup-adapter.js')].update(current='0'*64))
            changed('Missing release adapter delta refused',lambda v:v.pop('adapterChanges'))
            changed('Wrong historical release adapter digest refused',lambda v:v['adapterChanges'][str(PRODUCT/'adapter/release_tuple.py')].update(old='0'*64))
            changed('Wrong current release adapter digest refused',lambda v:v['adapterChanges'][str(PRODUCT/'adapter/release_tuple.py')].update(current='0'*64))
            changed('Missing historical preflight row refused',lambda v:v['preflightDeltas'].pop())
            changed('Wrong historical row label refused',lambda v:v['preflightDeltas'][0].update(label='foreign'))
            changed('Wrong retained object ordering refused',lambda v:v['nativeCommands'][2]['argv'].__setitem__(slice(1,3),list(reversed(v['nativeCommands'][2]['argv'][1:3]))))
            generator=random.Random(report['seed']); names=sorted(value['inputs'])
            selected=generator.sample(names,min(16,len(names)))
            for index,path in enumerate(selected):
                changed('Seeded wrong declared input hash '+str(index),lambda v,p=path:v['inputs'].update({p:'0'*64}))
            report['sampledInputPaths']=selected
            yes('Original composition still validates',native.validate_composition(args.frontend_report,args.frontend_sha256,args.lock,args.sha256)==value)
        for path,digest in inputs.items():yes('Executed source unchanged '+Path(path).name,frontend.sha(path)==digest)
        report['passed']=True
    except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
    frontend.write(out/'report.json',report)
    print(json.dumps(dict(passed=report['passed'],report=str(out/'report.json'),checks=len(report['checks']),proposedLock=report.get('proposedLock'),error=report.get('error'))))
    return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
