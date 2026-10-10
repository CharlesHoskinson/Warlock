port module AnnouncementReplay exposing (main)

import Binding
import Catalog
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import Launch
import OutcomeAnnouncements as Attention
import OutputController as Outputs
import Platform
import Settings
import Shell
import SnapReplay as Fixture
import SurfaceController as Controller
import UInt64

port outgoing : E.Value -> Cmd msg
one = Fixture.counter "1"
field name raw = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
sequence model = D.decodeValue (D.field "sequence" UInt64.decoder) (Attention.encode model) |> Result.withDefault UInt64.zero
bound = Fixture.bound
binding = D.decodeValue Binding.decoder bound |> Result.toMaybe
base = binding |> Maybe.map Fixture.readyFor |> Maybe.withDefault Desktop.initial
snapshot = E.object [("catalogProtocol",E.int 1),("lifetime",E.string "1"),("generation",E.string "1"),("entries",E.list identity [E.object [("id",E.string "docs.desktop"),("name",E.string "Documents"),("iconHint",E.string ""),("wmclass",E.string "documents")]])]
launchBase = Launch.bind (E.encode 0 bound) Launch.init |> Launch.catalog snapshot
launchStarted = Launch.select "docs.desktop" launchBase |> Maybe.map (\selection -> Launch.start selection launchBase) |> Maybe.withDefault (launchBase,Nothing)
launchReceipt = E.object [("catalogProtocol",E.int 1),("kind",E.string "launch-outcome"),("intent",Tuple.second launchStarted |> Maybe.withDefault E.null),("status",E.string "Refused"),("reason",E.string "stale-catalog")]
launchBefore = {base | launch=Tuple.first launchStarted,applications=Catalog.decode snapshot |> Result.toMaybe,open=True,query="Documents"}
launchRaw = E.object [("protocolVersion",E.int 3),("kind",E.string "application-launch-outcome"),("binding",bound),("outcome",launchReceipt)]
launchResult = Desktop.update (Desktop.Incoming launchRaw) launchBefore
launchAfter = Tuple.first launchResult
launchMessage = Attention.observe launchBefore launchAfter Attention.initial

rootDesktop root = Controller.desktop (Outputs.controller root)
step message root = Outputs.update (Outputs.Interaction message) root |> Tuple.first
native raw root = step (Desktop.Incoming raw) root
scoped make root = Desktop.capture (rootDesktop root) |> Maybe.map (\stamp -> step (make stamp) root) |> Maybe.withDefault root
scope id = E.object [("id",E.string id),("generation",E.string "1")]
topology ids revision = E.object [("viewProtocol",E.int 1),("kind",E.string "view-topology"),("revision",E.string revision),("views",E.list scope ids)]
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
-- Replay arrangement: the production admission gate requires native idle.
pointerIdle = E.object [("protocolVersion",E.int 3),("kind",E.string "pointer-ownership"),("ownershipProtocol",E.int 1),("binding",bound),("requestId",E.string "1"),("serial",E.string "1"),("state",E.string "idle"),("owner",E.null)]
openedRoot = Outputs.update (Outputs.Topology (topology ["1","2"] "1")) Outputs.initial |> Tuple.first |> native attached |> native pointerIdle |> scoped Desktop.OpenSettings
settingsSnapshot = E.object [("schema",E.int 1),("revision",E.string "1"),("values",E.object [("theme",E.string "night"),("textScale",E.int 100)])]
settingsRead = E.object [("protocolVersion",E.int 3),("kind",E.string "shell-settings"),("binding",bound),("requestId",E.string ((rootDesktop openedRoot).settingsExpected |> Maybe.map UInt64.string |> Maybe.withDefault "0")),("snapshot",settingsSnapshot)]
settingsReady = native settingsRead openedRoot
settingsChanged = scoped (\stamp -> Desktop.EditSettings stamp {theme=Settings.Dawn,textScale=100,effectsOff=False,reducedTransparency=False}) settingsReady
settingsPending = scoped Desktop.SaveSettings settingsChanged
settingsReceipt request owner = E.object [("protocolVersion",E.int 3),("kind",E.string "shell-settings-outcome"),("binding",owner),("requestId",E.string (UInt64.string request)),("status",E.string "Refused"),("snapshot",E.null)]
pendingRequest = (rootDesktop settingsPending).settings.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero
settingsRefused = native (settingsReceipt pendingRequest bound) settingsPending
repeated = native (settingsReceipt pendingRequest bound) settingsRefused
secondPending = scoped Desktop.SaveSettings settingsRefused
secondRequest = (rootDesktop secondPending).settings.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero
secondRefused = native (settingsReceipt secondRequest bound) secondPending
retired = Outputs.update (Outputs.Topology (topology ["2"] "2")) secondRefused |> Tuple.first
annSequence root = D.decodeValue (D.at ["announcement","sequence"] UInt64.decoder) (Outputs.frame root) |> Result.withDefault UInt64.zero

transferResult =
    case binding of
        Nothing -> E.null
        Just owner ->
            let geometry=Fixture.geometryFor owner
                caps={effects=True,operations=["transfer-workspace"]}
                (pending,_,_)=Effects.beginGeometry caps geometry (Effects.TransferWorkspace {source="1",sourceGeneration=Fixture.counter "4",destination="2"}) one base.windows.shell.effects
                intent=pending.transaction |> Maybe.map .intent
                refused=intent |> Maybe.map (\i -> Effects.apply (E.object [("kind",E.string "receipt"),("effectProtocol",E.int 2),("intent",Effects.encodeIntent i),("status",E.string "Refused")]) pending |> (\(next,_,_)->next)) |> Maybe.withDefault pending
                replace effects = let windows=base.windows
                                      shell=windows.shell
                                  in {base|windows={windows|shell={shell|effects=effects}}}
            in Attention.encode (Attention.observe (replace pending) (replace refused) Attention.initial)

main = Platform.worker
    {init=\() ->
        let foreign=E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "2")]
            duplicateLaunch=Desktop.update (Desktop.Incoming launchRaw) launchAfter
            foreignSettings=native (settingsReceipt pendingRequest foreign) settingsPending
            beforeFrame=Outputs.frame settingsPending
            checks=[("launchMatchedRefusal",Launch.status launchAfter.launch=="Refused"),("launchRefusalPreservesQueryAndOpen",launchAfter.query==launchBefore.query && launchAfter.open),
                ("launchRefusalDoesNotRequestFocus",List.isEmpty (Tuple.second launchResult)),("launchRefusalCorrelated",sequence launchMessage==one),
                ("launchRepeatSilent",Tuple.first duplicateLaunch==launchAfter && List.isEmpty (Tuple.second duplicateLaunch) && Attention.observe launchAfter (Tuple.first duplicateLaunch) launchMessage==launchMessage),
                ("settingsMatchedPending",pendingRequest/=UInt64.zero),("rootSettingsRefusalAnnounced",annSequence settingsRefused==one),
                ("rootRepeatSilent",annSequence repeated==one),("newRequestSameWordsGetsNewSerial",annSequence secondRefused==Fixture.counter "2" && secondRequest/=pendingRequest),
                ("foreignSettingsRefusalIgnored",Outputs.frame foreignSettings==beforeFrame),("ownerRetirementDoesNotAllocateAnnouncement",annSequence retired==annSequence secondRefused),
                ("transferRefusalCorrelated",D.decodeValue (D.field "sequence" UInt64.decoder) transferResult==Ok one)]
        in ((),outgoing (E.object [("checks",E.object (List.map (\(name,passed)->(name,E.bool passed)) checks)),("settingsFrame",Outputs.frame settingsRefused),("secondFrame",Outputs.frame secondRefused),("retiredFrame",Outputs.frame retired),("launchMessage",Attention.encode launchMessage),("transferMessage",transferResult)]))
    ,update=\_ model -> (model,Cmd.none),subscriptions=\_->Sub.none}
