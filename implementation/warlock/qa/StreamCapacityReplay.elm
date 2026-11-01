port module StreamCapacityReplay exposing (main)

{-| Actual owning renderer/controller pin proposals plus adversarial registration
inputs. Native frames below are explicit bridge fixtures, never native evidence.
Injected duplicate requests and oversized focus strings exercise the transport
boundary; they are not represented as normal Desktop-generated user actions.
-}

import Desktop
import Json.Decode as D
import Json.Encode as E
import OutputController as Outputs
import Pins
import Platform
import Shell
import SurfaceController as Controller
import SurfaceSnapshot
import UInt64

port outgoing : E.Value -> Cmd msg

counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
advance count value = List.range 1 count |> List.foldl (\_ current -> UInt64.next current |> Maybe.withDefault current) (counter value) |> UInt64.string
ids seed =
    { life=advance seed "9007199254741001",session=advance seed "9007199254742001"
    , epoch=advance seed "9007199254743001",output=advance seed "9007199254744001"
    , revision=advance seed "9007199254745001",pinsRevision=advance seed "9007199254746001"
    , foreign=advance seed "9007199254749001"
    , items=List.range 0 (1+modBy 7 seed) |> List.map (\index -> "capacity-"++String.fromInt seed++"-"++String.fromInt index++".desktop")
    }
binding i = E.object [("lifetime",E.string i.life),("session",E.string i.session),("frontend",E.string i.epoch)]
native kind fields = E.object ([("protocolVersion",E.int 3),("kind",E.string kind)]++fields)
field name raw = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
textField name raw = D.decodeValue (D.field name D.string) raw |> Result.withDefault ""
replace name value raw = D.decodeValue (D.keyValuePairs D.value) raw |> Result.map (\pairs -> E.object ((name,value)::List.filter (Tuple.first >> (/=) name) pairs)) |> Result.withDefault raw
scope = E.object [("id",E.string "1"),("generation",E.string "1")]
topology = E.object [("viewProtocol",E.int 2),("kind",E.string "view-topology"),("revision",E.string "1"),("views",E.list identity [scope]),("locations",E.list identity [E.object [("scope",scope),("box",E.list E.int [0,0,800,600])]])]
desktop model = Controller.desktop (Outputs.controller model)
frame model = Controller.frame (Outputs.controller model)
step event model =
    let (next,effects)=Outputs.update event model
        (registered,packet)=Outputs.register effects next
    in {model=registered,effects=effects,packet=packet}
receive raw model = step (Outputs.Interaction (Desktop.Incoming raw)) model
expected model = (desktop model).expected |> Maybe.map UInt64.string |> Maybe.withDefault "0"
requestWire kind effects = List.filterMap (\effect -> case effect of
    Controller.DesktopEffect (Desktop.Send raw) -> if textField "kind" raw==kind then Just raw else Nothing
    _ -> Nothing) effects |> List.head |> Maybe.withDefault E.null
renderer popup control model =
    SurfaceSnapshot.decode (frame model) |> Result.toMaybe |> Maybe.andThen (SurfaceSnapshot.action popup control)
        |> Maybe.map (\action -> E.object [("viewProtocol",E.int 1),("kind",E.string "view-action"),("scope",scope),("action",action)])
        |> Maybe.withDefault E.null
perform popup control model = step (Outputs.Renderer (renderer popup control model)) model

-- Follow only currently published Next-page actions. No topology, binding,
-- receipt or disposition is synthesized to recover from a local refusal.
seekPublished remaining control current =
    if renderer True control current/=E.null || remaining<=0 then
        {model=current,trace=[]}
    else
        let action=renderer True "control:page-next" current
            next=step (Outputs.Renderer action) current
            found=seekPublished (remaining-1) control next.model
        in {model=found.model,trace=E.object [("action",action),("commit",next.packet |> Maybe.withDefault E.null)]::found.trace}
preferences i = E.object [("revision",E.string i.pinsRevision),("identities",E.list E.string i.items)]
catalog i = E.object [("catalogProtocol",E.int 2),("lifetime",E.string i.life),("generation",E.string i.revision),("entries",E.list (\item -> E.object [("id",E.string item),("name",E.string item),("iconHint",E.string ""),("wmclass",E.string ""),("genericName",E.string ""),("keywords",E.list E.string [])]) i.items)]
setup i =
    let located=step (Outputs.Topology topology) Outputs.initial
        attachedRaw=native "attached" [("binding",binding i)]
        attached=receive attachedRaw located.model
        projectionRaw=native "action-projection" [("binding",binding i),("requestId",E.string ((desktop attached.model).windows.shell.expected |> Maybe.map UInt64.string |> Maybe.withDefault "0")),("context",E.object [("lifetime",E.string i.life),("epoch",E.string i.epoch),("output",E.string i.output),("revision",E.string i.revision)]),("scene",E.object [("revision",E.string i.revision),("focused",E.null),("windows",E.list identity [])])]
        projected=receive projectionRaw attached.model
        pointerRaw=native "pointer-ownership" [("ownershipProtocol",E.int 1),("binding",binding i),("requestId",E.string "1"),("serial",E.string "1"),("state",E.string "idle"),("owner",E.null)]
        pointed=receive pointerRaw projected.model
        opened=perform False "bar:applications" pointed.model
        catalogRaw=native "application-catalog" [("binding",binding i),("requestId",E.string (expected opened.model)),("snapshot",catalog i),("preferences",preferences i)]
        ready=receive catalogRaw opened.model
    in {model=ready.model,trace=E.object [("topology",topology),("attached",attachedRaw),("projection",projectionRaw),("pointer",pointerRaw),("openCommit",opened.packet |> Maybe.withDefault E.null),("catalog",catalogRaw)]}

bytes text = String.foldl (\character total -> let code=Char.toCode character in total+(if code<128 then 1 else if code<2048 then 2 else if code<65536 then 3 else 4)) 0 text
packetValue (_,packet) = packet |> Maybe.withDefault E.null
packetRequests result = D.decodeValue (D.field "requests" (D.list D.value)) (packetValue result) |> Result.withDefault []
packetBounded result =
    case Tuple.second result of
        Nothing -> False
        Just packet -> let wire=E.encode 0 packet in bytes wire<=131072 && String.length wire<=131072
compact result = (desktop (Tuple.first result)).presentationCapacity && packetBounded result && String.contains "Compact presentation" (E.encode 0 (packetValue result))
noRequests result = Tuple.second result/=Nothing && List.isEmpty (packetRequests result)
pinState model =
    let pins=(desktop model).pins
    in E.object [("snapshot",pins.snapshot |> Maybe.map Pins.encode |> Maybe.withDefault E.null),("pending",pins.pending |> Maybe.map (\pending -> E.object [("request",E.string (UInt64.string pending.request)),("identities",E.list E.string pending.identities)]) |> Maybe.withDefault E.null),("notice",E.string pins.notice)]
resultTrace name before result = E.object [("name",E.string name),("beforePins",pinState before),("afterPins",pinState (Tuple.first result)),("beforeBatches",E.int (Outputs.pendingBatches before)),("afterBatches",E.int (Outputs.pendingBatches (Tuple.first result))),("commit",packetValue result)]

pipeline seed =
    let i=ids seed
        fixture=setup i
        target=List.drop 1 i.items |> List.head |> Maybe.withDefault ""
        moveAction=renderer True ("pin-left:"++target) fixture.model
        (pending,moveEffects)=Outputs.update (Outputs.Renderer moveAction) fixture.model
        wire=requestWire "taskbar-pins-write" moveEffects
        send raw=Controller.DesktopEffect (Desktop.Send raw)
        rejected=Outputs.register (List.repeat 17 (send wire)) pending
        admitted=Outputs.register (List.repeat 16 (send wire)) pending
        registered=Outputs.register moveEffects pending
        unknownRaw=native "taskbar-pins-outcome" [("binding",binding i),("requestId",field "requestId" wire),("status",E.string "Unknown"),("preferences",E.null)]
        unknown=receive unknownRaw (Tuple.first registered)
        unknownRejected=Outputs.register (List.repeat 17 (send wire)) unknown.model
        recoveryAction=renderer True "control:refresh" unknown.model
        recovery=step (Outputs.Renderer recoveryAction) unknown.model
        recoveryWire=requestWire "catalog-request" recovery.effects
        recoveryRejected=Outputs.register (List.repeat 17 (send wire)) recovery.model
        recoveryMarker=case ((desktop unknown.model).pins.pending,(desktop recovery.model).pins.pending) of
            (Just prior,Just later) ->
                prior.request==later.request && prior.identities==later.identities
                    && prior.confirmation/=later.confirmation
                    && UInt64.compare (counter (textField "requestId" recoveryWire)) prior.request==GT
            _ -> False
        recoveryReached=textField "kind" recoveryWire=="catalog-request"
            && field "binding" recoveryWire==binding i
            && textField "requestId" recoveryWire==expected recovery.model
            && recoveryMarker
            && (desktop recovery.model).pins.snapshot==(desktop unknown.model).pins.snapshot
            && (desktop recovery.model).pins.notice==(desktop unknown.model).pins.notice
        recoveryPreserved=recoveryReached && (desktop (Tuple.first recoveryRejected)).pins==(desktop recovery.model).pins
        foreignWire=replace "binding" (replace "session" (E.string i.foreign) (field "binding" wire)) wire
        foreignRejected=Outputs.register (List.repeat 17 (send foreignWire)) pending
        requestRejected=Outputs.register (List.repeat 17 (send (replace "requestId" (E.string i.foreign) wire))) pending
        retryPage=seekPublished 12 ("pin-left:"++target) (Tuple.first rejected)
        retryAction=renderer True ("pin-left:"++target) retryPage.model
        (retryPending,retryEffects)=Outputs.update (Outputs.Renderer retryAction) retryPage.model
        retryWire=requestWire "taskbar-pins-write" retryEffects
        retryRegistered=Outputs.register retryEffects retryPending
        retryReachable=retryAction/=E.null && textField "kind" retryWire=="taskbar-pins-write"
            && field "binding" retryWire==binding i
            && UInt64.compare (counter (textField "requestId" retryWire)) (counter (textField "requestId" wire))==GT
        retryAdmitted=retryReachable && (desktop retryPending).pins.pending/=Nothing
            && (desktop (Tuple.first retryRegistered)).pins==(desktop retryPending).pins
            && List.length (packetRequests retryRegistered)==1
            && List.member retryWire (packetRequests retryRegistered)
            && not (List.member wire (packetRequests retryRegistered))
            && packetBounded retryRegistered
        proposedOrder=case i.items of
            first::second::rest -> second::first::rest
            _ -> []
        pendingMatches=(desktop pending).pins.pending |> Maybe.map (\proposal -> proposal.identities==proposedOrder && field "requestId" wire==E.string (UInt64.string proposal.request)) |> Maybe.withDefault False
        reached=(desktop fixture.model).open && pendingMatches && field "binding" wire==binding i && textField "kind" wire=="taskbar-pins-write" && (desktop pending).pins.snapshot==(desktop fixture.model).pins.snapshot
        freshCleared=String.contains "not sent" (desktop (Tuple.first rejected)).pins.notice && (desktop (Tuple.first rejected)).pins.pending==Nothing && (desktop (Tuple.first rejected)).pins.snapshot==(desktop pending).pins.snapshot
        unknownPreserved=(desktop unknown.model).pins.pending/=Nothing && String.contains "not confirmed" (desktop unknown.model).pins.notice && (desktop (Tuple.first unknownRejected)).pins==(desktop unknown.model).pins && recoveryPreserved
        peerPreserved=(desktop (Tuple.first foreignRejected)).pins==(desktop pending).pins && (desktop (Tuple.first requestRejected)).pins==(desktop pending).pins
        preservedPairs=[(pending,rejected),(unknown.model,unknownRejected),(recovery.model,recoveryRejected),(pending,foreignRejected),(pending,requestRejected)]
        batchCustody=List.all (\(before,result) -> Outputs.pendingBatches before==Outputs.pendingBatches (Tuple.first result)) preservedPairs
        noAllocation=List.all (\(before,result) -> (desktop before).request==(desktop (Tuple.first result)).request) preservedPairs
        checks=[("freshActionAfterLocalRefusalAdmitted",retryAdmitted),("refusalPreservesRegisteredBatchCount",batchCustody),("refusalDoesNotAllocateRequest",noAllocation),("publishedPinReachable",reached),("sixteenRequestsAdmitted",List.length (packetRequests admitted)==16 && (desktop (Tuple.first admitted)).pins==(desktop pending).pins && Outputs.pendingBatches (Tuple.first admitted)==Outputs.pendingBatches pending+1),("seventeenRequestsRefused",noRequests rejected && compact rejected),("freshSavingLocallyUnsent",freshCleared),("unknownReservationPreserved",unknownPreserved && noRequests unknownRejected && compact unknownRejected && noRequests recoveryRejected && compact recoveryRejected),("mismatchedIdentityPreserved",peerPreserved && noRequests foreignRejected && noRequests requestRejected),("noPartialReplay",List.all noRequests [rejected,unknownRejected,recoveryRejected,foreignRejected,requestRejected]),("everyFallbackBounded",List.all packetBounded [rejected,unknownRejected,recoveryRejected,foreignRejected,requestRejected])]
    in {checks=checks,row=E.object [("seed",E.int seed),("binding",binding i),("setup",fixture.trace),("publishedMoveAction",moveAction),("actualPinWire",wire),("unknownReceipt",unknownRaw),("recoveryAction",recoveryAction),("actualRecoveryWire",recoveryWire),("allocatedRecoveryMarker",E.bool recoveryReached),("retryNavigation",E.list identity retryPage.trace),("retryAction",retryAction),("actualFreshRetryWire",retryWire),("freshRetryReachable",E.bool retryReachable),("retryPinsBeforeRegistration",pinState retryPending),("checks",E.object (List.map (Tuple.mapSecond E.bool) checks)),("outcomes",E.list identity [resultTrace "17-fresh" pending rejected,resultTrace "16-fresh" pending admitted,resultTrace "17-unknown" unknown.model unknownRejected,resultTrace "explicit-recovery-read" unknown.model (recovery.model,recovery.packet),resultTrace "17-unknown-with-recovery-marker" recovery.model recoveryRejected,resultTrace "17-foreign-binding" pending foreignRejected,resultTrace "17-foreign-request" pending requestRejected,resultTrace "fresh-published-action-after-local-refusal" retryPending retryRegistered])]}

boundaries =
    let focus text=Controller.DesktopEffect (Desktop.Focus text)
        send value=Controller.DesktopEffect (Desktop.Send value)
        bare value=Outputs.register [send value] Outputs.initial
        exactAscii=bare (E.string (String.repeat 8190 "x"))
        overAscii=bare (E.string (String.repeat 8191 "x"))
        exactUnicode=bare (E.string (String.repeat 4095 "é"))
        overUnicode=bare (E.string (String.repeat 4095 "é"++"x"))
        base=Outputs.register [focus ""] Outputs.initial
        overhead=bytes (E.encode 0 (packetValue base))
        payloadBytes=131072-overhead
        unicode=String.repeat (payloadBytes//2) "é"++String.repeat (modBy 2 payloadBytes) "x"
        wholeExact=Outputs.register [focus unicode] Outputs.initial
        wholeOver=Outputs.register [focus (unicode++"x")] Outputs.initial
        huge=String.repeat 70000 "é"
        emptyOverflow=Outputs.register [focus huge] Outputs.initial
        unboundOverflow=Outputs.register [send (E.string "unbound"),focus huge] Outputs.initial
        missingBindingOverflow=Outputs.register [Controller.DesktopEffect (Desktop.WindowEffect Shell.RestartBackend),focus huge] Outputs.initial
        initialDesktop=desktop Outputs.initial
        readonlyDesktop=desktop (Tuple.first emptyOverflow)
        readonlyPreserved=readonlyDesktop.pins==initialDesktop.pins && readonlyDesktop.applications==initialDesktop.applications && readonlyDesktop.request==initialDesktop.request && readonlyDesktop.windows==initialDesktop.windows
        checks=[("requestlessDomainPreserved",readonlyPreserved),("request8192AsciiAdmitted",List.length (packetRequests exactAscii)==1 && not (desktop (Tuple.first exactAscii)).presentationCapacity),("request8193AsciiRefused",noRequests overAscii && compact overAscii),("request8192UnicodeAdmitted",List.length (packetRequests exactUnicode)==1 && not (desktop (Tuple.first exactUnicode)).presentationCapacity),("request8193UnicodeRefused",noRequests overUnicode && compact overUnicode),("whole131072UnicodeAdmitted",bytes (E.encode 0 (packetValue wholeExact))==131072 && not (desktop (Tuple.first wholeExact)).presentationCapacity),("whole131073UnicodeCompacted",compact wholeOver && noRequests wholeOver),("requestlessOverflowCompacted",compact emptyOverflow && noRequests emptyOverflow && Outputs.pendingBatches (Tuple.first emptyOverflow)==0),("unboundOverflowCompacted",compact unboundOverflow && noRequests unboundOverflow),("missingBindingOverflowCompacted",compact missingBindingOverflow && noRequests missingBindingOverflow)]
    in {checks=checks,row=E.object [("seed",E.int -1),("kind",E.string "Adversarial registration-boundary inputs, not Desktop-produced requests"),("baseCommitUtf8Bytes",E.int overhead),("wholeInputUtf8Bytes",E.int 131073),("checks",E.object (List.map (Tuple.mapSecond E.bool) checks)),("outcomes",E.list identity [resultTrace "request-8192-ascii" Outputs.initial exactAscii,resultTrace "request-8193-ascii" Outputs.initial overAscii,resultTrace "request-8192-unicode" Outputs.initial exactUnicode,resultTrace "request-8193-unicode" Outputs.initial overUnicode,resultTrace "whole-131072-unicode" Outputs.initial wholeExact,resultTrace "whole-131073-unicode" Outputs.initial wholeOver,resultTrace "requestless-overflow" Outputs.initial emptyOverflow,resultTrace "unbound-overflow" Outputs.initial unboundOverflow,resultTrace "missing-binding-overflow" Outputs.initial missingBindingOverflow])]}

main : Program () () Never
main =
    Platform.worker
        { init =
            \_ ->
                let
                    cases = List.range 0 31 |> List.map pipeline
                    names = List.head cases |> Maybe.map (.checks >> List.map Tuple.first) |> Maybe.withDefault []
                    allChecks =
                        List.map
                            (\name ->
                                ( name
                                , List.all
                                    (\item ->
                                        List.filter (Tuple.first >> (==) name) item.checks
                                            |> List.head
                                            |> Maybe.map Tuple.second
                                            |> Maybe.withDefault False
                                    )
                                    cases
                                )
                            )
                            names
                            ++ boundaries.checks
                in
                ( ()
                , outgoing
                    (E.object
                        [ ( "checks", E.object (List.map (Tuple.mapSecond E.bool) allChecks) )
                        , ( "cases", E.list .row (cases ++ [boundaries]) )
                        ]
                    )
                )
        , update = \_ model -> (model,Cmd.none)
        , subscriptions = \_ -> Sub.none
        }
