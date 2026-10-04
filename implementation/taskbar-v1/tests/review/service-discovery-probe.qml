import QtQuick
import Quickshell

// Reproduces host immutable _services replacement through scoped API closure.
// Root launches offscreen through protected QA; no windows are constructed.
ShellRoot {
  id: test
  property var _services: ({})
  property int phase: 0
  property int changes: 0
  function serviceFor(id) { return _services[String(id)] || null }
  QtObject {
    id: api
    property var lookup: function(id) { return test.serviceFor(id) }
    function serviceFor(id) { return lookup(String(id)) }
  }
  QtObject {
    id: consumer
    readonly property var service: api.serviceFor("hoskinson.windows")
    onServiceChanged: test.changes++
  }
  Timer {
    interval: 25; running: true; repeat: true
    onTriggered: {
      if (test.phase === 0) {
        if (consumer.service !== null) test.fail("initial absent service")
        test._services = {"hoskinson.windows": {name:"first"}}
      } else if (test.phase === 1) {
        if (!consumer.service || consumer.service.name !== "first") test.fail("service add not observed through lookup closure")
        test._services = {}
      } else if (test.phase === 2) {
        if (consumer.service !== null) test.fail("service removal not observed")
        test._services = {"hoskinson.windows": {name:"second"}}
      } else {
        if (!consumer.service || consumer.service.name !== "second") test.fail("replacement service not observed")
        console.log("TASKBAR_DISCOVERY_PROBE " + JSON.stringify({passed:true,changes:test.changes}))
        Qt.quit()
      }
      test.phase++
    }
  }
  function fail(message) { console.error("TASKBAR_DISCOVERY_PROBE " + message); Qt.exit(1) }
  Timer { interval: 2000; running: true; onTriggered: test.fail("bounded probe deadline") }
}
