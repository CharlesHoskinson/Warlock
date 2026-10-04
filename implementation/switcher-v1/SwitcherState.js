.pragma library

// Generation/ordinal originates synchronously in the compositor Lua callback.
// The shell owns builder/commit tokens and retains terminal-generation tombstones.
var MAX_STEPS = 4096;
function create(session, epoch) {
    return {session:session, epoch:epoch, generation:0, phase:"idle", steps:{},
            finalOrdinal:0, released:false, builder:false, token:"", request:null,
            selected:0, effect:null, claimed:false};
}
function copy(state) { return JSON.parse(JSON.stringify(state)); }
function integer(value, maximum) { return typeof value === "number" && value % 1 === 0 && value > 0 && value <= maximum; }
function current(state, session, generation) {
    return session === state.session && integer(generation, 2147483647) && generation >= state.generation;
}
function fresh(state, generation) {
    var next=create(state.session,state.epoch);next.generation=generation;
    next.phase="pending";next.token=next.epoch+":"+generation;return next;
}
function result(state, accepted, builder, effect) {
    return {state:state, accepted:!!accepted, builder:!!builder, effect:effect || null};
}
function selected(state) {
    var sum=0; Object.keys(state.steps).forEach(function(key){sum+=state.steps[key]});
    var count=state.request && state.request.candidates.length || 0;
    return count ? (state.manualSelected === undefined ? ((sum % count) + count) % count : state.manualSelected) : 0;
}
function settle(state) {
    if(!state.request)return result(state,true,false);
    state.selected=selected(state);
    if(!state.released){state.phase="open";return result(state,true,false);}
    for(var i=1;i<=state.finalOrdinal;i++)if(!Object.prototype.hasOwnProperty.call(state.steps,String(i))){state.phase="pending";return result(state,true,false);}
    state.phase="committed";
    var candidate=state.request.candidates[state.selected];
    state.effect={epoch:state.epoch,generation:state.generation,token:state.token,candidate:copy(candidate)};
    return result(state,true,false,copy(state.effect));
}
function step(state, session, generation, ordinal, direction) {
    if(!current(state,session,generation) || !integer(ordinal,MAX_STEPS) || (direction!==1 && direction!==-1))return result(state,false,false);
    var next=generation>state.generation?fresh(state,generation):copy(state);
    if(next.phase!=="pending" && next.phase!=="open")return result(state,false,false);
    if(next.released && ordinal>next.finalOrdinal)return result(state,false,false);
    if(Object.prototype.hasOwnProperty.call(next.steps,String(ordinal))){
        if(next.steps[String(ordinal)]!==direction){next.phase="cancelled";next.effect=null;return result(next,false,false);}
        return result(state,true,false);
    }
    next.steps[String(ordinal)]=direction;
    if(next.manualSelected !== undefined && !next.released && next.request) {
        var count=next.request.candidates.length;
        next.manualSelected=((next.manualSelected+direction)%count+count)%count;
    }
    var builder=!next.builder;next.builder=true;
    var settled=settle(next);settled.builder=builder;return settled;
}
function release(state, session, generation, finalOrdinal) {
    if(!current(state,session,generation) || !integer(finalOrdinal,MAX_STEPS))return result(state,false,false);
    var next=generation>state.generation?fresh(state,generation):copy(state);
    if(next.phase!=="pending" && next.phase!=="open")return result(state,false,false);
    if(next.released)return result(state,next.finalOrdinal===finalOrdinal,false);
    if(Object.keys(next.steps).some(function(key){return Number(key)>finalOrdinal;}))return result(state,false,false);
    next.released=true;next.finalOrdinal=finalOrdinal;return settle(next);
}
function validCandidate(candidate) {
    return candidate && typeof candidate.address==="string" && /^0x[0-9a-fA-F]+$/.test(candidate.address)
        && typeof candidate.pid==="number" && candidate.pid%1===0 && candidate.pid>0
        && (typeof candidate.stableId==="string" || typeof candidate.stableId==="number") && String(candidate.stableId).length>0;
}
function ready(state, epoch, generation, token, request) {
    if(epoch!==state.epoch || generation!==state.generation || token!==state.token || state.phase!=="pending" || !state.builder || state.request)return result(state,false,false);
    var next=copy(state);
    if(!request || request.mode!=="switcher" || !Array.isArray(request.candidates) || !request.candidates.length || request.candidates.length>MAX_STEPS
        || !request.candidates.every(validCandidate)) {next.phase="cancelled";return result(next,false,false);}
    next.request=copy(request);return settle(next);
}
function cancel(state, generation, token) {
    if(generation!==undefined && (generation!==state.generation || token!==state.token))return result(state,false,false);
    var next=copy(state);next.phase="cancelled";next.effect=null;next.request=null;return result(next,true,false);
}
function claim(state, epoch, generation, token) {
    if(state.phase!=="committed" || state.claimed || epoch!==state.epoch || generation!==state.generation || token!==state.token || !state.effect)return {state:state,candidate:null};
    var next=copy(state);next.claimed=true;return {state:next,candidate:copy(next.effect.candidate)};
}
function choose(state, index) {
    if(state.phase!=="open" || state.released || !state.request || typeof index!=="number" || index%1!==0 || index<0 || index>=state.request.candidates.length)return result(state,false,false);
    var next=copy(state);next.manualSelected=index;next.selected=index;return result(next,true,false);
}
function barrier(state, session, generation) {
    if(!current(state,session,generation) || generation<=state.generation)return result(state,false,false);
    var next=fresh(state,generation);next.phase="cancelled";return result(next,true,false);
}
