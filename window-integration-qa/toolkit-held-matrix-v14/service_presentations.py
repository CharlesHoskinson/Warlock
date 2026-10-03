"""Require real V12 commits bound to actual uploaded/rendered source events."""
from capture_evidence import captured_and_seeded,unchanged_pairs

def validate(packet,operation,members):
    captured=captured_and_seeded(packet,operation,members)
    expected={(str(row['stableId']),row['pid']) for row in members};events=packet['rendererEvents'];matches=[]
    for record in packet['history']:
        if len(record['members'])!=3 or record['operation']!=operation or {(str(row['stableId']),row['pid']) for row in record['members']}!=expected:continue
        if not record['validated'] or not record['ready'] or record['profile'].get('failure') or record['profile'].get('settlementFailure') or record['profile'].get('settlementReason')!='native handover complete':continue
        commits=record['results'];reason='presented ready' if operation=='minimize' else 'presented endpoint'
        if len(commits)!=3 or {(str(row['identity'][1]),row['identity'][2]) for row in commits}!=expected or any(row['operation']!=operation or row['reason']!=reason for row in commits):continue
        token=record['token'];sources=record['sources'];digests=[{k:row[k] for k in ('stableId','pid','digest')} for row in sources]
        authority=[event for event in events if event.get('event')==('ready' if operation=='minimize' else 'endpoint') and event.get('token')==token and event.get('servicePromoted') is True and event.get('sourceDigests')==digests]
        complete=[event for event in events if event.get('event')=='presented' and event.get('accepted') is True and event.get('token')==token and [(str(row['stableId']),row['pid'],row['digest']) for row in event.get('members',[])]==[(str(row['stableId']),row['pid'],row['digest']) for row in sources]]
        bound=[]
        for presentation in complete:
            swap=[event for event in events if event.get('event')=='swap' and event.get('success') is True and all(event.get(key)==presentation.get(key) for key in ('token','sequence','output','generation','members'))]
            if len(swap)==1:bound.append(dict(presentation=presentation,swap=swap[0]))
        if authority and bound:matches.append(dict(record=record,authority=authority,boundPresentations=bound))
    if len(matches)!=1:raise ValueError('One exact complete family native handover from actual presentation required')
    retirement=packet['retirement']
    if (not retirement['actorDirectoryGone'] or not retirement['originalRetirementDelegatedOnce'] or not retirement['productRegistryRemoved'] or retirement['observedControllerBindings']!=1 or not retirement['rendererClosed'] or retirement['rendererExitCode']!=0):raise ValueError('Actual actor/renderer normal resource retirement required')
    return dict(capture=captured,actualPresentation=matches[0],cachePairs=unchanged_pairs(packet,members))
