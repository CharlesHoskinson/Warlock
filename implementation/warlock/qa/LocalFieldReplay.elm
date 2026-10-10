port module LocalFieldReplay exposing (main)

import Desktop
import Json.Decode as D
import Json.Encode as E
import Platform
import Popup
import Presentation
import Surface
import UInt64

port outgoing : E.Value -> Cmd msg
counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
frame pub lease files = Surface.packet (counter pub) (counter lease) {base | open=not files,filesOpen=files}
base = Desktop.initial
event pub lease kind field value = E.object [("surfaceProtocol",E.int 2),("surface",E.string "popup"),("publication",E.string pub),("lease",E.string lease),("kind",E.string kind),("id",E.string field),("query",E.string value)]
present pub lease files model = Popup.update (Popup.Present (frame pub lease files)) model |> Tuple.first
local pub lease kind field value model = Popup.update (Popup.LocalAction (event pub lease kind field value)) model |> Tuple.first
external pub lease kind field value model = Popup.update (Popup.Action (event pub lease kind field value)) model |> Tuple.first
sameDraft left right = left.pendingQuery==right.pendingQuery && left.lastQuery==right.lastQuery && left.composition==right.composition
result =
    let initial=present "1" "1" False Popup.initial
        advanced=present "2" "1" False initial
        edited=local "1" "1" "surface-query" "control:search" "edi" advanced
        continued=local "1" "1" "surface-query" "control:search" "editor" edited
        refreshed=present "3" "1" False continued
        acknowledged=Popup.update (Popup.Present (Surface.packet (counter "4") (counter "1") {base | open=True,query="editor"})) refreshed |> Tuple.first
        reopened=present "3" "2" False edited
        files=present "3" "1" True edited
        composition=advanced |> local "1" "1" "surface-composition-start" "control:search" "" |> local "1" "1" "surface-preedit" "control:search" "é"
        committed=local "1" "1" "surface-composition-end" "control:search" "é" composition
        checks=[("localPaintGapPreservesDraft",edited.pendingQuery==Just "edi" && edited.lastQuery==Just ("edi",counter "2",counter "1"))
               ,("localFifoKeepsLatestValue",continued.pendingQuery==Just "editor")
               ,("refreshPreservesUnacknowledgedDraft",refreshed.pendingQuery==Just "editor" && refreshed.lastQuery==Just ("editor",counter "3",counter "1"))
               ,("matchingObservationAcknowledgesDraft",acknowledged.pendingQuery==Nothing)
               ,("staleExternalQueryStillRejected",sameDraft advanced (external "1" "1" "surface-query" "control:search" "wrong" advanced))
               ,("futureLocalQueryRejected",sameDraft advanced (local "3" "1" "surface-query" "control:search" "wrong" advanced))
               ,("zeroPublicationRejected",sameDraft advanced (local "0" "1" "surface-query" "control:search" "wrong" advanced))
               ,("oldLeaseLocalQueryRejected",sameDraft reopened (local "1" "1" "surface-query" "control:search" "wrong" reopened))
               ,("newLeaseRetiresPriorDraft",reopened.pendingQuery==Nothing && reopened.lastQuery==Nothing && reopened.composition==Popup.Idle)
               ,("replacedFieldRejectsOldLocalQuery",sameDraft files (local "1" "1" "surface-query" "control:search" "wrong" files))
               ,("boundedLocalQueryRejected",sameDraft advanced (local "1" "1" "surface-query" "control:search" (String.repeat 257 "x") advanced))
               ,("sameLeaseLocalPreeditHeld",composition.composition/=Popup.Idle && composition.pendingQuery==Just "é" && composition.lastQuery==Nothing)
               ,("sameLeaseLocalCommitUsesCurrentScope",committed.composition==Popup.Idle && committed.lastQuery==Just ("é",counter "2",counter "1"))
               ,("staleExternalCompositionStillRejected",sameDraft composition (external "1" "1" "surface-composition-end" "control:search" "wrong" composition))
               ,("staleButtonStillRejected",Presentation.dispatch True (E.object [("surfaceProtocol",E.int 2),("surface",E.string "popup"),("publication",E.string "1"),("lease",E.string "1"),("id",E.string "control:close"),("kind",E.string "surface-action")]) advanced.presentation==Nothing)]
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) checks))]
main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
