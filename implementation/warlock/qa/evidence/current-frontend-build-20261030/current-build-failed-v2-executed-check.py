#!/usr/bin/env python3
"""Protected actual three-root recipe and retained mutation checks."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import time
import traceback

R=Path(__file__).resolve().parents[3]
P=R/'implementation/warlock'
B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--lock',type=Path,required=True)
    ap.add_argument('--sha256',required=True)
    args=ap.parse_args()
    spec=importlib.util.spec_from_file_location('warlock_current_build',P/'adapter/current_build.py')
    recipe=importlib.util.module_from_spec(spec); spec.loader.exec_module(recipe)
    scope=recipe.require_scope()
    out=B/('current-build-contracts-'+str(time.time_ns())); out.mkdir(mode=0o700)
    inputs={str(Path(__file__).resolve()):recipe.sha(__file__),str(P/'adapter/current_build.py'):recipe.sha(P/'adapter/current_build.py')}
    report=dict(passed=False,nativeAcceptance=False,releaseAccepted=False,scope=scope,inputs=inputs,checks=[],limit='Current frontend recipe and actual bounded mutation checks, not native tuple composition, complete upstream source provenance or offline reproducibility.')
    def yes(name,condition):
        report['checks'].append(dict(name=name,passed=bool(condition)))
        if not condition: raise AssertionError(name)
    def rejects(name,call):
        try: call()
        except recipe.ChangedInput as error:
            report['checks'].append(dict(name=name,passed=True,error=str(error)))
        else: yes(name,False)
    try:
        lock=recipe.validate_lock(args.lock,args.sha256)
        yes('Reviewed current lock validates',lock['roots']==recipe.ROOTS)
        def altered_lock(name,alter):
            value=json.loads(json.dumps(lock)); alter(value)
            path=out/(name+'.json'); recipe.write(path,value)
            rejects(name,lambda:recipe.validate_lock(path,recipe.sha(path)))
        source=next(iter(lock['sources']))
        held=next(p for p in lock['inputs'] if str(recipe.HELD) in p)
        altered_lock('Changed source dependency hash refused',lambda v:v['inputs'].update({source:'0'*64}))
        altered_lock('Changed held dependency hash refused',lambda v:v['inputs'].update({held:'0'*64}))
        altered_lock('Unlisted source refused',lambda v:v['sources'].update({'unlisted.elm':'0'*64}))
        altered_lock('Unlisted cache input refused',lambda v:v['cache'].update({'foreign-package':'0'*64}))
        altered_lock('Changed root recipe refused',lambda v:v['roots'].update(Main='foreign.js'))
        duplicate=out/'duplicate.json'; duplicate.write_text('{"schema":1,"schema":1}')
        rejects('Duplicate JSON keys refused',lambda:recipe.validate_lock(duplicate,recipe.sha(duplicate)))
        rejects('Wrong reviewed lock digest refused',lambda:recipe.validate_lock(args.lock,'0'*64))
        built=out/'build'; result=recipe.build(args.lock,args.sha256,built)
        yes('Actual Main Bar Popup optimized compilation succeeds',result['passed'] and len(result['commands'])==3 and all(c['exit']==0 for c in result['commands']))
        receipt=built/'report.json'; receipt_sha=recipe.sha(receipt)
        yes('Current report validates actual inputs and outputs',recipe.validate_report(receipt,receipt_sha)['passed'])
        def altered_output(name,path):
            original=path.read_bytes()
            try:
                path.write_bytes(original+b'\nTAMPERED\n')
                rejects(name,lambda:recipe.validate_report(receipt,receipt_sha))
            finally: path.write_bytes(original)
        for name in ['elm.js','bar.js','popup.js']:
            altered_output('Changed compiled '+name+' refused',built/'assets'/name)
        static=next(iter(lock['static']))
        altered_output('Changed static asset refused',built/'assets'/static)
        altered_output('Changed compiler log refused',built/'Main.stdout')
        foreign=built/'assets/foreign.js'; foreign.write_text('foreign')
        try: rejects('Unlisted output refused',lambda:recipe.validate_report(receipt,receipt_sha))
        finally: foreign.unlink()
        rejects('Wrong reviewed report digest refused',lambda:recipe.validate_report(receipt,'0'*64))
        failed=json.loads(receipt.read_text()); failed['passed']=False
        failed_path=built/'failed-receipt.json'; recipe.write(failed_path,failed)
        rejects('Failed receipt refused',lambda:recipe.validate_report(failed_path,recipe.sha(failed_path)))
        wrong=json.loads(receipt.read_text()); wrong['commands'][0]['module']='Foreign'
        wrong_path=built/'wrong-roots.json'; recipe.write(wrong_path,wrong)
        rejects('Foreign root receipt refused',lambda:recipe.validate_report(wrong_path,recipe.sha(wrong_path)))
        for label,alter in [
            ('Foreign compiler command refused',lambda r:r['commands'][0]['argv'].__setitem__(0,'/usr/bin/false')),
            ('Foreign compiler environment refused',lambda r:r['commands'][0]['environment'].update(LD_PRELOAD='/foreign.so')),
            ('Timed-out receipt refused',lambda r:r['commands'][0].update(timedOut=True)),
            ('Raised native claim refused',lambda r:r.update(nativeAcceptance=True)),
            ('Raised release claim refused',lambda r:r.update(releaseAccepted=True))]:
            value=json.loads(receipt.read_text()); alter(value)
            path=built/(label.replace(' ','-')+'.json'); recipe.write(path,value)
            rejects(label,lambda:recipe.validate_report(path,recipe.sha(path)))
        yes('Restored original report remains valid',recipe.validate_report(receipt,receipt_sha)['passed'])
        for path,value in inputs.items(): yes('Driver input unchanged '+Path(path).name,recipe.sha(path)==value)
        report.update(passed=True,buildReceipt=dict(path=str(receipt),sha256=receipt_sha),lock=dict(path=str(args.lock),sha256=args.sha256))
    except Exception as error: report.update(error=repr(error),traceback=traceback.format_exc())
    recipe.write(out/'report.json',report)
    print(json.dumps(dict(passed=report['passed'],report=str(out/'report.json'),checks=len(report['checks']),error=report.get('error'))))
    return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
