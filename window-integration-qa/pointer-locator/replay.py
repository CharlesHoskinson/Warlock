#!/usr/bin/env python3
"""Replay retained Quint states against the real staged C++ state helper."""
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
def decode(value):
    if isinstance(value,list):return [decode(x) for x in value]
    if isinstance(value,dict):
        if '#bigint' in value:return int(value['#bigint'])
        if '#tup' in value:return tuple(decode(x) for x in value['#tup'])
        if '#set' in value:return set(decode(x) for x in value['#set'])
        if '#map' in value:return {decode(k):decode(v) for k,v in value['#map']}
        return {k:decode(v) for k,v in value.items()}
    return value
def line(state):
    event=state['lastEvent'];tag=event['tag'];v=event['value']
    # Quarter-unit coordinates exercise the helper's fractional arithmetic.
    if tag=='Claim':return f"C {v} {state['owners'][v]}"
    if tag=='Disconnect':return f"D {v[0]} {v[1]}"
    if tag=='Query':return f"Q {v[0]} {v[1]} {state['x']/4} {state['y']/4} {state['originX']/4} {state['originY']/4}"
    if tag=='Move':return f"M {v[0]/4} {v[1]/4}"
    if tag=='Retire':return 'R'
    if tag in ('Hover','KeyboardFocus'):return 'N'
    raise ValueError(tag)
def main():
    traces=sorted((HERE/'traces').glob('*.itf.json'))
    assert len(traces)==41, 'expected 11 named and30 random retained traces'
    subprocess.run(['c++','-std=c++20','-Wall','-Wextra','-Werror',str(HERE/'replay_state.cpp'),'-o',str(HERE/'replay_state')],check=True)
    outcomes=[]
    for path in traces:
        states=decode(json.loads(path.read_text()))['states'][1:]
        result=subprocess.run([str(HERE/'replay_state')],input='I\n'+'\n'.join(line(s) for s in states)+'\n',text=True,capture_output=True,check=True)
        rows=result.stdout.splitlines();assert len(rows)==len(states)
        for index,(state,row) in enumerate(zip(states,rows),1):
            values=row.split();pending=int(values[0]);replied=values[1]=='1'
            sent=set((int(p.rsplit(':',1)[0]),int(p.rsplit(':',1)[1])) for p in values[4:])
            assert pending==len(state['pending']) and replied==state['replied'] and sent==state['sent'], (path.name,index,state['lastEvent'],row)
            if replied:assert (float(values[2]),float(values[3]))==(state['replyX']/4,state['replyY']/4),(path.name,index,row)
        outcomes.append({'trace':path.name,'states':len(states),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    report={'passed':True,'nativeIntegrated':False,'traces':len(outcomes),'replayedStates':sum(r['states'] for r in outcomes),'actualHelperSHA256':hashlib.sha256((HERE/'PointerLocatorState.hpp').read_bytes()).hexdigest(),'outcomes':outcomes}
    (HERE/'replay-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"PASS: {report['traces']} traces / {report['replayedStates']} actual C++ state transitions")
if __name__=='__main__':main()
