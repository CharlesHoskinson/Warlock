port module FilesReplay exposing (main)
import Desktop
import NativePointerFixture
import Files
import Surface
import SurfaceRenderer
import Presentation
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64
port outgoing : E.Value -> Cmd msg
counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
native raw model = NativePointerFixture.incoming raw model |> Tuple.first
snapshot revision target = E.object [("service",E.string "9"),("revision",E.string revision),("available",E.bool True),("reason",E.string ""),("peer",E.object [("pid",E.string "20"),("start",E.string "40"),("instance",E.string "owned1"),("target",E.string target),("visible",E.bool True)])]
loaded request value = E.object [("protocolVersion",E.int 3),("kind",E.string "files-snapshot"),("binding",bound),("requestId",E.string (UInt64.string request)),("snapshot",value)]
outcome request status value = E.object [("protocolVersion",E.int 3),("kind",E.string "files-outcome"),("binding",bound),("requestId",E.string (UInt64.string request)),("status",E.string status),("snapshot",value)]
dispatch build model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (build stamp) model) |> Maybe.withDefault (model,[])
effect e = case e of
    Desktop.Send wire -> D.decodeValue (D.field "kind" D.string) wire==Ok "files-open"
    _ -> False
result =
    let attached=E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
        ready=native attached Desktop.initial
        (opening,_)=dispatch Desktop.OpenFiles ready
        read=native (loaded (opening.filesExpected |> Maybe.withDefault UInt64.zero) (snapshot "1" "home")) opening
        current=read.files.snapshot |> Maybe.withDefault {service=counter "9",revision=counter "1",available=False,reason="",peer=Nothing}
        target=Files.intent current "coll:images"
        (pending,effects)=dispatch (\stamp -> Desktop.OpenFilesTarget stamp target) read
        request=pending.files.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero
        opened=native (outcome request "Opened" (snapshot "2" "coll:images")) pending
        unknown=native (outcome request "Unknown" (snapshot "1" "home")) pending
        (unknownPopup,_)=dispatch Desktop.OpenFiles unknown
        (refreshed,refreshEffects)=dispatch Desktop.RefreshFiles unknownPopup
        reconciled=native (loaded (refreshed.filesExpected |> Maybe.withDefault UInt64.zero) (snapshot "2" "coll:images")) refreshed
        (_,repeat)=dispatch (\stamp -> Desktop.OpenFilesTarget stamp target) reconciled
        (_,unknownRepeat)=dispatch (\stamp -> Desktop.OpenFilesTarget stamp target) unknownPopup
        replaced=E.object [("service",E.string "9"),("revision",E.string "2"),("available",E.bool True),("reason",E.string ""),("peer",E.object [("pid",E.string "21"),("start",E.string "41"),("instance",E.string "replacement"),("target",E.string "coll:images"),("visible",E.bool True)])]
        wrongPeer=native (outcome request "Opened" replaced) pending
        wrongLocation=native (outcome request "Opened" (snapshot "2" "coll:videos")) pending
        disconnected=native (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")]) pending
        wrong=native (outcome (counter "999") "Opened" (snapshot "2" "coll:images")) pending
        (edited,editEffects)=dispatch (\stamp -> Desktop.EditFilesPath stamp "/tmp/Documents") read
        (folder,folderEffects)=dispatch Desktop.OpenFilesPath edited
        (invalid,_)=dispatch (\stamp -> Desktop.EditFilesPath stamp "$(touch injected)") read
        (_,invalidEffects)=dispatch Desktop.OpenFilesPath invalid
        (closed,closeEffects)=dispatch Desktop.CloseFiles read
        (other,_)=dispatch Desktop.OpenSystemMenu read
        frame=Surface.packet (counter "1") (counter "1") edited
        originalFrame=Surface.packet (counter "1") (counter "1") read
        presentation=Presentation.accept frame Presentation.initial
        field=E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-query"),("surface",E.string "popup"),("publication",E.string "1"),("lease",E.string "1"),("id",E.string "control:files-path"),("query",E.string "/tmp/Other")]
        resolved=Surface.resolve (counter "1") (counter "1") field edited
        typed=resolved |> Maybe.map (\message -> Desktop.update message edited) |> Maybe.withDefault (edited,[])
        checked name value=(name,E.bool value)
        checks=[checked "FilesOpenerIntegrated" (D.decodeValue (D.field "bar" (D.list (D.field "id" D.string))) originalFrame |> Result.map (List.member "bar:files") |> Result.withDefault False)
            ,checked "InstalledCollectionNamesPreserved" (List.all (\(identifier,_) -> List.any (\c -> c.id=="files:collection:"++identifier) (Surface.controls read)) Files.collections)
            ,checked "NativeModeAccepted" (SurfaceRenderer.decode frame |> Result.map (SurfaceRenderer.mode >> (==) "files") |> Result.withDefault False)
            ,checked "CurrentLocationDisplayed" (List.any (\c -> c.id=="files:location:state" && c.label=="Current location: home" && not c.enabled) (Surface.controls read))
            ,checked "ExactlyOneExplicitCollectionOpening" (List.length (List.filter effect effects)==1)
            ,checked "PopupClosesBeforeNativeOpening" (not pending.filesOpen && not (List.any (\e -> case e of
                Desktop.Focus _ -> True
                _ -> False) effects))
            ,checked "ObservedOutcomeSettles" (opened.files.pending==Nothing && String.contains "opened" opened.files.notice)
            ,checked "UnknownRemainsVisibleAndCannotReplay" (unknown.files.pending/=Nothing && String.contains "not confirmed" unknown.files.notice && List.isEmpty unknownRepeat)
            ,checked "RefreshNeverOpens" (not (List.any effect refreshEffects))
            ,checked "ChangedReadReconcilesWithoutReplay" (reconciled.files.pending==Nothing && List.isEmpty repeat)
            ,checked "ReplacementCannotBeReportedAsReused" (wrongPeer.files.pending/=Nothing && String.contains "not confirmed" wrongPeer.files.notice)
            ,checked "WrongLocationCannotBeReportedAsOpened" (wrongLocation.files.pending/=Nothing && String.contains "not confirmed" wrongLocation.files.notice)
            ,checked "ConnectionLossKeepsUnknownWithoutReplay" (not disconnected.filesOpen && disconnected.files.pending==Nothing && disconnected.files.snapshot==Nothing && String.contains "not confirmed" disconnected.files.notice)
            ,checked "WrongReceiptDoesNotSettle" (wrong==pending)
            ,checked "TypingHasNoEffect" (edited.files.draft=="/tmp/Documents" && List.isEmpty editEffects)
            ,checked "FolderRequiresExplicitAction" (List.length (List.filter effect folderEffects)==1 && folder.files.pending/=Nothing)
            ,checked "CommandTextDoesNotOpen" (List.isEmpty invalidEffects)
            ,checked "CloseHasNoNavigationEffect" (not closed.filesOpen && not (List.any effect closeEffects))
            ,checked "AnotherPopupRetiresFiles" (not other.filesOpen && other.systemMenuOpen && other.files==read.files)
            ,checked "FolderFieldHasScopedAcknowledgment" (Presentation.editQuery field presentation/=Nothing && (Tuple.first typed).files.draft=="/tmp/Other" && List.isEmpty (Tuple.second typed))
            ,checked "DetachedSessionRetiresFiles" (not (native (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected"),("binding",bound)]) read).filesOpen)
            ,checked "AllControlsNamed" (List.all (\c -> not (String.isEmpty c.ariaLabel)) (Surface.controls read))]
    in E.object [("checks",E.object checks),("frame",originalFrame),("pathFrame",frame),("pendingFrame",Surface.packet (counter "3") (counter "1") {read | files=pending.files})]
main = Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
