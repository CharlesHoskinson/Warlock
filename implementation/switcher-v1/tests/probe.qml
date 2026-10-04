import QtQuick
import Quickshell
ShellRoot {
 id:root
 property int checks:0
 SwitcherController {id:controller;session:"session"}
 property var request:({mode:"switcher",candidates:[{address:"0x1",pid:1,stableId:"a"},{address:"0x2",pid:2,stableId:"b"}]})
 function check(value,message){if(!value)throw Error(message);checks++}
 Component.onCompleted: {
  try {
   controller.release("session",1,1)
   check(!controller.presentationOpen && controller.pending,"release-before-step pending")
   var lease=JSON.parse(controller.step("session",1,1,1))
   check(lease.builder,"one builder")
   controller.ready(lease.epoch,1,lease.token,JSON.stringify(request))
   check(!controller.presentationOpen && controller.machine.phase==="committed","ready commits without overlay")
   check(JSON.parse(controller.claim(lease.epoch,1,lease.token)).address==="0x2","guarded candidate")
   check(JSON.parse(controller.claim(lease.epoch,1,lease.token))===null,"one-use claim")
   lease=JSON.parse(controller.step("session",2,1,-1))
   controller.ready(lease.epoch,2,lease.token,JSON.stringify(request))
   check(controller.presentationOpen,"live chord visible")
   controller.cancel()
   controller.release("session",2,1)
   check(!controller.presentationOpen && controller.machine.phase==="cancelled","cancel survives delayed release")
   controller.ready(lease.epoch,2,lease.token,JSON.stringify(request))
   check(!controller.presentationOpen,"stale ready cannot reopen")
   lease=JSON.parse(controller.step("session",3,1,1))
   controller.ready(lease.epoch,3,lease.token,JSON.stringify(request))
   controller.choose(0)
   controller.release("session",3,1)
   check(JSON.parse(controller.claim(lease.epoch,3,lease.token)).address==="0x1","arrow selection enters reducer")
   lease=JSON.parse(controller.step("session",4,1,1))
   controller.barrier("session",5)
   controller.ready(lease.epoch,4,lease.token,JSON.stringify(request))
   check(!controller.presentationOpen && controller.machine.generation===5,"reload barrier closes stale builder")
   console.log("SWITCHER_QML_PASS "+checks)
   Qt.quit()
  } catch(error) {console.error("SWITCHER_QML_FAIL "+error);Qt.exit(1)}
 }
}
