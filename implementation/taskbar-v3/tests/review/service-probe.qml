import QtQuick
import Quickshell
import "../../widget_v68" as Candidate

// No windows. Root must launch offscreen through protected qa_run.py with a
// fresh private TASKBAR_FAKE_STATE_DIR and TASKBAR_FAKE_HELPER=fake-observer.py.
ShellRoot {
  id: test
  property bool sawOfflineAfterFirst: false
  property bool done: false
  property int phases: 0
  Candidate.Service {
    id: observer
    helper: Quickshell.env("TASKBAR_FAKE_HELPER")
    onOnlineChanged: if (!online && acceptedSnapshots === 1) test.sawOfflineAfterFirst = true
    onAcceptedSnapshotsChanged: {
      if (acceptedSnapshots === 2) {
        if (streamState.epoch !== "second" || streamState.sequence !== 1) test.fail("fresh epoch not accepted after process restart")
        observer.refresh()
      }
      if (acceptedSnapshots === 3) {
        if (!test.sawOfflineAfterFirst) test.fail("exit did not invalidate online state")
        if (rejectedSnapshots !== 2) test.fail("stale and foreign epochs not both rejected")
        if (streamState.epoch !== "second" || streamState.sequence !== 2) test.fail("refresh did not deliver the next snapshot")
        test.done = true
        console.log("TASKBAR_SERVICE_PROBE " + JSON.stringify({passed:true,accepted:acceptedSnapshots,rejected:rejectedSnapshots,exitReset:true,refresh:true}))
        Qt.quit()
      }
    }
  }
  function fail(message) {
    console.error("TASKBAR_SERVICE_PROBE " + JSON.stringify({passed:false,error:message}))
    Qt.exit(1)
  }
  Timer { interval: 10000; running: true; onTriggered: if (!test.done) test.fail("bounded probe deadline") }
}
