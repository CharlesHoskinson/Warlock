module uiNativeStreamTest {
  import uiNativeStream.* from "./ui-native-stream"
  run catalogTest = init.then(offer(frame(Catalog, Empty))).then(callback).then(dispatch).then(dispatch).expect(catalogWitness and safety)
  run pinsSavedTest = init.then(offer(frame(Pins, Empty))).then(callback).then(dispatch).then(complete(Saved)).then(dispatch).expect(pinsWitness and safety)
  run emptyCommitTest = init.then(offer(frame(Empty, Empty))).then(callback).then(dispatch).then(dispatch).expect(emptyWitness and safety)
  run refusedPinTest = init.then(offer(frame(Pins, Empty))).then(callback).then(dispatch).then(complete(Refused)).then(dispatch).expect(refusalWitness and s.durable == 0 and safety)
  run unknownNoReplayTest = init.then(offer(frame(Pins, Empty))).then(callback).then(dispatch).then(complete(Unknown)).then(dispatch).then(reset).then(offer(frame(Pins, Empty))).then(callback).then(dispatch).then(dispatch).expect(unknownWitness and s.writes == 1 and s.durable == 0 and safety)
  run wholeBadBatchTest = init.then(offer(frame(Catalog, UnknownMethod))).expect(badBatchWitness and safety)
  run pathSelectorTest = init.then(offer(frame(PathSelector, Empty))).expect(s.rejected == 1 and s.callbacks == 0 and s.writes == 0)
  run badBindingTest = init.then(offer({ ...frame(Catalog, Empty), second: { ...request(Pins), binding: 2 } })).expect(s.rejected == 1 and s.callbacks == 0)
  run kernelSessionTest = init.then(offer({ ...frame(Catalog, Empty), kernel: false })).then(offer({ ...frame(Catalog, Empty), session: false })).expect(s.rejected == 2 and s.callbacks == 0)
  run schemaVersionTest = init.then(offer({ ...frame(Catalog, Empty), version: 2 })).then(offer({ ...frame(Catalog, Empty), first: { ...request(Catalog), schema: false } })).expect(s.rejected == 2 and s.callbacks == 0)
  run boundaryTest = init.expect(validDesktop({ ...frame(Catalog, Empty), bytes: 131072, first: { ...request(Catalog), bytes: 8192 } }) and not(validDesktop({ ...frame(Catalog, Empty), bytes: 131073 })) and not(validDesktop({ ...frame(Catalog, Empty), first: { ...request(Catalog), bytes: 8193 } })))
  run legacyTest = init.expect(validLegacy(65536, 1, true, true, true) and validLegacy(65536, 2, true, true, true) and not(validLegacy(65537, 1, true, true, true)) and not(validLegacy(1, 3, true, true, true))).then(offer({ ...frame(Catalog, Empty), bytes: 65537 })).expect(s.phase == "checked")
  run trustedNativeProfileTest = initNative.then(offer(frame(Catalog, Empty))).expect(s.profile == Native and s.rejected == 1 and s.callbacks == 0)
  run forgedGatewayTest = init.expect(validGateway(1048704, 1048576, true, 1, "native-event", 3, 1, true) and not(validGateway(1048705, 1048576, true, 1, "native-event", 3, 1, true)) and not(validGateway(1, 1, true, 1, "native-event", 3, 1, false)) and not(validGateway(1, 1, true, 1, "server", 3, 1, true)) and not(validGateway(1, 1, true, 2, "native-event", 3, 1, true)) and not(validGateway(1, 1, true, 1, "native-event", 3, 2, true)))
}
