.pragma library

var nextGeneration = 0
function allocateGeneration() {
    if (nextGeneration >= 9007199254740991) throw new Error("widget-generation-exhausted")
    return ++nextGeneration
}
function integer(v, min, max) {
    return typeof v === "number" && isFinite(v) && Math.floor(v) === v && v >= min && v <= max
}
function number(v) { return typeof v === "number" && isFinite(v) }
function identity(v) {
    if (!v || typeof v !== "object" || Array.isArray(v)) throw new Error("identity-object")
    var keys = Object.keys(v).sort()
    if (JSON.stringify(keys) !== '["address","pid","stableId"]') throw new Error("identity-keys")
    if (typeof v.address !== "string" || !/^0x[1-9a-f][0-9a-f]{0,15}$/.test(v.address)) throw new Error("identity-address")
    if (typeof v.stableId !== "string" || !/^[1-9a-f][0-9a-f]{0,15}$/.test(v.stableId)) throw new Error("identity-stable")
    if (!integer(v.pid, 1, 2147483647)) throw new Error("identity-pid")
    return {address:v.address, stableId:v.stableId, pid:v.pid}
}
function decode(encoded) {
    if (typeof encoded !== "string" || encoded.length > 131072 || /[^\x00-\x7f]/.test(encoded)) throw new Error("request-size-ascii")
    var values = JSON.parse(encoded)
    if (!Array.isArray(values) || !integer(values.length, 1, 512)) throw new Error("request-family-bound")
    // Exact records have only primitive canonical fields. Refuse lexical duplicate
    // keys (JSON.parse would otherwise silently overwrite), escapes and nesting.
    var records=encoded.match(/\{[^{}]*\}/g)
    if (!records || records.length!==values.length || encoded.indexOf("\\")>=0) throw new Error("request-record-syntax")
    records.forEach(function(raw) {
        var keys=raw.match(/"(?:address|stableId|pid)"\s*:/g)
        if (!keys || keys.length!==3) throw new Error("request-duplicate-key")
        var names=keys.map(function(k){return k.slice(1,k.indexOf('"',1))}).sort()
        if(JSON.stringify(names)!=='["address","pid","stableId"]')throw new Error("request-duplicate-key")
    })
    var addresses = Object.create(null)
    return values.map(function(v) {
        var id = identity(v)
        if (addresses[id.address]) throw new Error("request-duplicate-address")
        addresses[id.address] = true
        return id
    })
}
function validateObservation(v) {
    if (v === null) return null
    if (!v || !v.target || !v.witness) throw new Error("missing-observation")
    var t=v.target, w=v.witness, m=w.monitor, b=w.bar, i=w.icon, c=w.clip, a=w.allocation, s=w.screen
    if (!integer(w.widgetGeneration,1,9007199254740991) || !integer(w.delegateGeneration,1,9007199254740991)) throw new Error("object-generation")
    if (!m || !b || !i || !c || !a || !s || !integer(m.id,0,2147483647) || typeof s.name!=="string" || !s.name.length) throw new Error("output-witness")
    if (typeof b.position!=="string" || ["top","bottom","left","right"].indexOf(b.position)<0) throw new Error("bar-position")
    var nums=[m.x,m.y,m.width,m.height,m.scale,s.width,s.height,b.x,b.y,b.width,b.height,i.x,i.y,i.width,i.height,c.x,c.y,c.width,c.height,a.width,a.height]
    if (!nums.every(number) || m.scale<=0 || m.width<=0 || m.height<=0 || s.width<=0 || s.height<=0 || b.width<=0 || b.height<=0 || i.width<=0 || i.height<=0 || a.width<=0 || a.height<=0) throw new Error("allocation-numeric")
    if (c.x<0 || c.y<0 || c.x+i.width>c.width || c.y+i.height>c.height) throw new Error("allocation-clipped")
    if (t.visible!==true || typeof t.home!=="boolean" || t.screenName!==s.name || t.monitorX!==m.x || t.monitorY!==m.y || !t.rect) throw new Error("target-output")
    if (t.rect.x!==m.x+b.x+i.x || t.rect.y!==m.y+b.y+i.y || t.rect.width!==i.width || t.rect.height!==i.height) throw new Error("target-translation")
    return v
}
function capture(encoded, items) {
    var identities=decode(encoded) // Refuse before any widget lookup.
    if (!Array.isArray(items) || !integer(items.length,1,512)) throw new Error("widget-list-bound")
    var refs=items.slice(), generations=Object.create(null), capturedGenerations=[]
    refs.forEach(function(item) {
        if (!item || typeof item.motionTargetObservation!=="function" || !integer(item.motionWidgetGeneration,1,9007199254740991)) throw new Error("widget-reference")
        if (generations[item.motionWidgetGeneration]) throw new Error("duplicate-widget-generation")
        generations[item.motionWidgetGeneration]=true
        capturedGenerations.push(item.motionWidgetGeneration)
    })
    var all=identities.map(function(id) {
        return refs.map(function(item) {
            var v=validateObservation(item.motionTargetObservation(id))
            if(v && v.witness.widgetGeneration!==item.motionWidgetGeneration) throw new Error("widget-generation-mismatch")
            return v
        })
    })
    // Re-observe every candidate, including missing ones, after the bounded family lookup.
    all.forEach(function(row,n) { row.forEach(function(v,k) {
        var fresh=validateObservation(refs[k].motionTargetObservation(identities[n]))
        if (JSON.stringify(v)!==JSON.stringify(fresh)) throw new Error("observation-changed")
    }) })
    refs.forEach(function(item,k) {if(item.motionWidgetGeneration!==capturedGenerations[k])throw new Error("widget-lifetime-changed")})
    var members=identities.map(function(id,n) {
        var candidates=all[n].filter(function(v) {return v!==null})
        // Explicit tie index avoids depending on sort stability.
        candidates=candidates.map(function(v,k){return {value:v,index:k}})
        candidates.sort(function(a,b){return (a.value.target.home?0:1)-(b.value.target.home?0:1)||a.index-b.index})
        var chosen=candidates.length ? candidates[0].value : null
        return {identity:id,target:chosen ? chosen.target : null,witness:chosen ? chosen.witness : null}
    })
    return {schema:"motion-targets-v1",queryKind:"one-bulk-observation",members:members}
}
