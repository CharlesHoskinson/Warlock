port module LocalFieldReplay exposing (main)

import Desktop
import Json.Decode as D
import Json.Encode as E
import Platform
import Popup
import Presentation
import Surface
import SurfaceSnapshot
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
buttonEvent pub lease identity = E.object [("surfaceProtocol",E.int 2),("surface",E.string "popup"),("publication",E.string pub),("lease",E.string lease),("kind",E.string "surface-action"),("id",E.string identity)]
controlRow identity dom label = E.object [("id",E.string identity),("domId",E.string dom),("label",E.string label),("ariaLabel",E.string label),("detail",E.string ""),("enabled",E.bool True)]
richFrame pub lease queryValue =
    E.object
        [ ("surfaceProtocol",E.int 2)
        , ("publication",E.string pub)
        , ("lease",E.string lease)
        , ("mode",E.string "applications")
        , ("status",E.string "Type to search applications.")
        , ("bar",E.list identity [controlRow "bar:applications" "open-applications" "Applications"])
        , ("popup",E.list identity
            [ controlRow "control:search" "search-applications" queryValue
            , controlRow "control:close" "close-applications" "Windows"
            , controlRow "control:refresh" "refresh-applications" "Refresh"
            , controlRow "control:acknowledge" "ack-launch" "I checked; allow another launch"
            , controlRow "jump:open:org.gnome.TextEditor" "jump-editor" "Actions"
            , controlRow "pin:org.gnome.TextEditor" "pin-editor" "Pin"
            , controlRow "unpin:org.mozilla.firefox" "unpin-firefox" "Unpin"
            , controlRow "pin-left:org.mozilla.firefox" "left-firefox" "Move earlier"
            , controlRow "pin-right:org.mozilla.firefox" "right-firefox" "Move later"
            , controlRow "entry:org.gnome.TextEditor" "entry-editor" "Text Editor"
            , controlRow "control:page-previous" "page-prev" "Previous page"
            , controlRow "control:page-next" "page-next" "Next page"
            ])
        ]
hasQuery pub lease value effects =
    let dispatches = List.filterMap (\effect -> case effect of
            Popup.Dispatch wire -> Just wire
            _ -> Nothing) effects
        exact wire =
            (D.decodeValue (D.keyValuePairs D.value) wire |> Result.map (List.map Tuple.first >> List.sort)) == Ok (List.sort ["surfaceProtocol","kind","surface","publication","lease","id","query"])
                && D.decodeValue (D.field "surfaceProtocol" D.int) wire == Ok 2
                && D.decodeValue (D.field "kind" D.string) wire == Ok "surface-query"
                && D.decodeValue (D.field "surface" D.string) wire == Ok "popup"
                && D.decodeValue (D.field "id" D.string) wire == Ok "control:search"
                && D.decodeValue (D.map3 (\p l q -> (p,l,q)) (D.field "publication" D.string) (D.field "lease" D.string) (D.field "query" D.string)) wire == Ok (pub,lease,value)
    in case dispatches of
        [wire] -> exact wire
        _ -> False
hasNoDispatch effects =
    List.all (\effect -> case effect of
        Popup.Dispatch _ -> False
        _ -> True) effects
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
        blockedIds=["entry:org.gnome.TextEditor","pin:org.gnome.TextEditor","unpin:org.mozilla.firefox","pin-left:org.mozilla.firefox","pin-right:org.mozilla.firefox","jump:open:org.gnome.TextEditor","control:page-previous","control:page-next"]
        safeIds=["control:close","control:refresh","control:acknowledge"]
        richInitial=Popup.update (Popup.Present (richFrame "1" "7" "")) Popup.initial |> Tuple.first
        -- The first query may still be in flight when the user returns to
        -- the currently rendered value. The later first result must not
        -- erase that newest local intent.
        (reversionFirst,reversionFirstEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-query" "control:search" "f")) richInitial
        (reversionLatest,reversionLatestEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-query" "control:search" "")) reversionFirst
        (reversionDelayed,reversionRetryEffects)=Popup.transition (Popup.Present (richFrame "2" "7" "f")) reversionLatest
        (reversionDone,reversionDoneEffects)=Popup.transition (Popup.Present (richFrame "3" "7" "")) reversionDelayed
        -- A matching old value in an unrelated newer publication cannot
        -- establish that the earlier request has retired.
        (unrelatedEarlier,unrelatedEffects)=Popup.transition (Popup.Present (richFrame "2" "7" "")) reversionFirst
        (unrelatedReverse,unrelatedReverseEffects)=Popup.transition (Popup.LocalAction (event "2" "7" "surface-query" "control:search" "")) unrelatedEarlier
        (unrelatedDelayed,unrelatedRetryEffects)=Popup.transition (Popup.Present (richFrame "3" "7" "f")) unrelatedReverse
        -- The intermediate edit is scoped to the old publication; when an
        -- earlier edit advances publication during preedit, composition end
        -- matching that new authority needs no redundant query dispatch.
        (reversionRepeat,reversionRepeatEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-query" "control:search" "")) reversionLatest
        (preeditFirst,preeditFirstEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-query" "control:search" "c")) richInitial
        (preeditSecond,preeditSecondEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-query" "control:search" "b")) preeditFirst
        preeditStarted=local "1" "7" "surface-composition-start" "control:search" "b" preeditSecond
        preeditChanged=local "1" "7" "surface-preedit" "control:search" "c" preeditStarted
        (preeditAdvanced,preeditAdvancedEffects)=Popup.transition (Popup.Present (richFrame "2" "7" "c")) preeditChanged
        (preeditEnded,preeditEndEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-composition-end" "control:search" "c")) preeditAdvanced
        -- Cancellation must restore a pre-composition local intent without
        -- duplicating an outstanding request in the same publication.
        (cancelSameStart,cancelSameStartEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-composition-start" "control:search" "")) reversionLatest
        (cancelSamePreedit,cancelSamePreeditEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-preedit" "control:search" "x")) cancelSameStart
        (cancelSameEnd,cancelSameEndEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-composition-end" "control:search" "")) cancelSamePreedit
        (cancelSameLater,cancelSameLaterEffects)=Popup.transition (Popup.Present (richFrame "2" "7" "f")) cancelSameEnd
        (cancelSameSettled,cancelSameSettledEffects)=Popup.transition (Popup.Present (richFrame "3" "7" "")) cancelSameLater
        -- The earlier a/P1 can advance the authority while b/P1 is pending.
        (cancelAheadA,cancelAheadAEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-query" "control:search" "a")) richInitial
        (cancelAheadB,cancelAheadBEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-query" "control:search" "b")) cancelAheadA
        (cancelAheadStart,cancelAheadStartEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-composition-start" "control:search" "b")) cancelAheadB
        (cancelAheadPreedit,cancelAheadPreeditEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-preedit" "control:search" "bx")) cancelAheadStart
        (cancelAheadFrame,cancelAheadFrameEffects)=Popup.transition (Popup.Present (richFrame "2" "7" "a")) cancelAheadPreedit
        (cancelAheadEnd,cancelAheadEndEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-composition-end" "control:search" "b")) cancelAheadFrame
        (cancelAheadSettled,cancelAheadSettledEffects)=Popup.transition (Popup.Present (richFrame "3" "7" "b")) cancelAheadEnd
        -- A same-lease stale DOM can start composition at a baseline that
        -- differs from the retained b intent. Cancellation must send b,
        -- not the composition-end value a, under the current publication.
        (cancelDifferentStart,cancelDifferentStartEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-composition-start" "control:search" "a")) cancelAheadB
        (cancelDifferentPreedit,cancelDifferentPreeditEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-preedit" "control:search" "ax")) cancelDifferentStart
        (cancelDifferentFrame,cancelDifferentFrameEffects)=Popup.transition (Popup.Present (richFrame "2" "7" "a")) cancelDifferentPreedit
        (cancelDifferentEnd,cancelDifferentEndEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-composition-end" "control:search" "a")) cancelDifferentFrame
        (cancelDifferentSettled,cancelDifferentSettledEffects)=Popup.transition (Popup.Present (richFrame "3" "7" "b")) cancelDifferentEnd
        -- With no prior local request, cancel reveals the current authority.
        -- The new publication here is a directed external presentation.
        (cancelCleanStart,cancelCleanStartEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-composition-start" "control:search" "")) richInitial
        (cancelCleanPreedit,cancelCleanPreeditEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-preedit" "control:search" "x")) cancelCleanStart
        (cancelCleanFrame,cancelCleanFrameEffects)=Popup.transition (Popup.Present (richFrame "2" "7" "a")) cancelCleanPreedit
        (cancelCleanEnd,cancelCleanEndEffects)=Popup.transition (Popup.LocalAction (event "1" "7" "surface-composition-end" "control:search" "")) cancelCleanFrame
        richPending=local "1" "7" "surface-query" "control:search" "foot" richInitial
        richComposing=richPending |> local "1" "7" "surface-composition-start" "control:search" "foot" |> local "1" "7" "surface-preedit" "control:search" "foot漢"
        decodedRich=SurfaceSnapshot.decode (richFrame "1" "7" "") |> Result.toMaybe
        checks=[("reversionFirstQueryActuallyDispatched",hasQuery "1" "7" "f" reversionFirstEffects && reversionFirst.pendingQuery==Just "f")
               ,("reversionToPublishedValueRetainsLatestIntent",reversionLatest.pendingQuery==Just "" && hasQuery "1" "7" "" reversionLatestEffects)
               ,("reversionSurvivesDelayedEarlierResult",reversionDelayed.pendingQuery==Just "" && hasQuery "2" "7" "" reversionRetryEffects)
               ,("reversionMatchingLatestValueIsVisible",(Presentation.current reversionDone.presentation |> Maybe.andThen SurfaceSnapshot.queryValue)==Just "" && reversionDone.pendingQuery==Nothing && hasNoDispatch reversionDoneEffects)
               ,("unrelatedOldValueKeepsFirstPending",unrelatedEarlier.pendingQuery==Just "f" && hasQuery "2" "7" "f" unrelatedEffects)
               ,("reversionAfterUnrelatedPublicationRetainsIntent",unrelatedReverse.pendingQuery==Just "" && hasQuery "2" "7" "" unrelatedReverseEffects)
               ,("lateFirstAfterUnrelatedPublicationStillRetriesLatest",unrelatedDelayed.pendingQuery==Just "" && hasQuery "3" "7" "" unrelatedRetryEffects)
               ,("repeatedReversionRetainsPendingWithoutDispatch",reversionRepeat.pendingQuery==Just "" && reversionRepeat.lastQuery==Just ("",counter "1",counter "7") && List.isEmpty reversionRepeatEffects)
               ,("preeditAdvanceFirstTwoEditsDispatched",List.length preeditFirstEffects==1 && hasQuery "1" "7" "c" preeditFirstEffects && List.length preeditSecondEffects==1 && hasQuery "1" "7" "b" preeditSecondEffects)
               ,("preeditAdvanceHoldsDraft",preeditAdvanced.composition/=Popup.Idle && preeditAdvanced.pendingQuery==Just "c" && List.length preeditAdvancedEffects==2 && hasNoDispatch preeditAdvancedEffects)
               ,("preeditEndMatchingAdvancedPublicationSettles",preeditEnded.composition==Popup.Idle && preeditEnded.pendingQuery==Nothing && List.isEmpty preeditEndEffects && (Presentation.current preeditEnded.presentation |> Maybe.andThen SurfaceSnapshot.queryValue)==Just "c")
               ,("cancelSameScopeSetupAndPreedit",reversionLatest.pendingQuery==Just "" && reversionLatest.lastQuery==Just ("",counter "1",counter "7") && hasQuery "1" "7" "" reversionLatestEffects && cancelSameStart.composition/=Popup.Idle && cancelSamePreedit.composition/=Popup.Idle && cancelSamePreedit.pendingQuery==Just "x" && List.isEmpty cancelSameStartEffects && List.isEmpty cancelSamePreeditEffects)
               ,("cancelSameScopeRetainsPendingWithoutReplay",cancelSameEnd.composition==Popup.Idle && cancelSameEnd.pendingQuery==Just "" && cancelSameEnd.lastQuery==Just ("",counter "1",counter "7") && List.isEmpty cancelSameEndEffects)
               ,("cancelSameScopeLaterOldResultRebases",cancelSameLater.pendingQuery==Just "" && cancelSameLater.lastQuery==Just ("",counter "2",counter "7") && List.length cancelSameLaterEffects==3 && hasQuery "2" "7" "" cancelSameLaterEffects)
               ,("cancelSameScopeLatestProjectionSettles",cancelSameSettled.pendingQuery==Nothing && (Presentation.current cancelSameSettled.presentation |> Maybe.andThen SurfaceSnapshot.queryValue)==Just "" && List.length cancelSameSettledEffects==2 && hasNoDispatch cancelSameSettledEffects)
               ,("cancelAdvancedSetupHasTwoExactRequests",List.length cancelAheadAEffects==1 && hasQuery "1" "7" "a" cancelAheadAEffects && List.length cancelAheadBEffects==1 && hasQuery "1" "7" "b" cancelAheadBEffects && List.isEmpty cancelAheadStartEffects && List.isEmpty cancelAheadPreeditEffects)
               ,("cancelAdvancedPresentationHoldsPreedit",cancelAheadFrame.composition/=Popup.Idle && cancelAheadFrame.pendingQuery==Just "bx" && List.length cancelAheadFrameEffects==2 && hasNoDispatch cancelAheadFrameEffects)
               ,("cancelAdvancedRestoresAndRebasesPriorIntent",cancelAheadEnd.composition==Popup.Idle && cancelAheadEnd.pendingQuery==Just "b" && cancelAheadEnd.lastQuery==Just ("b",counter "2",counter "7") && List.length cancelAheadEndEffects==1 && hasQuery "2" "7" "b" cancelAheadEndEffects)
               ,("cancelAdvancedMatchingProjectionSettles",cancelAheadSettled.pendingQuery==Nothing && (Presentation.current cancelAheadSettled.presentation |> Maybe.andThen SurfaceSnapshot.queryValue)==Just "b" && List.length cancelAheadSettledEffects==2 && hasNoDispatch cancelAheadSettledEffects)
               ,("cancelDifferentBaselineSetupHoldsPriorIntent",cancelAheadB.pendingQuery==Just "b" && cancelDifferentStart.composition/=Popup.Idle && cancelDifferentPreedit.pendingQuery==Just "ax" && List.isEmpty cancelDifferentStartEffects && List.isEmpty cancelDifferentPreeditEffects && cancelDifferentFrame.composition/=Popup.Idle && List.length cancelDifferentFrameEffects==2 && hasNoDispatch cancelDifferentFrameEffects)
               ,("cancelDifferentBaselineDispatchesRetainedIntent",cancelDifferentEnd.composition==Popup.Idle && cancelDifferentEnd.pendingQuery==Just "b" && cancelDifferentEnd.lastQuery==Just ("b",counter "2",counter "7") && List.length cancelDifferentEndEffects==1 && hasQuery "2" "7" "b" cancelDifferentEndEffects)
               ,("cancelDifferentBaselineMatchingProjectionSettles",cancelDifferentSettled.pendingQuery==Nothing && (Presentation.current cancelDifferentSettled.presentation |> Maybe.andThen SurfaceSnapshot.queryValue)==Just "b" && List.length cancelDifferentSettledEffects==2 && hasNoDispatch cancelDifferentSettledEffects)
               ,("cancelWithoutPriorPendingRevealsNewAuthority",List.isEmpty cancelCleanStartEffects && List.isEmpty cancelCleanPreeditEffects && cancelCleanFrame.composition/=Popup.Idle && List.length cancelCleanFrameEffects==2 && hasNoDispatch cancelCleanFrameEffects && cancelCleanEnd.composition==Popup.Idle && cancelCleanEnd.pendingQuery==Nothing && cancelCleanEnd.lastQuery==Nothing && (Presentation.current cancelCleanEnd.presentation |> Maybe.andThen SurfaceSnapshot.queryValue)==Just "a" && List.isEmpty cancelCleanEndEffects)
               ,("localPaintGapPreservesDraft",edited.pendingQuery==Just "edi" && edited.lastQuery==Just ("edi",counter "2",counter "1"))
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
               ,("staleButtonStillRejected",Presentation.dispatch True (E.object [("surfaceProtocol",E.int 2),("surface",E.string "popup"),("publication",E.string "1"),("lease",E.string "1"),("id",E.string "control:close"),("kind",E.string "surface-action")]) advanced.presentation==Nothing)
               ,("pendingBlocksPinJumpUnpinAndPagingTransitions",List.all (\identity -> (Popup.transition (Popup.LocalAction (buttonEvent "1" "7" identity)) richPending |> Tuple.second)==[]) blockedIds)
               ,("pendingAllowsSafeEscapeAndRefreshTransitions",List.all (\identity -> List.length (Popup.transition (Popup.LocalAction (buttonEvent "1" "7" identity)) richPending |> Tuple.second)==1) safeIds)
               ,("composingBlocksAllNonFieldButtonsInTransition",List.all (\identity -> (Popup.transition (Popup.LocalAction (buttonEvent "1" "7" identity)) richComposing |> Tuple.second)==[]) (blockedIds++safeIds))
               ,("honestOverlayDisablesExactBlockedSet",decodedRich |> Maybe.map (\snap -> let overlaid = SurfaceSnapshot.honestPendingQuery "foot" snap in SurfaceSnapshot.queryValue overlaid==Just "foot" && List.all (\identity -> not (SurfaceSnapshot.enabled True identity overlaid) && SurfaceSnapshot.action True identity overlaid==Nothing) blockedIds && List.all (\identity -> SurfaceSnapshot.enabled True identity overlaid) safeIds) |> Maybe.withDefault False)
               ,("composingOverlayDisablesEveryNonFieldControl",decodedRich |> Maybe.map (\snap -> let overlaid = SurfaceSnapshot.composingPopup snap in SurfaceSnapshot.enabled True "control:search" overlaid && List.all (\identity -> not (SurfaceSnapshot.enabled True identity overlaid) && SurfaceSnapshot.action True identity overlaid==Nothing) (blockedIds++safeIds)) |> Maybe.withDefault False)]
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) checks))]
main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
