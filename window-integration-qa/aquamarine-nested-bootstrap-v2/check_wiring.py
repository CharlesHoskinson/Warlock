#!/usr/bin/env python3
"""Structural checks of actual private source; not native callback execution."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent
w=(B/'candidate/src/backend/Wayland.cpp').read_text();b=(B/'candidate/src/backend/Backend.cpp').read_text();checks=[]
def block(text,marker):
 start=text.index(marker);begin=text.index('{',start);depth=0
 for end in range(begin,len(text)):
  depth+=text[end]=='{';depth-=text[end]=='}'
  if depth==0:return text[begin:end+1]
 raise AssertionError('Unclosed source block '+marker)
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
create=block(b,'CBackend::create(');selected=block(create,'if (selection == NestedPolicy::Selection::Wayland)')
check('invalid explicit selection returns before backend construction',create.index('Selection::Invalid')<create.index('return nullptr')<create.index('new CBackend'))
check('mandatory parent placed first and only explicit headless copied as auxiliary',selected.index('selectedBackends.clear')<selected.index('AQ_BACKEND_WAYLAND')<selected.index('AQ_BACKEND_REQUEST_MANDATORY')<selected.index('selectedBackends.push_back(parent)')<selected.index('AQ_BACKEND_HEADLESS') and 'AQ_BACKEND_DRM' not in selected)
start=block(b,'CBackend::start(');mandatory=block(start,'if (optionsForType(impl->type()).backendRequestMode == AQ_BACKEND_REQUEST_MANDATORY)')
check('failed mandatory startup clears implementations and returns false','implementations.clear();' in mandatory and 'return false;' in mandatory)
gpu=block(b,'CBackend::onNewGpu(')
check('late GPU explicit selection refused before DRM creation',gpu.index('Selection::Unspecified')<gpu.index('return;')<gpu.index('CDRMBackend::fromGpu'))
toplevel=block(w,'waylandState.xdgToplevel->setConfigure(')
check('toplevel only stages size, never publishes/frame-kicks','stageSize(w, h)' in toplevel and not any(token in toplevel for token in ['events.state.emit','events.newOutput.emit','frameReady.emit']))
configure=block(w,'waylandState.xdgSurface->setConfigure(')
check('ACK sent before acknowledged state and deferred publication',configure.index('sendAckConfigure(serial)')<configure.index('lifecycle->acknowledge()')<configure.index('idleCallbacks.emplace_back'))
check('configure deferred callback uses weak lifetime and poststate guard',configure.index('weak.lock()')<configure.index('lifecycle->announce()')<configure.index('events.newOutput.emit')<configure.index('events.state.emit')<configure.index('!lifecycle->bufferAllowed()')<configure.index('sched.frameReady.emit'))
relay=block(w,'frameReadyListener = sched.frameReady.listen(')
check('shared public frame relay requires real lifecycle authority','lifecycle->bufferAllowed()' in relay and relay.index('bufferAllowed()')<relay.index('events.frame.emit'))
idle=block(w,'frameIdle = makeShared<std::function<void(void)>>(')
check('idle frame guarded before scheduler frame emission',idle.index('bufferAllowed()')<idle.index('sched.frameReady.emit'))
commit=block(w,'CWaylandOutput::commit(')
check('actual buffer commit refuses before snapshot/attach',commit.index('bufferAllowed()')<commit.index('state->snapshot()')<commit.index('sendAttach'))
destroy=block(w,'CWaylandOutput::destroy(')
check('destroy invalidates lifecycle before public destroy and callbacks',destroy.index('second->destroy()')<destroy.index('events.destroy.emit()') and 'frameCallback.reset()' in destroy and 'sched.invalidate()' in destroy)
frame=block(w,'CWaylandOutput::onFrameDone(')
check('frame completion holds output and checks authority before present',frame.index('self.lock()')<frame.index('bufferAllowed()')<frame.index('events.present.emit'))
transport=block(w,'const auto transportAlive =')
check('parent error invalidates every lifecycle/scheduler and clears strict readiness','wl_display_get_error' in transport and 'Selection::Wayland' in transport and 'backend->ready = false' in transport and 'second->destroy()' in transport and 'frameCallback.reset()' in transport and 'sched.invalidate()' in transport and 'return false' in transport)
backend_start=block(w,'CWaylandBackend::start(')
check('Wayland startup rejects real dispatch failure','if (!dispatchEvents())' in backend_start and 'return false;' in backend_start and 'events.newOutput.emit' not in backend_start)
report={'result':'pass','checks':checks,'scope':'Structural source wiring only; real transport loss and callback reentrancy require native proof','sources':{str(B/'candidate/src/backend'/name):hashlib.sha256((B/'candidate/src/backend'/name).read_bytes()).hexdigest() for name in ['Wayland.cpp','Backend.cpp','NestedLifecycle.hpp']}}
print(json.dumps(report,indent=2))
