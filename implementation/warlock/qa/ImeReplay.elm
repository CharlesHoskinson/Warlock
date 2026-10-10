port module ImeReplay exposing (main)

import Binding
import Catalog
import Desktop
import NativePointerFixture
import Json.Decode as D
import Json.Encode as E
import Launch
import Platform
import Popup
import Shell
import Surface
import UInt64

port outgoing : E.Value -> Cmd msg

counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
catalog = E.object [("catalogProtocol",E.int 2),("lifetime",E.string "1"),("generation",E.string "1"),("entries",E.list identity [E.object [("id",E.string "editor"),("name",E.string "Editor"),("iconHint",E.string ""),("wmclass",E.string ""),("genericName",E.string "Text editor"),("keywords",E.list E.string [])]])]
base =
    let initial=Desktop.initial
        windows=initial.windows
        shell=windows.shell
        binding=D.decodeValue Binding.decoder (E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]) |> Result.toMaybe
    in NativePointerFixture.ready {initial | open=True,applications=Catalog.decode catalog |> Result.toMaybe,windows={windows | shell={shell | binding=binding,phase=Shell.Ready}},launch=Launch.init |> Launch.bind "ime-fixture" |> Launch.catalog catalog}

frame number query = Surface.packet (counter number) (counter "1") {base | query=query}
event number kind query = E.object [("surfaceProtocol",E.int 2),("surface",E.string "popup"),("publication",E.string number),("lease",E.string "1"),("id",E.string "control:search"),("kind",E.string kind),("query",E.string query)]
edit number kind query model = Popup.update (Popup.Action (event number kind query)) model |> Tuple.first
present number query model = Popup.update (Popup.Present (frame number query)) model |> Tuple.first
composing model = model.composition/=Popup.Idle

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
result =
    let ready=present "1" "" Popup.initial
        started=edit "1" "surface-composition-start" "" ready
        held=edit "1" "surface-preedit" "é" started
        refreshed=present "2" "" held
        equal=present "3" "é" refreshed
        refreshedAgain=present "4" "" equal
        committed=edit "4" "surface-composition-end" "é" refreshedAgain
        finalInput=edit "4" "surface-query" "é" committed
        acknowledged=present "5" "é" finalInput
        cancelled=ready |> edit "1" "surface-composition-start" "" |> edit "1" "surface-preedit" "candidate" |> edit "1" "surface-composition-end" ""
        stale=edit "1" "surface-composition-end" "wrong" refreshedAgain
        closed=Popup.update (Popup.Present (Surface.packet (counter "5") (counter "1") {base | open=False})) refreshedAgain |> Tuple.first
        files=Popup.update (Popup.Present (Surface.packet (counter "5") (counter "1") {base | open=False,filesOpen=True})) refreshedAgain |> Tuple.first
        inputBeforeEnd=edit "4" "surface-query" "é" refreshedAgain
        checks=[("startBlocksBeforeFirstPreedit",composing started)
               ,("preeditNeverMarksQuerySent",held.lastQuery==Nothing && held.pendingQuery==Just "é")
               ,("sameFieldRefreshPreservesPreedit",composing refreshed && refreshed.pendingQuery==Just "é" && refreshed.lastQuery==Nothing)
               ,("MatchingObservationCannotAcknowledgeUnsentPreedit",composing equal && equal.pendingQuery==Just "é")
               ,("commitSetsOneCurrentScopedQuery",not (composing committed) && committed.pendingQuery==Just "é" && committed.lastQuery==Just ("é",counter "4",counter "1"))
               ,("finalInputDoesNotChangeSentQuery",finalInput.lastQuery==committed.lastQuery && finalInput.pendingQuery==committed.pendingQuery)
               ,("nativeAcknowledgementClearsPending",acknowledged.pendingQuery==Nothing)
               ,("cancelClearsPreeditWithoutQuery",cancelled.composition==Popup.Idle && cancelled.pendingQuery==Nothing && cancelled.lastQuery==Nothing)
               ,("oldPublicationCannotCommitComposition",stale.composition==refreshedAgain.composition && stale.pendingQuery==refreshedAgain.pendingQuery && stale.lastQuery==Nothing)
               ,("closeRetiresLocalComposition",closed.composition==Popup.Idle && closed.pendingQuery==Nothing)
               ,("fieldReplacementDoesNotInheritPreedit",files.composition==Popup.Idle && files.pendingQuery==Nothing)
               ,("finalInputBeforeEndRemainsPreedit",composing inputBeforeEnd && inputBeforeEnd.lastQuery==Nothing)]
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) checks)),("frame",frame "1" ""),("refreshFrame",frame "2" ""),("equalFrame",frame "3" "é"),("nextFrame",frame "4" ""),("ackFrame",frame "5" "é"),("closedFrame",Surface.packet (counter "6") (counter "1") {base | open=False}),("filesFrame",Surface.packet (counter "6") (counter "1") {base | open=False,filesOpen=True})]
