#!/usr/bin/env python3
"""Check installed ownership projection against Quint-generated snapshots.

This exercises the actual helper and its on-disk state parser. Live QA covers
the compositor commands; this replay does not execute monitor hotplug itself.
"""
import json
from pathlib import Path
import sys
import tempfile
from mbt_desktop import decode
sys.path.insert(0, str(Path.home()/'.local/share/hypr-window-controls'))
from window_state import monitor_owner


def main():
    paths=sorted((Path(__file__).parent/'qa-traces').glob('monitor-owner-*.itf.json'))
    assert paths,'Generate monitor_owner Quint traces first'
    checked=0
    with tempfile.TemporaryDirectory(prefix='monitor-owner-qa-') as temp:
        runtime=Path(temp)
        state=runtime/'hypr-windowctl'
        state.mkdir()
        for path in paths:
            for i,trace_state in enumerate(json.loads(path.read_text())['states']):
                s=decode(trace_state)['s']
                home=str(s['desktop']+1)
                window=dict(address='0x123',pid=42,stableId=str(s['identity']),monitor=s['raw'],
                            workspace={'name':'special:win-minimized' if s['minimized'] else home})
                (state/'0x123').write_text(f"{home} 0 {s['savedIdentity']}\n")
                (state/'0x123.monitor.json').write_text(json.dumps(dict(pid=42,stableId=str(s['savedIdentity']),
                    homeWorkspace=str(s['savedHome']+1),monitorName=s['savedMonitor'])))
                monitors=[dict(id=0,name='physical',focused=True)]
                if s['present']:monitors.append(dict(id=1,name=s['outputName']))
                workspaces=[dict(name=home,monitorID=s['home'])] if s['homeExists'] else []
                valid=s['savedIdentity']==s['identity'] and s['savedHome']==s['desktop']
                if not s['minimized'] or not valid:expected=s['raw']
                elif s['homeExists']:expected=s['home']
                elif s['savedMonitor']=='physical':expected=0
                elif s['present'] and s['savedMonitor']==s['outputName']:expected=1
                else:expected=0
                actual=monitor_owner(window,monitors,workspaces,runtime)
                assert actual==expected,(path.name,i,s,actual,expected)
                checked+=1
    print(f'Monitor ownership projection: {len(paths)} traces, {checked} installed-helper states passed')


if __name__=='__main__':main()
