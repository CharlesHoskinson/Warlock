#!/usr/bin/env python3
"""Replay session model into staged helper; generated snapshots, not native QA."""
import copy
import importlib.machinery
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch
sys.path.insert(0,str(Path.home()/'window-behavior-spec'))
from mbt_desktop import decode

ROOT=Path(__file__).resolve().parent
HELPER=Path(os.getenv('SNAP_SESSION_HELPER',str(Path.home()/'.local/bin/hypr-snap-groups')))
helper=importlib.machinery.SourceFileLoader('session_snap_helper',str(HELPER)).load_module()


def window(address,identity):
    return {'address':hex(address),'pid':40+address,'initialClass':'qa','stableId':str(identity),
            'workspace':{'name':'1'},'monitor':0,'at':[100,100],'size':[640,500]}

def resolve(expected):
    target=expected['target']['tag']
    with patch.dict(helper.os.environ,{},clear=False):
        helper.os.environ.pop('HYPRLAND_INSTANCE_SIGNATURE',None)
        if target=='Explicit':helper.os.environ['HYPRLAND_INSTANCE_SIGNATURE']=str(expected['current'])
        instances=[] if target=='Missing' else [{'instance':str(expected['current'])},{'instance':'other'}] if target=='Ambiguous' else [{'instance':str(expected['current'])}]
        with patch.object(helper,'ctl',return_value=json.dumps(instances)) as ctl:
            if target in ['Ambiguous','Missing']:
                try:helper.compositor_instance()
                except ValueError:return None
                raise AssertionError('Unknown target unexpectedly accepted')
            found=helper.compositor_instance()
            assert found==str(expected['current'])
            assert helper.os.environ['HYPRLAND_INSTANCE_SIGNATURE']==found
            if target=='Explicit':ctl.assert_not_called()
            return found


def main():
    paths=sorted((ROOT/'session-traces').glob('session-*.itf.json'))
    assert paths,'Generate Quint session traces first'
    count=0;events=set()
    for path in paths:
        state={'version':1,'next_id':1,'groups':[{'id':'snap-1','addresses':['0x1','0x2']}],'snapped':{}}
        for a,width in [(1,640),(2,800)]:
            w=window(a,1)
            state['snapped'][hex(a)]={'identity':helper.identity(w),'zone':'left' if a==1 else 'right',
                'workspace':'1','monitor':0,'normalSize':[width,500],'normalRect':[100,100,width,500]}
        for i,expected in enumerate(json.loads(path.read_text())['states']):
            expected=decode(expected)
            windows=[window(a,id) for a,id in expected['live'].items()]
            selected=resolve(expected)
            if i:
                event=expected['lastEvent'];tag=event['tag'];events.add(tag)
                if tag in ['Reload','Record'] and selected is not None:
                    state=helper.session_state(state,selected)
                    helper.sync(state,windows)
                    if tag=='Record':
                        a=event['value']
                        helper.record(state,windows,hex(a),'left' if a==1 else 'right',normal_size=[640,500],normal_position=[100,100])
            actual_saved={int(a,16):int(m['identity'][3]) for a,m in state['snapped'].items()}
            actual_normal={int(a,16):m['normalSize'][0] for a,m in state['snapped'].items()}
            assert actual_saved==expected['saved'],(path.name,i,'persisted identities',actual_saved,expected['saved'])
            assert actual_normal==expected['normal'],(path.name,i,'persisted normal sizes')
            assert int(state.get('instance',0))==expected['tag'],(path.name,i,'session tag')
            eligible={a for a,id in expected['saved'].items() if expected['live'].get(a)==id} if selected is not None and expected['tag'] in [0,expected['current']] else set()
            if selected is not None:
                projected=helper.sync(helper.session_state(copy.deepcopy(state),selected),windows)
                assert set(projected['snapped'])=={hex(a) for a in eligible},(path.name,i,'eligible identities')
                groups=helper.snapshot(projected,windows)
            else:groups=[]
            assert bool(groups)==(len(eligible)>=2),(path.name,i,'group recall')
            count+=1
    assert events=={'Reload','Record','NewSession','IdentityCollisionSession','Close','Reuse','Launch','ExplicitTarget','UniqueTarget','AmbiguousTarget','MissingTarget'},events
    print(f'Session backend replay ({HELPER}): {len(paths)} traces, {count} states, all 11 event types')


if __name__=='__main__':main()
