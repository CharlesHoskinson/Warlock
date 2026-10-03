"""Pure acceptance oracles for actual V4 host evidence, never input or IPC."""
import os,re
from pathlib import Path
CORE='efb50993780079460b0cbed1363e2166a2de1d9f'
AQ_SHA='4ed46e823441b7c9539193cb16020dbfe9297a9635ffcadca442452b9a64a63f'
MARKER='Private AQ_BACKENDS=wayland: mandatory parent, no DRM or libseat backend'
BAD=r'\[libseat\]|DRM Backend failed|Starting the DRM backend|enabling fallbacks|error [0-9]+:|Broken pipe|parent transport failed|xdg_surface[^\n]*never[^\n]*configured'
def ipc_complete(evidence):
    rows=evidence.get('ipcReadiness',[])
    if len(rows)!=1:return False
    row=rows[0];socket=row.get('socket',{});version=row.get('version',{});peer=row.get('peer',{})
    expected=str(Path(evidence['runtime'])/'hypr'/evidence['signature']/'.socket.sock')
    return all((row.get('path')==expected,socket.get('path')==expected,socket.get('uid')==os.getuid(),
        socket in evidence.get('sockets',[]),peer.get('pid')==evidence['compositorPID'],peer.get('uid')==os.getuid(),
        row.get('request')=='j/version',row.get('completeServerEOF') is True,
        2<=row.get('replyBytes',0)<=65536,bool(re.fullmatch('[a-f0-9]{64}',row.get('replySHA256',''))),
        version.get('commit')==CORE))
def transport(logs):
    text='\n'.join(logs)
    bad=re.findall(BAD,text,re.I)
    configured=bool(re.search(r'Output WAYLAND-1: configure surface with [0-9]+',text))
    return dict(pass_=MARKER in text and configured and not bad,mandatoryMarker=MARKER in text,
        configureACKHandlerObserved=configured,forbiddenDiagnostics=bad)
