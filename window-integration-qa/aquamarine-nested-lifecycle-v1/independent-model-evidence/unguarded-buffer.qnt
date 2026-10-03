module configure_lifecycle {
  var ack: bool
  var published: bool
  var dead: bool
  var queued: bool
  var publications: int
  var buffers: int
  var frames: int
  var states: int
  var requests: int
  var emissions: List[{kind: str, acknowledged: bool, published: bool, destroyed: bool}]
  val ready = ack and published and not(dead)
  action init = all { ack'=false, published'=false, dead'=false, queued'=false, publications'=0, buffers'=0, frames'=0, states'=0, requests'=0, emissions'=List() }
  action stage = all { ack'=ack, published'=published, dead'=dead, queued'=queued, publications'=publications, buffers'=buffers, frames'=frames, states'=states, requests'=requests, emissions'=emissions }
  action acknowledge = all { ack'=(ack or not(dead)), published'=published, dead'=dead, queued'=(queued or not(dead)), publications'=publications, buffers'=buffers, frames'=frames, states'=states, requests'=requests, emissions'=emissions }
  action announce = {
    val allowed = queued and ack and not(dead) and not(published)
    all { ack'=ack, published'=(published or allowed), dead'=dead, queued'=queued, publications'=publications + (if (allowed) 1 else 0), buffers'=buffers, frames'=frames, states'=states, requests'=requests, emissions'=emissions }
  }
  // State publication and frame request are separate transitions: callbacks may destroy synchronously between them.
  action publishState = all { ack'=ack, published'=published, dead'=dead, queued'=false, publications'=publications, buffers'=buffers, frames'=frames, states'=states+(if (ready and queued) 1 else 0), requests'=requests, emissions'=if (ready and queued) emissions.append({kind:"state",acknowledged:ack,published:published,destroyed:dead}) else emissions }
  action buffer = all { ack'=ack, published'=published, dead'=dead, queued'=queued, publications'=publications, buffers'=buffers+(if (true) 1 else 0), frames'=frames, states'=states, requests'=requests+1, emissions'=if (true) emissions.append({kind:"buffer",acknowledged:ack,published:published,destroyed:dead}) else emissions }
  action frame = all { ack'=ack, published'=published, dead'=dead, queued'=queued, publications'=publications, buffers'=buffers, frames'=frames+(if (ready) 1 else 0), states'=states, requests'=requests+1, emissions'=if (ready) emissions.append({kind:"frame",acknowledged:ack,published:published,destroyed:dead}) else emissions }
  action destroy = all { ack'=ack, published'=published, dead'=true, queued'=false, publications'=publications, buffers'=buffers, frames'=frames, states'=states, requests'=requests, emissions'=emissions }
  action parentLost = destroy
  // Random requests are unfiltered; refusal is implemented in each action, including stale queued callbacks.
  action step = any {stage, acknowledge, announce, publishState, buffer, destroy, frame, parentLost}
  val safeEmissions = emissions.foldl(true, (ok, e) => ok and e.acknowledged and e.published and not(e.destroyed))
  val safePublication = publications >= 0 and publications <= 1 and (not(published) or ack) and (published == (publications==1))
  val accountedEmissions = emissions.length()==buffers+frames+states and buffers>=0 and frames>=0 and states>=0 and buffers+frames<=requests
  val safe = safeEmissions and safePublication and accountedEmissions
  action check(p: bool): bool = all { assert(p), ack'=ack, published'=published, dead'=dead, queued'=queued, publications'=publications, buffers'=buffers, frames'=frames, states'=states, requests'=requests, emissions'=emissions }
  run initialCommitRefusedTest = init.then(buffer).then(frame).then(check(buffers==0 and frames==0 and emissions.length()==0))
  run toplevelDoesNotPublishTest = init.then(stage).then(frame).then(buffer).then(check(buffers==0 and frames==0 and not(ack)))
  run ackAloneDoesNotCommitTest = init.then(acknowledge).then(buffer).then(frame).then(check(buffers==0 and frames==0 and emissions.length()==0))
  run acknowledgedPublicationAllowsBufferTest = init.then(acknowledge).then(announce).then(buffer).then(frame).then(check(buffers==1 and frames==1 and safe))
  run destroyedOutputCannotReappearTest = init.then(destroy).then(acknowledge).then(announce).then(publishState).then(buffer).then(frame).then(check(dead and not(published) and emissions.length()==0))
  run repeatedConfigureStaysUsableTest = init.then(acknowledge).then(announce).then(buffer).then(stage).then(acknowledge).then(announce).then(buffer).then(check(buffers==2 and publications==1))
  run publishedDestructionRefusesMoreTest = init.then(acknowledge).then(announce).then(buffer).then(destroy).then(buffer).then(frame).then(check(buffers==1 and frames==0))
  run ackThenDestroyedQueuedCallbackRefusedTest = init.then(acknowledge).then(destroy).then(announce).then(publishState).then(frame).then(check(publications==0 and states==0 and frames==0))
  run stateListenerDestructionRefusesFrameTest = init.then(acknowledge).then(announce).then(publishState).then(destroy).then(frame).then(check(states==1 and frames==0 and safe))
  run publishedThenDestroyedQueuedReconfigureRefusedTest = init.then(acknowledge).then(announce).then(publishState).then(acknowledge).then(destroy).then(publishState).then(frame).then(check(states==1 and frames==0 and publications==1))
  run idleFrameBeforeAnnouncementRefusedTest = init.then(acknowledge).then(frame).then(check(frames==0 and requests==1))
  run publishedFrameAndBufferRecordedSeparatelyTest = init.then(acknowledge).then(announce).then(frame).then(buffer).then(frame).then(check(frames==2 and buffers==1 and emissions.length()==3 and safe))
  run parentLossBeforeAckInvalidatesQueuedWorkTest = init.then(parentLost).then(acknowledge).then(announce).then(buffer).then(frame).then(check(dead and emissions.length()==0))
  run parentLossAfterAckRefusesAnnouncementTest = init.then(acknowledge).then(parentLost).then(announce).then(publishState).then(frame).then(check(dead and publications==0 and frames==0))
  run publishedParentLossStopsBuffersFramesAndReconfigureTest = init.then(acknowledge).then(announce).then(buffer).then(frame).then(parentLost).then(acknowledge).then(announce).then(publishState).then(buffer).then(frame).then(check(dead and buffers==1 and frames==1 and publications==1 and safe))
}

