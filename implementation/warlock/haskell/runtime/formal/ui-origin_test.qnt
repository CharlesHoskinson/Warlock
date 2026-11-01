// Explicit traces for root to execute; no execution by author.
module ui_origin_test {
 import ui_origin.* from "./ui-origin"
 // Quint 0.33 fail propagates the attempted action's update effect, but a
 // blocked action produces no successor. Assert the pre-state, then finish
 // with the actual refusal; do not shift an unassigned state after fail().
 run privateRequired = init.expect(not(s.privateNet) and not(s.live)).then(start.fail())
 run controllerCommit = init.then(privateReady).then(start).then(issue(Controller)).then(request(validCommit)).then(sendCommit(true)).then(ack(Controller)).expect(s.forwarded == 1 and s.bar.length() == 2 and s.popup.length() == 2 and safety)
 run barAction = init.then(privateReady).then(start).then(issue(Bar)).then(request(validBar)).expect(s.barActions == 1 and s.controller.head() == ViewAction and safety)
 run popupAction = init.then(privateReady).then(start).then(issue(Popup)).then(request(validPopup)).expect(s.popupActions == 1 and s.controller.head() == ViewAction and safety)
 run independentRoles = init.then(privateReady).then(start).then(issue(Controller)).then(issue(Bar)).then(issue(Popup)).then(request(validBar)).then(request(validPopup)).then(request(validCommit)).then(sendCommit(true)).expect(s.barActions == 1 and s.popupActions == 1 and s.forwarded == 1 and safety)
 run topologyRead = init.then(privateReady).then(start).then(producer(Topology, true)).then(request(validRead)).expect(s.topologyReads == 1 and s.nativeReads == 0 and safety)
 run nativeRead = init.then(privateReady).then(start).then(producer(NativeGateway, true)).then(request(validRead)).expect(s.nativeReads == 1 and s.topologyReads == 0 and safety)
 run crossRole = init.then(privateReady).then(start).then(issue(Controller)).then(request({...validCommit, caller: Bar})).expect(s.result == Refused and s.forwarded == 0)
 run simpleGet = init.then(privateReady).then(start).then(producer(Topology, true)).then(request({...validRead, api: false})).expect(s.result == Refused and s.controller.length() == 1)
 run preflight = init.then(privateReady).then(start).then(request({...validRead, method: Options})).expect(s.result == Refused)
 run badPostOrigin = init.then(privateReady).then(start).then(issue(Controller)).then(request({...validCommit, origin: false})).expect(s.result == Refused and s.forwarded == 0)
 run badHeader = init.then(privateReady).then(start).then(issue(Controller)).then(request({...validCommit, api: false})).expect(s.result == Refused)
 run wrongHost = init.then(privateReady).then(start).then(request({...validRead, host: false})).expect(s.result == Refused)
 run wrongPath = init.then(privateReady).then(start).then(request({...validRead, route: Other})).expect(s.result == Refused)
 run unknownProvenance = init.then(privateReady).then(start).then(producer(UnknownSource, true)).expect(s.retired and s.controller.length() == 0)
 run staleBinding = init.then(privateReady).then(start).then(issue(Controller)).then(request({...validCommit, binding: false})).expect(s.result == Refused and s.forwarded == 0)
 run retired = init.then(privateReady).then(start).then(engineReturn(true, false, true)).expect(s.retired and not(s.clean)).then(request(validCommit).fail())
 run retiredStartRefused = init.then(privateReady).then(start).then(engineReturn(true, false, true)).expect(s.retired and not(s.clean)).then(start.fail())
 run cleanEngine = init.then(privateReady).then(start).then(engineReturn(false, true, true)).expect(s.retired and s.clean and not(s.enginePassed))
 run expired = init.then(privateReady).then(start).then(deadline).expect(s.expired and s.forwarded == 0).then(request(validCommit).fail())
 run expiredStartRefused = init.then(privateReady).then(start).then(deadline).expect(s.expired and s.forwarded == 0).then(start.fail())
 run noReplayUnknown = init.then(privateReady).then(start).then(issue(Controller)).then(request(validCommit)).then(sendCommit(true)).then(unknown(Controller)).then(issue(Bar)).expect(s.forwarded == 1 and s.failed.contains(Controller) and s.active.contains(Bar)).then(issue(Controller).fail())
 run queueFull = init.then(privateReady).then(start).then(producer(Topology, true)).then(producer(Topology, true)).then(producer(NativeGateway, true)).then(issue(Bar)).then(request(validBar)).expect(s.result == Full and s.retired and s.barActions == 0)
 run atomicReservationFull = init.then(privateReady).then(start).then(producer(Topology, true)).then(producer(Topology, true)).then(producer(Topology, true)).then(issue(Controller)).then(request(validCommit)).expect(s.result == Full and s.retired and s.bar.length() == 0 and s.popup.length() == 0)
 run sendFailure = init.then(privateReady).then(start).then(issue(Controller)).then(request(validCommit)).then(sendCommit(false)).expect(s.retired and s.forwarded == 0 and s.bar.length() == 2 and s.result == Unknown)
 run staleGateway = init.then(privateReady).then(start).then(producer(NativeGateway, false)).expect(s.retired and s.controller.length() == 0)
 run wrongRoleRoute = init.then(privateReady).then(start).then(issue(Bar)).then(request({...validCommit, listener: Bar, caller: Bar})).expect(s.result == Refused and s.forwarded == 0)
 run malformedPost = init.then(privateReady).then(start).then(issue(Controller)).then(request({...validCommit, wellFormed: false})).expect(s.result == Refused and s.forwarded == 0)
 run noAckReceipt = init.then(privateReady).then(start).then(issue(Bar)).then(ack(Bar)).expect(s.forwarded == 0 and s.controller.length() == 0 and s.bar.length() == 0 and s.popup.length() == 0)
 // Focus rows are included in the same atomic reservation as the base pair.
 run focusReservation = init.then(privateReady).then(start).then(issue(Controller)).then(request({...validCommit, focusBar: true, focusPopup: true})).then(sendCommit(true)).expect(s.bar.length() == 3 and s.popup.length() == 3 and s.forwarded == 1 and safety)
 run focusSaturationAtomic = init.then(privateReady).then(start).then(issue(Controller)).then(request({...validCommit, focusBar: true})).then(sendCommit(true)).then(ack(Controller)).then(issue(Controller)).then(request(validCommit)).expect(s.result == Full and s.retired and s.bar.length() == 3 and s.popup.length() == 2 and s.forwarded == 1 and safety)
 run roleReadIsolation = init.then(privateReady).then(start).then(issue(Controller)).then(request(validCommit)).then(sendCommit(true)).then(request({...validRead, listener: Bar, caller: Bar})).expect(s.bar.length() == 1 and s.popup.length() == 2 and s.controller.length() == 0 and safety)
 run sendUnknownNoReplay = init.then(privateReady).then(start).then(issue(Controller)).then(request(validCommit)).then(sendCommit(false)).expect(s.retired and s.result == Unknown and s.forwarded == 0 and s.bar.length() == 2 and s.popup.length() == 2).then(sendCommit(true).fail())
 run sendUnknownIssueRefused = init.then(privateReady).then(start).then(issue(Controller)).then(request(validCommit)).then(sendCommit(false)).expect(s.retired and s.result == Unknown and s.forwarded == 0 and s.bar.length() == 2 and s.popup.length() == 2).then(issue(Controller).fail())
}
