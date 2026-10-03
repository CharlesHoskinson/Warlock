.pragma library
// Offline prototype shared by output fragments. Integrating code supplies
// fresh identity/family/native-geometry proof and actual presented rectangles.
function clone(value) { return JSON.parse(JSON.stringify(value)) }
function same(a,b) { return JSON.stringify(a)===JSON.stringify(b) }
function validRect(r) { return r && ['x','y','width','height'].every(function(k){return Number.isFinite(r[k])}) && r.width>0 && r.height>0 }
function mix(a,b,p) {
    var q=p<.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2
    var r={};['x','y','width','height'].forEach(function(k){r[k]=a[k]+(b[k]-a[k])*q});return r
}
function GlobalRoute(seed) {
    if(!seed.completeAtlas || !validRect(seed.full) || !validRect(seed.icon) || !validRect(seed.current) || !seed.digest || !same(seed.identity,seed.atlasIdentity))throw Error('incomplete or foreign atlas')
    if(!seed.outputs.length || (new Set(seed.outputs)).size!==seed.outputs.length || seed.outputs.indexOf(seed.destination)<0)throw Error('invalid output participants/destination')
    this.identity=clone(seed.identity);this.nativeRect=clone(seed.nativeRect);this.full=clone(seed.full);this.icon=clone(seed.icon)
    this.digest=seed.digest;this.outputs=seed.outputs.slice();this.destination=seed.destination;this.topology=seed.topology
    this.token=seed.token;this.acceptedOperation=seed.operation;this.operation=seed.operation;this.current=clone(seed.current)
    this.from=clone(seed.current);this.to=clone(seed.operation==='minimize'?seed.icon:seed.full)
    this.phase='running';this.validated=true;this.elapsed=0;this.duration=seed.operation==='minimize'?190:230
    this.progress=0;this.ready={};this.endReady={};this.readySent=false;this.doneSent=false;this.events=[];this.frames=[]
}
GlobalRoute.prototype.reserve=function(request) {
    if(!same(request.identity,this.identity) || request.previousToken!==this.token || ['minimize','restore'].indexOf(request.operation)<0)return false
    var old=this.token.split('-'),next=request.token.split('-')
    if(next[0]!==old[0] || !Number.isSafeInteger(Number(next[1])) || Number(next[1])<=Number(old[1]))return false
    this.token=request.token;this.operation=request.operation;this.from=clone(this.current)
    this.to=clone(request.operation==='minimize'?this.icon:this.full);this.elapsed=0;this.progress=0;this.duration=request.operation==='minimize'?190:230
    this.phase='provisional';this.validated=false;this.ready={};this.endReady={};this.readySent=false;this.doneSent=false
    return true
}
GlobalRoute.prototype.tick=function(deltaMs) {
    if(!Number.isFinite(deltaMs) || deltaMs<0)throw Error('invalid frame time')
    if(['provisional','running','rollback'].indexOf(this.phase)<0)return
    this.elapsed+=deltaMs;this.progress=Math.min(1,this.elapsed/this.duration)
    this.current=mix(this.from,this.to,this.progress)
    // A provisional endpoint never produces a native ready/done signal.
}
GlobalRoute.prototype.promote=function(proof) {
    if(this.phase!=='provisional' || !same(proof.identity,this.identity) || proof.token!==this.token || !proof.familyValidated || !same(proof.nativeRect,this.nativeRect) || proof.digest!==this.digest || proof.topology!==this.topology)return false
    this.validated=true;this.phase='running';this.acceptedOperation=this.operation;this.completeIfPresented();return true
}
GlobalRoute.prototype.reject=function(proof) {
    if(this.phase!=='provisional' || !same(proof.identity,this.identity) || proof.token!==this.token || !proof.priorIntentFreshlyValidated)return false
    this.from=clone(this.current);this.operation=this.acceptedOperation;this.to=clone(this.operation==='minimize'?this.icon:this.full)
    this.phase='rollback';this.validated=true;this.elapsed=0;this.progress=0;this.ready={};this.endReady={};this.readySent=false;this.doneSent=false
    return true
}
GlobalRoute.prototype.present=function(output,token,topology,rect,timestamp) {
    if(token!==this.token || topology!==this.topology || this.outputs.indexOf(output)<0 || !validRect(rect) || !Number.isFinite(timestamp))return false
    this.frames.push({output:output,token:token,time:timestamp,rect:clone(rect),phase:this.phase,digest:this.digest});if(this.frames.length>512)this.frames.shift()
    this.ready[output]=true
    if(same(rect,this.to))this.endReady[output]=true
    this.completeIfPresented();return true
}
GlobalRoute.prototype.completeIfPresented=function() {
    if(!this.validated || !this.outputs.every(function(o){return this.ready[o]},this))return
    if(!this.readySent) {this.readySent=true;this.events.push({kind:this.phase==='rollback'?'rollbackReady':'ready',token:this.token,identity:clone(this.identity),operation:this.operation})}
    if(this.progress===1 && this.outputs.every(function(o){return this.endReady[o]},this) && !this.doneSent) {
        this.doneSent=true;this.events.push({kind:this.phase==='rollback'?'rollbackDone':'done',token:this.token,identity:clone(this.identity),operation:this.operation});this.phase='idle'
    }
}
GlobalRoute.prototype.removeOutput=function(output) {
    if(this.outputs.indexOf(output)<0)return false
    this.phase='cancelled';this.ready={};this.endReady={};this.validated=false
    this.events.push({kind:'needsFreshSettlement',token:this.token,identity:clone(this.identity),previouslyAcceptedOperation:this.acceptedOperation});return true
}
GlobalRoute.prototype.close=function() {this.phase='cancelled';this.validated=false;this.digest='';this.ready={};this.endReady={}}
if(typeof module!=='undefined')module.exports={GlobalRoute:GlobalRoute}
