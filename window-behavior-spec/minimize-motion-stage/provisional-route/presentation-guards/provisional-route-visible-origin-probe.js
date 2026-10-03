const fs = require('fs');
const vm = require('vm');
const crypto = require('crypto');
const path = '/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/presentation-guards/GlobalRoute.js';
const raw = fs.readFileSync(path, 'utf8');
const sandbox = {module: {exports: {}}};
vm.runInNewContext(raw.replace(/^\.pragma library\s*/, ''), sandbox);
const {GlobalRoute} = sandbox.module.exports;
const identity = ['0x10', 'abc', 123];
const seed = {
    identity, atlasIdentity: identity, completeAtlas: true,
    digest: '1'.repeat(64), full: {x: 80, y: 20, width: 80, height: 60},
    icon: {x: 180, y: 0, width: 10, height: 10},
    current: {x: 130, y: 10, width: 45, height: 35},
    nativeRect: {x: 82, y: 48, width: 76, height: 30},
    outputs: ['left', 'right'], destination: 'right', topology: 1,
    token: 'abcdef123456-1', operation: 'minimize'
};
const copy = x => JSON.parse(JSON.stringify(x));
const equal = (a, b) => ['x', 'y', 'width', 'height'].every(k => a[k] === b[k]);
function present(r, output, sequence, time) {
    const frame = {identity, token: r.token, topology: r.topology, output,
        digest: r.digest, rect: copy(r.current), sequence, time};
    if (!r.submit(frame) || !r.present(frame)) throw Error('valid baseline frame rejected');
}
const route = new GlobalRoute(seed);
present(route, 'left', 1, 10);
present(route, 'right', 1, 10);
route.tick(80);
const displayed = copy(route.presented.left.rect);
const computed = copy(route.current);
const accepted = route.reserve({identity, previousToken: route.token,
    token: 'abcdef123456-2', operation: 'restore'});
const asynchronous = new GlobalRoute(seed);
present(asynchronous, 'left', 1, 10);
present(asynchronous, 'right', 1, 10);
asynchronous.tick(50);
present(asynchronous, 'left', 2, 60);
const perOutput = copy(asynchronous.presented);
asynchronous.reserve({identity, previousToken: asynchronous.token,
    token: 'abcdef123456-2', operation: 'restore'});
const malformed = new GlobalRoute(seed);
const malformedAccepted = malformed.reserve({identity, previousToken: malformed.token,
    token: 'abcdef123456-2-extra', operation: 'restore'});
const report = {
    sourceSHA256: crypto.createHash('sha256').update(raw).digest('hex'),
    productionTouched: false,
    computedWithoutPresentation: {displayed, computed, accepted, origin: copy(route.from),
        originMatchesDisplayed: equal(route.from, displayed)},
    asynchronousOutputs: {displayed: perOutput, origin: copy(asynchronous.from),
        originMatchesLeft: equal(asynchronous.from, perOutput.left.rect),
        originMatchesRight: equal(asynchronous.from, perOutput.right.rect)},
    malformedTokenAccepted: malformedAccepted
};
fs.writeFileSync('/home/hoskinson/window-integration-qa/provisional-route-visible-origin-report.json',
    JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
