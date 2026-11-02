port module SolFilesRebind2214 exposing (main)

-- QA-only, unexecuted. Requires the Files Confirmation base92f1 patch.
-- Every input enters Desktop.update; no authority constructor or model mutator.
-- Pointer idle is a synthetic source fixture through its real decoder, not
-- an observed native input fact. This worker accepts no native operation.
import Binding
import Desktop
import Files
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

counter : String -> UInt64.Counter
counter raw = D.decodeValue UInt64.decoder (E.string raw) |> Result.withDefault UInt64.zero

type alias Seed = { id : Int, old : (String,String,String), fresh : (String,String,String) }

seeds : List Seed
seeds =
    [ {id=0,old=("1","1","1"),fresh=("1","2","2")}
    , {id=1,old=("9007199254740991","1","1"),fresh=("9007199254740991","2","2")}
    , {id=2,old=("9007199254740992","9007199254740992","1"),fresh=("9007199254740992","9007199254740993","2")}
    , {id=3,old=("18446744073709551615","1","18446744073709551613"),fresh=("18446744073709551615","1","18446744073709551614")}
    , {id=4,old=("1","18446744073709551615","1"),fresh=("2","18446744073709551615","1")}
    , {id=5,old=("1","1","9007199254740992"),fresh=("1","1","9007199254740993")}
    , {id=6,old=("18446744073709551615","18446744073709551615","18446744073709551614"),fresh=("18446744073709551615","18446744073709551615","18446744073709551615")}
    , {id=7,old=("1","1","1"),fresh=("18446744073709551615","18446744073709551615","18446744073709551615")}
    ]

bindingWire : (String,String,String) -> E.Value
bindingWire (life,session,frontend) = E.object [("lifetime",E.string life),("session",E.string session),("frontend",E.string frontend)]

header : String -> List (String,E.Value)
header kind = [("protocolVersion",E.int 3),("kind",E.string kind)]

attached : E.Value -> E.Value
attached binding = E.object (header "attached" ++ [("binding",binding)])

idle : E.Value -> E.Value
idle binding = E.object (header "pointer-ownership" ++ [("ownershipProtocol",E.int 1),("binding",binding),("requestId",E.string "1"),("serial",E.string "1"),("state",E.string "idle"),("owner",E.null)])

lost : E.Value
lost = E.object (header "host-disconnected")

peerAt : String -> Files.Peer
peerAt target = {pid=counter "20",start=counter "40",instance="owned1",target=target,visible=True}

snapshotAt : String -> String -> Files.Snapshot
snapshotAt revision target = {service=counter "9",revision=counter revision,available=True,reason="",peer=Just (peerAt target)}

snapshotWire : String -> String -> E.Value
snapshotWire revision target = E.object
    [("service",E.string "9"),("revision",E.string revision),("available",E.bool True),("reason",E.string "")
    ,("peer",E.object [("pid",E.string "20"),("start",E.string "40"),("instance",E.string "owned1"),("target",E.string target),("visible",E.bool True)])]

readWire : String -> E.Value -> String -> E.Value
readWire kind binding request = E.object (header kind ++ [("binding",binding),("requestId",E.string request)])

loaded : E.Value -> String -> String -> String -> E.Value
loaded binding request revision target = E.object (header "files-snapshot" ++ [("binding",binding),("requestId",E.string request),("snapshot",snapshotWire revision target)])

outcome : E.Value -> String -> String -> String -> String -> E.Value
outcome binding request status revision target = E.object (header "files-outcome" ++ [("binding",binding),("requestId",E.string request),("status",E.string status),("snapshot",snapshotWire revision target)])

intent : Files.Intent
intent = {service=counter "9",revision=counter "1",target="coll:images"}

openWire : E.Value -> String -> E.Value
openWire binding request = E.object (header "files-open" ++ [("binding",binding),("requestId",E.string request),("intent",E.object [("service",E.string "9"),("revision",E.string "1"),("target",E.string "coll:images")])])

-- Complete child states below are literal independent expectations. They do
-- not call Files.initial/observe/propose/receive/disconnect or copy its output.
readExpected : Files.Model
readExpected = {snapshot=Just (snapshotAt "1" "home"),draft="",pending=Nothing,spent=[],notice="Choose a collection or folder."}

pendingExpected : String -> Files.Confirmation -> String -> Files.Model
pendingExpected request phase notice = {snapshot=Just (snapshotAt "1" "home"),draft="",pending=Just {request=counter request,intent=intent,confirmation=phase},spent=[intent],notice=notice}

awaitingNotice : String
awaitingNotice = "Files: waiting for the requested location…"
unknownNotice : String
unknownNotice = "Files: opening not confirmed. Refresh only reads state; this request will not be repeated."
lostNotice : String
lostNotice = "Files: opening not confirmed after connection loss. Open the menu to read current state; this request will not be repeated."

disconnectedExpected : String -> Files.Model
disconnectedExpected notice = {snapshot=Nothing,draft="",pending=Nothing,spent=[],notice=notice}

openedExpected : Files.Model
openedExpected = {snapshot=Just (snapshotAt "2" "coll:images"),draft="",pending=Nothing,spent=[intent],notice="Files: requested location opened."}

refusedExpected : Files.Model
refusedExpected = {snapshot=Just (snapshotAt "1" "home"),draft="",pending=Nothing,spent=[intent],notice="Files: request refused. Refresh before choosing again."}

native : E.Value -> Desktop.Model -> (Desktop.Model,List Desktop.Effect)
native raw = Desktop.update (Desktop.Incoming raw)

gesture : (Desktop.ViewStamp -> Desktop.Msg) -> Desktop.Model -> (Desktop.Model,List Desktop.Effect)
gesture build model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (build stamp) model) |> Maybe.withDefault (model,[])

wireEqual : E.Value -> E.Value -> Bool
wireEqual actual expected = E.encode 0 actual == E.encode 0 expected

soleSend : E.Value -> List Desktop.Effect -> Bool
soleSend expected effects = case effects of
    [Desktop.Send actual] -> wireEqual actual expected
    _ -> False

-- Focus counters are independently derived from the fixed prelude's pure
-- Desktop.advance calls, not read back from the reducer as expected values.
focusKey : E.Value -> String -> String
focusKey binding publication = "applications:" ++ E.encode 0 binding ++ ":" ++ publication ++ ":files:close"

openReadEffects : E.Value -> String -> String -> List Desktop.Effect -> Bool
openReadEffects binding request publication effects = case effects of
    [Desktop.Send actual,Desktop.Focus target] -> wireEqual actual (readWire "files-request" binding request) && target==focusKey binding publication
    _ -> False

soleFocus : E.Value -> String -> List Desktop.Effect -> Bool
soleFocus binding publication effects = case effects of
    [Desktop.Focus target] -> target==focusKey binding publication
    _ -> False

soleRestart : List Desktop.Effect -> Bool
soleRestart effects = case effects of
    [Desktop.WindowEffect Shell.RestartBackend] -> True
    _ -> False

-- Every reached effect of reattachment is checked, including non-Files reads;
-- an extra effect or Files mutation cannot hide in a filtered projection.
reattachEffects : E.Value -> List Desktop.Effect -> Bool
reattachEffects binding effects = case effects of
    [Desktop.Send catalog,Desktop.Send settings,Desktop.Send motion,Desktop.Send shortcuts,Desktop.WindowEffect (Shell.Send projection)] ->
        wireEqual catalog (readWire "catalog-request" binding "7")
            && wireEqual settings (readWire "shell-settings-request" binding "8")
            && wireEqual motion (readWire "motion-preferences-request" binding "9")
            && wireEqual shortcuts (readWire "shortcut-preferences-request" binding "10")
            && wireEqual projection (readWire "projection-request" binding "2")
    _ -> False

sameBinding : E.Value -> Desktop.Model -> Bool
sameBinding expected model = model.windows.shell.binding |> Maybe.map (Binding.encode >> (\actual -> wireEqual actual expected)) |> Maybe.withDefault False

checksFor : Seed -> List (String,Bool)
checksFor seed =
    let
        a = bindingWire seed.old
        b = bindingWire seed.fresh
        -- Named GIVEN arrangement, independently checked below. No direct
        -- record mutation: attachment, native idle, read and input are real
        -- Desktop handlers. No native input/provider observation is claimed.
        aAttached = native (attached a) Desktop.initial |> Tuple.first
        aIdle = native (idle a) aAttached |> Tuple.first
        (aOpening,aOpeningEffects) = gesture Desktop.OpenFiles aIdle
        (aRead,aReadEffects) = native (loaded a "5" "1" "home") aOpening
        (aPending,aOpenEffects) = gesture (\stamp -> Desktop.OpenFilesTarget stamp intent) aRead
        (aUnknown,aUnknownEffects) = native (outcome a "6" "Unknown" "1" "home") aPending
        (aDisconnected,aDisconnectEffects) = native lost aUnknown
        (aUnsentDisconnected,aUnsentDisconnectEffects) = native lost aRead
        (reconnecting,reconnectEffects) = Desktop.update (Desktop.Window (TaskbarShell.Native Shell.Reconnect)) aDisconnected
        (rebound,rebindEffects) = native (attached b) reconnecting
        (bIdle,bIdleEffects) = native (idle b) rebound
        (bOpening,bOpeningEffects) = gesture Desktop.OpenFiles bIdle
        (bRead,bReadEffects) = native (loaded b "11" "1" "home") bOpening
        (bRefresh,bRefreshEffects) = gesture Desktop.RefreshFiles bRead
        (bRefreshDuplicate,bRefreshDuplicateEffects) = gesture Desktop.RefreshFiles bRefresh
        (bReadAgain,bReadAgainEffects) = native (loaded b "12" "1" "home") bRefresh
        (bPending,bOpenEffects) = gesture (\stamp -> Desktop.OpenFilesTarget stamp intent) bReadAgain
        (oldReceipt,oldReceiptEffects) = native (outcome a "6" "Opened" "2" "coll:images") bPending
        -- This old-binding receipt deliberately uses the NEW pending request
        -- and otherwise valid payload, isolating the binding guard itself.
        (oldBindingCurrentRequest,oldBindingCurrentEffects) = native (outcome a "13" "Opened" "2" "coll:images") bPending
        (freshBindingOldRequest,freshBindingOldEffects) = native (outcome b "6" "Opened" "2" "coll:images") bPending
        (bUnknown,bUnknownEffects) = native (outcome b "13" "Unknown" "1" "home") bPending
        (bOpened,bOpenedEffects) = native (outcome b "13" "Opened" "2" "coll:images") bUnknown
        (bRefused,bRefusedEffects) = native (outcome b "13" "Refused" "1" "home") bUnknown
        (oldRead,oldReadEffects) = native (loaded a "12" "2" "coll:images") bRefresh
        (staleAttach,staleAttachEffects) = native (attached a) rebound
        named suffix ok = ("binding-seed-" ++ String.fromInt seed.id ++ "/" ++ suffix,ok)
    in
    [ named "given-bindings-are-valid-and-distinct" (case (D.decodeValue Binding.decoder a,D.decodeValue Binding.decoder b) of
        (Ok old,Ok fresh) -> old/=fresh && Binding.replaces fresh old
        _ -> False)
    , named "given-a-read-complete-child-and-request" (aRead.files==readExpected && aRead.request==counter "5" && aRead.filesExpected==Nothing && sameBinding a aRead && openReadEffects a "5" "3" aOpeningEffects && soleFocus a "4" aReadEffects)
    , named "one-a-open-exact-wire-and-complete-awaiting" (soleSend (openWire a "6") aOpenEffects && aPending.files==pendingExpected "6" Files.Awaiting awaitingNotice)
    , named "a-unknown-complete-child-with-no-effect" (aUnknown.files==pendingExpected "6" Files.Unconfirmed unknownNotice && List.isEmpty aUnknownEffects)
    , named "disconnect-retires-old-reservation-honestly" (aDisconnected.files==disconnectedExpected lostNotice && not aDisconnected.filesOpen && aDisconnected.filesExpected==Nothing && aDisconnected.windows.shell.phase==Shell.Detached && List.isEmpty aDisconnectEffects)
    , named "unemitted-disconnect-does-not-invent-unknown" (aUnsentDisconnected.files==disconnectedExpected "Choose a collection or folder." && List.isEmpty aUnsentDisconnectEffects)
    , named "explicit-reconnect-only-restarts-backend" (soleRestart reconnectEffects && reconnecting.files==disconnectedExpected lostNotice && reconnecting.windows.shell.reconnecting)
    , named "reattach-checks-all-read-effects-no-files-mutation" (reattachEffects b rebindEffects && rebound.files==disconnectedExpected lostNotice && rebound.request==counter "10" && sameBinding b rebound)
    , named "new-binding-idle-real-decoder-has-no-effect" (List.isEmpty bIdleEffects && bIdle.files==disconnectedExpected lostNotice)
    , named "new-binding-read-complete-child-no-spent-authority" (bRead.files==readExpected && bRead.request==counter "11" && bRead.filesExpected==Nothing && bRead.filesOpen && openReadEffects b "11" "11" bOpeningEffects && soleFocus b "12" bReadEffects)
    , named "refresh-exact-read-only-wire" (soleSend (readWire "files-request" b "12") bRefreshEffects && bRefresh.files==readExpected && bRefresh.filesExpected==Just (counter "12"))
    , named "duplicate-refresh-preserves-entire-desktop-no-effect" (bRefreshDuplicate==bRefresh && List.isEmpty bRefreshDuplicateEffects)
    , named "refresh-reply-complete-child-no-effect" (bReadAgain.files==readExpected && bReadAgain.filesExpected==Nothing && List.isEmpty bReadAgainEffects)
    , named "fresh-explicit-open-is-new-current-scope-intent" (soleSend (openWire b "13") bOpenEffects && bPending.files==pendingExpected "13" Files.Awaiting awaitingNotice)
    , named "old-binding-old-request-preserves-entire-desktop" (oldReceipt==bPending && List.isEmpty oldReceiptEffects)
    , named "old-binding-current-request-preserves-entire-desktop" (oldBindingCurrentRequest==bPending && List.isEmpty oldBindingCurrentEffects)
    , named "fresh-binding-old-request-preserves-entire-desktop" (freshBindingOldRequest==bPending && List.isEmpty freshBindingOldEffects)
    , named "old-binding-read-preserves-entire-desktop" (oldRead==bRefresh && List.isEmpty oldReadEffects)
    , named "unsolicited-old-attachment-preserves-entire-desktop" (staleAttach==rebound && List.isEmpty staleAttachEffects)
    , named "fresh-unknown-complete-child-and-zero-effects" (bUnknown.files==pendingExpected "13" Files.Unconfirmed unknownNotice && List.isEmpty bUnknownEffects)
    , named "fresh-opened-positive-complete-child-and-zero-effects" (bOpened.files==openedExpected && List.isEmpty bOpenedEffects)
    , named "fresh-refusal-positive-complete-child-and-zero-effects" (bRefused.files==refusedExpected && List.isEmpty bRefusedEffects)
    ]

result : E.Value
result =
    let cases = List.concatMap checksFor seeds
    in E.object
        [("schema",E.int 1)
        ,("scope",E.string "Actual pure Desktop/Shell/Files binding reconnect component; no transport/native/whole-original acceptance")
        ,("seeds",E.list E.int (List.map .id seeds))
        ,("checks",E.object (List.map (\(name,ok) -> (name,E.bool ok)) cases))
        ,("requiredCheckCount",E.int 176)
        ,("originalAccepted",E.bool False)
        ,("nativeAccepted",E.bool False)]

main : Program () () Never
main = Platform.worker {init=\() -> ((),outgoing result),update=\message _ -> never message,subscriptions=\_ -> Sub.none}
