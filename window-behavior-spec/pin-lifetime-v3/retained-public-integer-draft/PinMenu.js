.pragma library

// A menu generation captures one public member and one immutable native token.
// These functions never contact Hyprland, change focus, or retry an action.
function create() { return {nonce:0,open:false,target:null,token:null,sent:false,status:"closed",receipt:null}; }
function publicTriple(w) {
    if (!w || typeof w.address !== "string" || !/^0x[0-9a-f]+$/.test(w.address) ||
        !Number.isSafeInteger(w.stableId) || w.stableId <= 0 ||
        !Number.isInteger(w.pid) || w.pid <= 0 || w.pid > 2147483647) throw Error("Exact public member required");
    return Object.freeze({address:w.address,stableId:w.stableId,pid:w.pid});
}
function samePublic(a,b) { return a && b && a.address === b.address && a.stableId === b.stableId && a.pid === b.pid; }
function nativeToken(t) {
    var fields=["address","stableId","pid","session","compositorPid","compositorStart","incarnation","epoch","generation"];
    if (!t || Object.keys(t).sort().join() !== fields.sort().join() ||
        !Number.isInteger(t.pid) || t.pid <= 0 || t.pid > 2147483647 ||
        !Number.isInteger(t.compositorPid) || t.compositorPid <= 0 || t.compositorPid > 2147483647) throw Error("Full typed native token required");
    var patterns={address:/^0x[0-9a-f]+$/,stableId:/^[0-9a-f]+$/,session:/^[A-Za-z0-9_]+$/,compositorStart:/^[1-9][0-9]*$/,incarnation:/^[0-9a-f]{32}$/,epoch:/^[1-9][0-9]*$/,generation:/^[1-9][0-9]*$/};
    Object.keys(patterns).forEach(function(k) { if(typeof t[k] !== "string" || !patterns[k].test(t[k])) throw Error("Malformed native token"); });
    ["epoch","generation"].forEach(function(k) { var v=t[k]; if(v.length>20 || (v.length===20 && v>"18446744073709551615")) throw Error("Native generation overflow"); });
    var copy={};fields.forEach(function(k){copy[k]=t[k];});return Object.freeze(copy);
}
function sameToken(a,b) { if(!a || !b) return false;return Object.keys(a).every(function(k){return typeof a[k]===typeof b[k] && a[k]===b[k];}) && Object.keys(a).length===Object.keys(b).length; }
function open(s,w) {
    if(!Number.isSafeInteger(s.nonce) || s.nonce >= Number.MAX_SAFE_INTEGER) throw Error("Menu generation exhausted");
    s.nonce++;s.open=true;s.target=publicTriple(w);s.token=null;s.sent=false;s.status="capturing";s.receipt=null;return s.nonce;
}
function dismiss(s) { s.open=false;s.target=null;s.token=null;s.status="closed"; }
function captured(s,nonce,target,code,receipt) {
    if(!s.open || s.nonce!==nonce || s.sent || !samePublic(s.target,target)) return false;
    s.status="capture-refused";
    try {
        if(code!==0 || !receipt || receipt.result!=="captured" || receipt.nativeWrites!==0 || receipt.nativeCompletionClaimed!==false || receipt.automaticRetries!==0 || !samePublic(receipt.publicIdentity,target)) return false;
        var t=nativeToken(receipt.captured), id=parseInt(t.stableId,16);
        if(!Number.isSafeInteger(id) || id!==target.stableId || t.address!==target.address || t.pid!==target.pid) return false;
        s.token=t;s.status="ready";return true;
    } catch(e) { s.token=null;return false; }
}
function invoke(s) {
    if(!s.open || s.sent || s.status!=="ready" || !s.token) return null;
    var invocation={nonce:s.nonce,token:s.token};s.sent=true;s.status="sending";return invocation;
}
function completed(s,invocation,code,receipt) {
    // Dismissal/replacement never publishes a success for a new menu. A sent
    // action remains independently evidenced by the exact helper, without retry.
    if(!invocation || s.nonce!==invocation.nonce || !s.open || !s.sent) return false;
    s.receipt=receipt;s.status="refused-or-uncertain";
    if(code!==0 || !receipt || receipt.result!=="complete" || receipt.nativeCompletionClaimed!==true || receipt.automaticRetries!==0 || !sameToken(receipt.captured,invocation.token) || !receipt.rawNativeResult || receipt.rawNativeResult.ok!==true || !sameToken(receipt.rawNativeResult.captured,invocation.token)) return false;
    s.status="complete";return true;
}
