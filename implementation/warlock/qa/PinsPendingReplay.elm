port module PinsPendingReplay exposing (main)

{-| Source-bound TEA003 pin-order fixture. Every interaction uses the actual
owning output/controller route and a currently published SurfaceSnapshot action.
Native frames are explicit bridge fixtures, not native acceptance evidence.
-}

import Binding
import Catalog
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
increment value = counter value |> UInt64.next |> Maybe.map UInt64.string |> Maybe.withDefault value
advance count value = List.range 1 count |> List.foldl (\_ current -> increment current) value
field name raw = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
textField name raw = D.decodeValue (D.field name D.string) raw |> Result.withDefault "0"
replace name value raw = D.decodeValue (D.keyValuePairs D.value) raw |> Result.map (\pairs -> E.object ((name,value)::List.filter (Tuple.first >> (/=) name) pairs)) |> Result.withDefault raw

values seed =
    let shifted=advance (modBy 17 seed)
        count=2+modBy 7 seed
    in {life=shifted "9007199254741001",session=shifted "9007199254741101",epoch=shifted "9007199254741201",output=shifted "9007199254741301",revision=shifted "9007199254741401",pinsRevision=shifted "9007199254745002",olderPinsRevision=shifted "9007199254745001",variant=shifted "9007199254750001",items=List.range 0 (count-1) |> List.map (\index -> "seed-"++String.fromInt seed++"-pin-"++String.fromInt index++".desktop")}
bound i = E.object [("lifetime",E.string i.life),("session",E.string i.session),("frontend",E.string i.epoch)]
native kind fields = E.object ([("protocolVersion",E.int 3),("kind",E.string kind)]++fields)
scope = E.object [("id",E.string "1"),("generation",E.string "1")]
topology = E.object [("viewProtocol",E.int 2),("kind",E.string "view-topology"),("revision",E.string "1"),("views",E.list identity [scope]),("locations",E.list identity [E.object [("scope",scope),("box",E.list E.int [0,0,800,600])]])]
desktop model = Controller.desktop (Outputs.controller model)
shell model = (desktop model).windows.shell
currentFrame model = Controller.frame (Outputs.controller model)
step event model =
    let (next,emitted)=Outputs.update event model
        (registered,commit)=Outputs.register emitted next
    in {model=registered,effects=emitted,commit=commit}
receive input model = step (Outputs.Interaction (Desktop.Incoming input)) model
wireValues emitted = List.filterMap (\effect -> case effect of
    Controller.DesktopEffect (Desktop.Send wire) -> Just wire
    _ -> Nothing) emitted
findWire kind result = wireValues result.effects |> List.filter (\raw -> textField "kind" raw==kind) |> List.head |> Maybe.withDefault E.null
expected model = (desktop model).expected |> Maybe.map UInt64.string |> Maybe.withDefault "0"
publishedAction popup identity model = SurfaceSnapshot.decode (currentFrame model) |> Result.toMaybe |> Maybe.andThen (SurfaceSnapshot.action popup identity)
rendererAction action = E.object [("viewProtocol",E.int 1),("kind",E.string "view-action"),("scope",scope),("action",action)]
perform popup identity model =
    let action=publishedAction popup identity model |> Maybe.withDefault E.null
    in {action=rendererAction action,result=step (Outputs.Renderer (rendererAction action)) model}

preferences revision identities = E.object [("revision",E.string revision),("identities",E.list E.string identities)]
catalog i = E.object [("catalogProtocol",E.int 2),("lifetime",E.string i.life),("generation",E.string i.revision),("entries",E.list (\identity -> E.object [("id",E.string identity),("name",E.string ("Pinned "++identity)),("iconHint",E.string ""),("wmclass",E.string ""),("genericName",E.string ""),("keywords",E.list E.string [])]) i.items)]
catalogReceipt i request pins = native "application-catalog" [("binding",bound i),("requestId",E.string request),("snapshot",catalog i),("preferences",pins)]
outcome i request status pins = native "taskbar-pins-outcome" [("binding",bound i),("requestId",E.string request),("status",E.string status),("preferences",pins)]
projection i request = native "action-projection" [("binding",bound i),("requestId",E.string request),("context",E.object [("lifetime",E.string i.life),("epoch",E.string i.epoch),("output",E.string i.output),("revision",E.string i.revision)]),("scene",E.object [("revision",E.string i.revision),("focused",E.null),("windows",E.list identity [])])]

setup i =
    let located=step (Outputs.Topology topology) Outputs.initial
        attachedRaw=native "attached" [("binding",bound i)]
        attached=receive attachedRaw located.model
        projectionRaw=projection i ((shell attached.model).expected |> Maybe.map UInt64.string |> Maybe.withDefault "0")
        projected=receive projectionRaw attached.model
        pointerRaw=native "pointer-ownership" [("ownershipProtocol",E.int 1),("binding",bound i),("requestId",E.string "1"),("serial",E.string "1"),("state",E.string "idle"),("owner",E.null)]
        pointed=receive pointerRaw projected.model
        opened=perform False "bar:applications" pointed.model
        pins=preferences i.pinsRevision i.items
        catalogRaw=catalogReceipt i (expected opened.result.model) pins
        ready=receive catalogRaw opened.result.model
    in {model=ready.model,raw=E.object [("topology",topology),("attached",attachedRaw),("projection",projectionRaw),("pointer",pointerRaw),("openAction",opened.action),("openCommit",opened.result.commit |> Maybe.withDefault E.null),("catalog",catalogRaw)],effects=ready.effects}

state model =
    let current=desktop model
        pins=current.pins
        nullableCounter value=value |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null
    in E.object [("request",E.string (UInt64.string current.request)),("expected",nullableCounter current.expected),("open",E.bool current.open),("query",E.string current.query),("binding",current.windows.shell.binding |> Maybe.map Binding.encode |> Maybe.withDefault E.null),("applications",current.applications |> Maybe.map (Catalog.entries >> List.map (.identity >> Catalog.id) >> E.list E.string) |> Maybe.withDefault E.null),("pins",E.object [("snapshot",pins.snapshot |> Maybe.map Pins.encode |> Maybe.withDefault E.null),("pending",pins.pending |> Maybe.map (\pending -> E.object [("request",E.string (UInt64.string pending.request)),("identities",E.list E.string pending.identities)]) |> Maybe.withDefault E.null),("notice",E.string pins.notice),("writable",E.bool (Pins.writable pins))]),("popupOwner",Outputs.owner model |> Maybe.map Outputs.encodeScope |> Maybe.withDefault E.null),("pendingBatches",E.int (Outputs.pendingBatches model))]
description effect = case effect of
    Controller.Publish frame -> E.object [("kind",E.string "publish"),("frame",frame)]
    Controller.DesktopEffect (Desktop.Send raw) -> E.object [("kind",E.string "send"),("wire",raw)]
    Controller.DesktopEffect (Desktop.Focus target) -> E.object [("kind",E.string "focus"),("target",E.string target)]
    Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send raw)) -> E.object [("kind",E.string "window-send"),("wire",raw)]
    _ -> E.object [("kind",E.string "unhandled")]
eventRow name contract input before result = E.object [("name",E.string name),("contract",E.string contract),("input",input),("before",state before),("after",state result.model),("frameBefore",currentFrame before),("frameAfter",currentFrame result.model),("effects",E.list description result.effects),("commit",result.commit |> Maybe.withDefault E.null),("sameDesktop",E.bool (desktop before==desktop result.model)),("sameOutput",E.bool (before==result.model))]

pipeline seed =
    let i=values seed
        fixture=setup i
        initial=fixture.model
        target=List.drop 1 i.items |> List.head |> Maybe.withDefault ""
        moveId="pin-left:"++target
        oldPins=preferences i.pinsRevision i.items
        refreshed=perform True "control:refresh" initial
        moved=perform True moveId refreshed.result.model
        readWire=findWire "catalog-request" refreshed.result
        writeWire=findWire "taskbar-pins-write" moved.result
        proposal=field "proposal" writeWire
        nextPins=replace "revision" (E.string (increment i.pinsRevision)) proposal
        readRaw=catalogReceipt i (textField "requestId" readWire) oldPins
        readResult=receive readRaw moved.result.model
        savedRaw=outcome i (textField "requestId" writeWire) "Saved" nextPins
        savedResult=receive savedRaw readResult.model
        repeatMove=perform True moveId readResult.model
        firstWrite=perform True moveId initial
        firstWire=findWire "taskbar-pins-write" firstWrite.result
        firstProposal=field "proposal" firstWire
        firstNext=replace "revision" (E.string (increment i.pinsRevision)) firstProposal
        afterWriteRefresh=perform True "control:refresh" firstWrite.result.model
        afterWriteReadWire=findWire "catalog-request" afterWriteRefresh.result
        firstSavedRaw=outcome i (textField "requestId" firstWire) "Saved" firstNext
        firstSaved=receive firstSavedRaw afterWriteRefresh.result.model
        afterWriteReadRaw=catalogReceipt i (textField "requestId" afterWriteReadWire) firstNext
        afterWriteRead=receive afterWriteReadRaw firstSaved.model
        unknownRaw=outcome i (textField "requestId" firstWire) "Unknown" E.null
        unknown=receive unknownRaw firstWrite.result.model
        unknownRefresh=perform True "control:refresh" unknown.model
        recoveryWire=findWire "catalog-request" unknownRefresh.result
        recoveryRaw=catalogReceipt i (textField "requestId" recoveryWire) firstNext
        recovered=receive recoveryRaw unknownRefresh.result.model
        unknownWithOldRead=receive unknownRaw afterWriteRefresh.result.model
        oldReadAfterUnknown=receive afterWriteReadRaw unknownWithOldRead.model
        savedAfterOldRead=receive firstSavedRaw oldReadAfterUnknown.model
        laterRecovery=perform True "control:refresh" oldReadAfterUnknown.model
        laterRecoveryWire=findWire "catalog-request" laterRecovery.result
        laterRecoveryRaw=catalogReceipt i (textField "requestId" laterRecoveryWire) firstNext
        laterRecovered=receive laterRecoveryRaw laterRecovery.result.model
        refusedRaw=outcome i (textField "requestId" firstWire) "Refused" oldPins
        refused=receive refusedRaw firstWrite.result.model
        variant=E.string i.variant
        mutateBinding key original=replace "binding" (replace key variant (field "binding" original)) original
        readNegatives=[("foreign-lifetime",mutateBinding "lifetime" readRaw),("foreign-session",mutateBinding "session" readRaw),("foreign-frontend",mutateBinding "frontend" readRaw),("foreign-request",replace "requestId" variant readRaw),("numeric-request",replace "requestId" (E.int 2) readRaw),("numeric-revision",replace "preferences" (replace "revision" (E.float 9007199254740992) oldPins) readRaw),("extra-envelope",replace "unexpected" (E.bool True) readRaw),("duplicate-identities",replace "preferences" (replace "identities" (E.list E.string [target,target]) oldPins) readRaw),("unknown-preference-field",replace "preferences" (replace "unexpected" (E.bool True) oldPins) readRaw)]
        savedNegatives=[("foreign-binding",mutateBinding "session" firstSavedRaw),("foreign-request",replace "requestId" variant firstSavedRaw),("numeric-request",replace "requestId" (E.int 2) firstSavedRaw),("numeric-revision",replace "preferences" (replace "revision" (E.float 9007199254740992) firstNext) firstSavedRaw),("unknown-status",replace "status" (E.string "Committed") firstSavedRaw),("extra-envelope",replace "unexpected" (E.bool True) firstSavedRaw)]
        invalidSaved=[("nonadvancing-saved",replace "preferences" (replace "revision" (E.string i.pinsRevision) firstNext) firstSavedRaw),("different-identities",replace "preferences" (replace "identities" (E.list E.string []) firstNext) firstSavedRaw)]
        staleReadRaw=catalogReceipt i (textField "requestId" readWire) (preferences i.olderPinsRevision i.items)
        readVariants=[("null-preferences",E.null),("lower-revision",preferences i.olderPinsRevision i.items),("same-revision",oldPins),("higher-revision",preferences (increment (increment i.pinsRevision)) i.items)]
        savingRead (name,pins)=
            let input=catalogReceipt i (textField "requestId" readWire) pins
            in eventRow name "preserve-pending-write" input moved.result.model (receive input moved.result.model)
        negativeRead (name,input)=eventRow name "exact-unchanged" input moved.result.model (receive input moved.result.model)
        negativeSaved (name,input)=eventRow name "exact-unchanged" input firstWrite.result.model (receive input firstWrite.result.model)
        unconfirmed (name,input)=eventRow name "pending-custody" input firstWrite.result.model (receive input firstWrite.result.model)
    in E.object [("seed",E.int seed),("pinCount",E.int (List.length i.items)),("setup",fixture.raw),("initial",state initial),("initialFrame",currentFrame initial),("moveId",E.string moveId),("readThenWrite",E.object [("refresh",eventRow "refresh-before-write" "published-action" refreshed.action initial refreshed.result),("move",eventRow "move-before-read-response" "published-action" moved.action refreshed.result.model moved.result),("read",eventRow "older-issued-catalog-read" "preserve-pending-write" readRaw moved.result.model readResult),("saved",eventRow "matching-Saved-after-read" "matching-Saved" savedRaw readResult.model savedResult),("repeatMove",eventRow "conflicting-second-command" "blocked-pending" repeatMove.action readResult.model repeatMove.result)]),("writeThenRead",E.object [("move",eventRow "write-first" "published-action" firstWrite.action initial firstWrite.result),("refresh",eventRow "read-issued-after-write" "published-action" afterWriteRefresh.action firstWrite.result.model afterWriteRefresh.result),("saved",eventRow "Saved-before-later-read" "matching-Saved" firstSavedRaw afterWriteRefresh.result.model firstSaved),("read",eventRow "read-after-Saved" "read-confirmed" afterWriteReadRaw firstSaved.model afterWriteRead)]),("unknownRecovery",E.object [("unknown",eventRow "Unknown-retains-write" "pending-custody" unknownRaw firstWrite.result.model unknown),("refresh",eventRow "explicit-read-after-Unknown" "published-action" unknownRefresh.action unknown.model unknownRefresh.result),("read",eventRow "new-read-reconciles-Unknown" "read-recovery" recoveryRaw unknownRefresh.result.model recovered)]),("unknownOlderRead",E.object [("unknown",eventRow "Unknown-with-read-already-issued" "pending-custody" unknownRaw afterWriteRefresh.result.model unknownWithOldRead),("olderRead",eventRow "read-issued-before-Unknown" "pending-custody" afterWriteReadRaw unknownWithOldRead.model oldReadAfterUnknown),("saved",eventRow "matching-Saved-after-unconfirmed-old-read" "matching-Saved" firstSavedRaw oldReadAfterUnknown.model savedAfterOldRead),("refresh",eventRow "new-explicit-read-after-older-response" "published-action" laterRecovery.action oldReadAfterUnknown.model laterRecovery.result),("read",eventRow "later-read-reconciles-Unknown" "read-recovery" laterRecoveryRaw laterRecovery.result.model laterRecovered)]),("refused",eventRow "matching-Refused" "matching-Refused" refusedRaw firstWrite.result.model refused),("readVariants",E.list savingRead readVariants),("readNegatives",E.list negativeRead readNegatives),("savedNegatives",E.list negativeSaved savedNegatives),("invalidSaved",E.list unconfirmed invalidSaved),("staleRead",eventRow "stale-pin-revision" "pending-custody" staleReadRaw moved.result.model (receive staleReadRaw moved.result.model)),("duplicateSaved",eventRow "duplicate-Saved" "exact-unchanged" savedRaw savedResult.model (receive savedRaw savedResult.model)),("duplicateRead",eventRow "duplicate-old-read" "exact-unchanged" readRaw savedResult.model (receive readRaw savedResult.model))]

main : Program Int () Never
main =
    Platform.worker
        { init =
            \seed ->
                ( ()
                , outgoing
                    (E.object
                        [ ( "schema", E.int 1 )
                        , ( "requirement", E.string "ELM-TEA-003" )
                        , ( "scenario", E.string "tea-effects" )
                        , ( "scope", E.string "Actual published renderer/output/controller/Desktop pin save ordering with explicit bridge fixtures; no native acceptance" )
                        , ( "pipeline", pipeline seed )
                        ]
                    )
                )
        , update = \_ model -> ( model, Cmd.none )
        , subscriptions = \_ -> Sub.none
        }
