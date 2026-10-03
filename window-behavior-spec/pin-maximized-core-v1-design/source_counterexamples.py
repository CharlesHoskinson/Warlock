#!/usr/bin/env python3
"""Primary-source predicate evidence; no actual compositor/effect execution."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent
checks=[]
def evidence(name,path,needles,result):
 p=B/'primary'/path;s=p.read_text();assert all(n in s for n in needles)
 checks.append({'name':name,'path':str(p.relative_to(B)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sourceLines':[s[:s.index(n)].count('\n')+1 for n in needles], 'predicates':needles,'boundedConsequence':result,'nativeExecution':False})
evidence('actualPinFloatingAndAnyFullscreenRefusal','src/config/shared/actions/ConfigActions.cpp',['!window->m_isFloating || Fullscreen::controller()->isFullscreen(window)'],'Native MAX must be accepted through a proper changed owning core API, not an unchanged PinAction call.')
evidence('preRawModalRefusal','src/desktop/state/FocusState.cpp',['void CFocusState::fullWindowFocus','Refusing focus to window shadowed by modal dialog','rawWindowFocus(pWindow, reason, surface);'],'A rawWindowFocus-only hook cannot reroute the path rejected by preceding modal-parent guard.')
evidence('originalOwnerFollowups','src/config/shared/actions/ConfigActions.cpp',['PWINDOWTOCHANGETO->warpCursor();','g_pInputManager->m_forcedFocus = PWINDOWTOCHANGETO;'],'Rerouted or refused fullWindowFocus does not rewrite caller local owner; original-owner followups need typed actual accepted target.')
evidence('legacyIndependentBitCopy','src/protocols/XDGShell.cpp',['m_self->m_window->m_pinned = true;','createdWindow->m_pinned = true;'],'Effective protection and independent child pin intent are conflated by two real source writes.')
evidence('renderFloatingOnly','src/render/Renderer.cpp',['!w->m_pinned || !w->m_isFloating'],'Adding native tiled MAX pin alone omits protected owner from final pin pass.')
evidence('hitFloatingOnly','src/desktop/state/ViewHitTester.cpp',['w->m_isFloating && w->m_isMapped','w->m_pinned'],'Final render band and native hit protection require matching nonfloating MAX policy.')
evidence('coreFocusPrecedesSeatAcceptance','src/desktop/state/FocusState.cpp',['m_focusWindow                             = pWindow;','rawSurfaceFocus(PWINDOWSURFACE, pWindow);'],'Core owner can change before native Seat acceptance; no atomically inferred owner+Seat success.')
evidence('surfaceRefusalOrMissingKeyboard','src/desktop/state/FocusState.cpp',['g_pSeatManager->m_seatGrab && !g_pSeatManager->m_seatGrab->accepts(pSurface)','if (g_pSeatManager->m_keyboard)'],'Seat refusal/lack of keyboard must retain partial actual observation and suppress success followup.')
(B/'source-counterexamples.json').write_text(json.dumps({'scope':'read-only primary source plus abstract model negatives, no native reproduction','checks':checks},indent=2)+'\n')
print(len(checks),'source predicates confirmed')
