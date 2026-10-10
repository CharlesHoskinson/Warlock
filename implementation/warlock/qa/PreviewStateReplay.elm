port module PreviewStateReplay exposing (main)

import Desktop
import Json.Decode as D
import Json.Encode as E
import NativePreviewSource as Source
import Platform
import PreviewPresenter as Presenter
import PreviewVisual as Visual
import Shell
import SurfaceController as Controller
import SurfaceRenderer as Renderer
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

binding = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
context root scene = E.object [("lifetime",E.string "1"),("incarnation",E.string root),("output",E.string "1"),("privacy",E.string "1"),("rendering",E.string "1"),("scene",E.string scene),("content",E.string "1")]
scope root scene live = E.object [("binding",binding),("context",context root scene),("observation",E.string scene),("clock",E.string "1"),("now",E.string scene),("present",E.bool True),("sourceLive",E.bool live),("locked",E.bool False),("gpuReady",E.bool True)]
source root scene live picker eligible = E.object
    [("protocolVersion",E.int 3),("kind",E.string (if picker then "preview-picker-family-scope" else "preview-family-style-crop-scope")),("binding",binding),("requestId",E.string scene),("scope",scope root scene live),("maximumTransferBytes",E.string "4096"),("previewEligible",E.bool eligible),("scopeKind",E.string (if picker then "picker-native-family-style-crop" else "native-family-style-crop-channels-unqualified")),
     ("members",E.list identity [E.object [("incarnation",E.string root),("parent",E.null),("content",E.string "1"),("renderOrder",E.int 0),("flags",E.int 1),("geometry",E.list E.int [0,0,10,10,0,0,10,10])]]),
     ("styles",E.list identity [E.object [("incarnation",E.string root),("flags",E.int 0),("channels",E.list E.int (List.repeat 18 0)),("gradients",E.list identity (List.repeat 6 (E.object [("angle",E.int 0),("colors",E.int 0)])))]]),
     ("crop",E.object [("pixelX",E.string "0"),("pixelY",E.string "0"),("width",E.int 10),("height",E.int 10),("scale",E.float 1)])]
window root = E.object [("incarnation",E.string root),("label",E.string ("Document "++root)),("owner",E.null),("application",E.string "documents"),("minimized",E.bool False),("available",E.bool True)]
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",binding)]
projection = E.object [("protocolVersion",E.int 3),("kind",E.string "action-projection"),("binding",binding),("requestId",E.string "1"),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string "1")]),("scene",E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity [window "1",window "2"])])]
native raw model = Controller.update (Controller.Interaction (Desktop.Incoming raw)) model |> Tuple.first
ready = Controller.initial |> native attached |> native projection
opened = Shell.capture (Controller.desktop ready).windows.shell |> Maybe.map (\stamp -> Controller.update (Controller.Interaction (Desktop.Window (TaskbarShell.Primary stamp "application:documents"))) ready |> Tuple.first) |> Maybe.withDefault ready
rawFrame = Controller.frame opened
frame = Renderer.decode rawFrame |> Result.toMaybe
field name raw = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
replace name value raw = D.decodeValue (D.keyValuePairs D.value) raw |> Result.map (List.map (\(key,old) -> (key,if key==name then value else old)) >> E.object) |> Result.withDefault raw
seed raw root scene live = E.object [("kind",E.string "source-seed"),("publication",field "publication" raw),("lease",field "lease" raw),("identity",E.string ("family:"++root)),("source",source root scene live True True),("title",E.string ("Document "++root)),("application",E.string "documents")]
event root body = E.object [("kind",E.string "event"),("identity",E.string ("family:"++root)),("event",body)]
request = event "1" (E.object [("kind",E.string "request"),("trigger",E.object [("binding",binding),("context",context "1" "1"),("origin",E.string "1"),("clock",E.string "1"),("deadline",E.string "1000")])])
receive raw model = Presenter.receive frame raw model
seeded = receive (seed rawFrame "1" "1" True) Presenter.initial |> Tuple.first
capturing = receive request seeded
job = D.decodeValue (D.index 0 (D.field "commands" (D.index 0 (D.field "job" D.value)))) (Tuple.second capturing) |> Result.withDefault E.null
packet ready_ fidelity coverage = E.object [("job",job),("handle",E.string (String.repeat 64 "a")),("owned",E.bool True),("signaled",E.bool ready_),("fidelity",E.string fidelity),("coverage",E.list E.string coverage),("expires",E.string "2000")]
family = ["client","decoration","modal","popup"]
frameEvent root kind ready_ fidelity coverage = event root (E.object [("kind",E.string kind),("frame",packet ready_ fidelity coverage)])
offered = receive (frameEvent "1" "offer" False "family" family) (Tuple.first capturing) |> Tuple.first
liveModel = receive (frameEvent "1" "fence" True "family" family) offered |> Tuple.first
historical = receive (seed rawFrame "1" "2" False) liveModel |> Tuple.first
unavailable = receive (seed rawFrame "1" "1" False) Presenter.initial |> Tuple.first
visual model = frame |> Maybe.map (\snapshot -> Visual.encode (Presenter.visual snapshot "family:1" model)) |> Maybe.withDefault E.null
state model = D.decodeValue (D.field "state" D.string) (visual model) |> Result.withDefault "hidden"
count raw = D.decodeValue (D.list D.value) raw |> Result.map List.length |> Result.withDefault -1
admitted raw = D.decodeValue Source.decoder raw |> Result.map (Source.source >> (==) Source.PickerFamily) |> Result.withDefault False

main = Platform.worker
    { init = \() ->
        let newFrame = replace "publication" (E.string "999") rawFrame
            newSnapshot = Renderer.decode newFrame |> Result.toMaybe
            retained = Presenter.present newSnapshot liveModel
            refreshed = Presenter.receive newSnapshot (seed newFrame "1" "2" True) (Tuple.first retained) |> Tuple.first
            replacement = Presenter.present (Renderer.decode (replace "lease" (E.string "999") newFrame) |> Result.toMaybe) liveModel
            foreign = receive (seed rawFrame "2" "1" True) (Tuple.first capturing) |> Tuple.first
            borrowed = receive (frameEvent "2" "offer" False "family" family) foreign |> Tuple.first
            badCoverage = receive (frameEvent "1" "offer" False "client" ["client"]) (Tuple.first capturing)
            commands = count (Tuple.second capturing)
            hidden = newSnapshot |> Maybe.map (\snapshot -> Presenter.visual snapshot "family:1" (Tuple.first retained)==Visual.Hidden) |> Maybe.withDefault False
            resumed = newSnapshot |> Maybe.map (\snapshot -> D.decodeValue (D.field "state" D.string) (Visual.encode (Presenter.visual snapshot "family:1" refreshed))==Ok "historical") |> Maybe.withDefault False
            retiring = Presenter.retireLegacy binding liveModel
            foreignRetiring = Presenter.retireLegacy (replace "frontend" (E.string "2") binding) liveModel
            checks =
                [("actualPickerSnapshot",frame/=Nothing),("supportedNativeSource",admitted (source "1" "1" True True True)),("unsupportedPickerEligibilityRejected",not (admitted (source "1" "1" True True False))),
                 ("legacyCannotBecomeEligible",D.decodeValue Source.decoder (source "1" "1" True False True) |> Result.map (always False) |> Result.withDefault True),
                 ("oneElmAcquire",commands==1),("loading",state (Tuple.first capturing)=="loading"),("liveNeedsFence",state offered=="loading"),("currentLive",state liveModel=="live"),("authorizedHistorical",state historical=="historical"),("unavailable",state unavailable=="unavailable"),
                 ("fullFamilyCoverageRequired",Tuple.first badCoverage==Tuple.first capturing && count (Tuple.second badCoverage)==0),
                 ("foreignIncarnationCannotBorrowPixels",frame |> Maybe.map (\snapshot -> Presenter.visual snapshot "family:2" borrowed==Presenter.visual snapshot "family:2" foreign) |> Maybe.withDefault False),
                 ("hostRetirementUsesElmRelease",count (Tuple.second retiring)==1),("foreignBindingCannotRetire",Tuple.first foreignRetiring==liveModel && count (Tuple.second foreignRetiring)==0),("sameLeaseRetainsCustody",count (Tuple.second retained)==0),("newPublicationHidesOldPixels",hidden),("nativeRefreshAuthorizesRetainedPixels",resumed),("newLeaseHidesOldFrame",Renderer.decode (replace "lease" (E.string "999") newFrame) |> Result.map (\snapshot -> Presenter.visual snapshot "family:1" (Tuple.first replacement)==Visual.Hidden) |> Result.withDefault False)]
        in ((),outgoing (E.object [("checks",E.object (List.map (\(name,ok)->(name,E.bool ok)) checks)),("frame",rawFrame),("states",E.list identity (List.map visual [Tuple.first capturing,liveModel,historical,unavailable])),("emitted",Tuple.second capturing)]))
    , update = \_ model -> (model,Cmd.none)
    , subscriptions = \_ -> Sub.none
    }
