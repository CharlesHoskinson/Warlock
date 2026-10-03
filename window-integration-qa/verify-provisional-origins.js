const fs = require('fs'), vm = require('vm'), crypto = require('crypto');
const sourcePath = '/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/presentation-guards/GlobalRoute.js';
const raw = fs.readFileSync(sourcePath, 'utf8');
const sandbox = {module: {exports: {}}};
vm.runInNewContext(raw.replace(/^\.pragma library\s*/, ''), sandbox);
const {GlobalRoute} = sandbox.module.exports;
const identity = ['0x10', 'abc', 123];
const seed = {
    identity, atlasIdentity: identity, completeAtlas: true, digest: '1'.repeat(64),
    full: {x: 80, y: 20, width: 80, height: 60},
    icon: {x: 180, y: 0, width: 10, height: 10},
    current: {x: 130, y: 10, width: 45, height: 35},
    nativeRect: {x: 82, y: 48, width: 76, height: 30},
    outputs: ['left', 'right'], destination: 'right', topology: 1,
    token: 'abcdef123456-1', operation: 'minimize'
};
const copy = x => JSON.parse(JSON.stringify(x));
const equal = (a, b) => ['x', 'y', 'width', 'height'].every(k => a[k] === b[k]);
function observe(r, output, sequence, time) {
    const f = {identity, token: r.token, topology: r.topology, output,
        digest: r.digest, rect: r.rectForOutput(output), sequence, time};
    if (!r.submit(f) || !r.present(f)) throw Error('baseline frame rejected');
}
function route() {
    const r = new GlobalRoute(seed);
    observe(r, 'left', 1, 10); observe(r, 'right', 1, 10);
    return r;
}
const request = r => ({identity, previousToken: r.token,
    token: 'abcdef123456-2', operation: 'restore'});
const unpresented = route();
const displayed = copy(unpresented.presented);
unpresented.tick(80);
const computed = copy(unpresented.current);
const reserved = unpresented.reserve(request(unpresented));
const asyncRoute = route();
asyncRoute.tick(50); observe(asyncRoute, 'left', 2, 60);
const asyncDisplayed = copy(asyncRoute.presented);
const asyncReserved = asyncRoute.reserve(request(asyncRoute));
const malformed = route();
const suffixRejected = !malformed.reserve({...request(malformed), token: 'abcdef123456-2-extra'});
const checks = {
    computedAheadOfDisplay: !equal(computed, displayed.right.rect),
    unpresentedTickKeepsObservedOrigins: reserved && seed.outputs.every(o => equal(unpresented.rectForOutput(o), displayed[o].rect)),
    asynchronousDisplayOriginsPreserved: asyncReserved && seed.outputs.every(o => equal(asyncRoute.rectForOutput(o), asyncDisplayed[o].rect)),
    malformedSuffixRejected: suffixRejected
};
const report = {sourceSHA256: crypto.createHash('sha256').update(raw).digest('hex'),
    checks, allPass: Object.values(checks).every(Boolean), productionTouched: false,
    nativePresentationProved: false};
fs.writeFileSync('/home/hoskinson/window-integration-qa/provisional-origin-repair-report.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
if (!report.allPass) process.exit(1);
