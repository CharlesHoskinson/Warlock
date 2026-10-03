const fs = require('fs');
const assert = require('assert');
const app = require(process.argv[2]).Elm.Replay.init({flags: null});
const deadline = setTimeout(() => { throw new Error('Original decoder deadline'); }, 15000);
function replay(message) {
  return new Promise(resolve => {
    const receive = value => { app.ports.outgoing.unsubscribe(receive); resolve(value); };
    app.ports.outgoing.subscribe(receive);
    app.ports.incoming.send(message);
  });
}
(async () => {
  const cases = [];
  for (const path of process.argv.slice(4)) {
    const native = JSON.parse(fs.readFileSync(path));
    assert(native.passed && native.cleanupPassed && !native.error);
    const packets = [...Object.entries(native.captures).map(([name,capture]) => [name,capture.renderTrace]),
      ...(native.identityTracePackets || []).map((packet,index) => ['identity-'+index,packet]),
      ...(native.inputMaskTracePackets || []).map((packet,index) => ['input-mask-'+index,packet])];
    for (const [name,packet] of packets) {
      const result = await replay(packet);
      assert.equal(result.passed,true,name+': '+result.error);
      for (const field of ['canonicalScene','currentSceneAdmitted','currentSceneEvidence','presentationEvidence','bindingCorrelationVerified'])
        assert.equal(result.summary[field],false,name+': '+field);
      if (packet.retained) assert(result.summary.frames.every(frame => !frame.usableDispatchTrace));
      cases.push({report:path,name,passed:true});
    }
  }
  fs.writeFileSync(process.argv[3],JSON.stringify({passed:true,checks:cases.length,scope:'Recorded native dispatch packets only; no scene or presentation acceptance',cases},null,2)+'\n');
  clearTimeout(deadline);
})().catch(error => { clearTimeout(deadline); console.error(error); process.exitCode=1; });
