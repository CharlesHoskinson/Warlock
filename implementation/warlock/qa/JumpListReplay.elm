port module JumpListReplay exposing (main)
import Desktop
import NativePointerFixture
import JumpList
import Surface
import SurfaceRenderer
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64
port outgoing : E.Value -> Cmd msg
counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
native raw model = NativePointerFixture.incoming raw model |> Tuple.first
row id label kind=E.object [("id",E.string id),("label",E.string label),("kind",E.string kind)]
snapshot revision entry=E.object [("service",E.string "9"),("revision",E.string revision),("entry",E.string entry),("name",E.string "Warlock Editor"),("available",E.bool True),("reason",E.string ""),("actions",E.list identity [row "desktop:Alpha" "New document" "desktop",row "desktop:Beta" "Private window" "desktop",row "recent:owned" "Open Warlock recent document" "recent"])]
loaded request value=E.object [("protocolVersion",E.int 3),("kind",E.string "jump-list-snapshot"),("binding",bound),("requestId",E.string (UInt64.string request)),("snapshot",value)]
outcome request status value=E.object [("protocolVersion",E.int 3),("kind",E.string "jump-list-outcome"),("binding",bound),("requestId",E.string (UInt64.string request)),("status",E.string status),("snapshot",value)]
dispatch build model=Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (build stamp) model) |> Maybe.withDefault (model,[])
effect e=case e of
    Desktop.Send wire -> D.decodeValue (D.field "kind" D.string) wire==Ok "jump-list-effect"
    _ -> False
result=
    let attached=E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
        ready=native attached Desktop.initial
        (applications,_)=dispatch Desktop.OpenApplications ready
        catalog=E.object [("catalogProtocol",E.int 2),("lifetime",E.string "8"),("generation",E.string "1"),("entries",E.list identity [E.object [("id",E.string "warlock-editor"),("name",E.string "Warlock Editor"),("iconHint",E.string "editor"),("wmclass",E.string "Editor"),("genericName",E.string "Text editor"),("keywords",E.list E.string [])]])]
        projected=native (E.object [("protocolVersion",E.int 3),("kind",E.string "application-catalog"),("binding",bound),("requestId",E.string (UInt64.string (applications.expected |> Maybe.withDefault UInt64.zero))),("snapshot",catalog)]) applications
        (opening,_)=dispatch (\stamp -> Desktop.OpenJumpList stamp "warlock-editor") projected
        read=native (loaded (opening.jumpExpected |> Maybe.withDefault UInt64.zero) (snapshot "1" "warlock-editor")) opening
        current=read.jumpList.snapshot |> Maybe.withDefault {service=counter "9",revision=counter "1",entry="warlock-editor",name="",available=False,reason="",actions=[]}
        target=JumpList.intent current "desktop:Alpha"
        (pending,effects)=dispatch (\stamp -> Desktop.JumpAction stamp target) read
        request=pending.jumpList.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero
        submitted=native (outcome request "Submitted" (snapshot "2" "warlock-editor")) pending
        unknown=native (outcome request "Unknown" (snapshot "1" "warlock-editor")) pending
        (unknownPopup,_)=dispatch (\stamp -> Desktop.OpenJumpList stamp "warlock-editor") unknown
        (_,repeat)=dispatch (\stamp -> Desktop.JumpAction stamp target) unknownPopup
        foreign=native (outcome request "Submitted" (snapshot "2" "foreign")) pending
        (_,unsupported)=dispatch (\stamp -> Desktop.JumpAction stamp (JumpList.intent current "desktop:Unsupported")) read
        (_,recentForeign)=dispatch (\stamp -> Desktop.JumpAction stamp (JumpList.intent current "recent:foreign")) read
        (recent,recentEffects)=dispatch (\stamp -> Desktop.JumpAction stamp (JumpList.intent current "recent:owned")) read
        (refreshing,refreshEffects)=dispatch Desktop.RefreshJumpList read
        wrongRead=native (loaded (refreshing.jumpExpected |> Maybe.withDefault UInt64.zero) (snapshot "2" "foreign")) refreshing
        (closed,closeEffects)=dispatch Desktop.CloseJumpList read
        (other,_)=dispatch Desktop.OpenSystemMenu read
        old=Desktop.capture read |> Maybe.map (\stamp -> Desktop.update (Desktop.JumpAction stamp target) submitted |> Tuple.second) |> Maybe.withDefault []
        frame=Surface.packet (counter "1") (counter "1") read
        check name value=(name,E.bool value)
        checks=[check "LauncherHasBoundedKeyboardJumpOpener" (List.any (\c -> c.id=="jump:open:warlock-editor") (Surface.controls projected))
            ,check "OriginalTwoDeclaredActionsShown" (List.all (\id -> List.any (\c -> c.id=="jump:action:"++id && c.enabled) (Surface.controls read)) ["desktop:Alpha","desktop:Beta"])
            ,check "UnsupportedActionsAbsent" (not (List.any (\c -> String.contains "Unsupported" c.label) (Surface.controls read)))
            ,check "OnlyOwnedRecentActionShown" (List.any (\c -> c.id=="jump:action:recent:owned") (Surface.controls read) && not (List.any (\c -> c.id=="jump:action:recent:foreign") (Surface.controls read)))
            ,check "ForeignRecentNeverDispatches" (List.isEmpty recentForeign)
            ,check "UnsupportedActionNeverDispatches" (List.isEmpty unsupported)
            ,check "OneExplicitDesktopAction" (List.length (List.filter effect effects)==1)
            ,check "OwnedRecentDispatchesOnce" (List.length (List.filter effect recentEffects)==1 && recent.jumpList.pending/=Nothing)
            ,check "PopupClosesBeforeLaunch" (pending.jumpEntry==Nothing)
            ,check "SubmissionNeverClaimsApplicationReady" (submitted.jumpList.pending==Nothing && String.contains "submitted" submitted.jumpList.notice)
            ,check "UnknownPersistsWithoutReplay" (unknown.jumpList.pending/=Nothing && String.contains "not confirmed" unknown.jumpList.notice && List.isEmpty repeat)
            ,check "ForeignApplicationCannotSettleReceipt" (foreign==pending)
            ,check "ForeignApplicationReadCannotReplaceOpenList" (wrongRead==refreshing)
            ,check "RefreshOnlyReads" (not (List.any effect refreshEffects))
            ,check "CloseReturnsToLauncherWithoutLaunch" (closed.open && closed.jumpEntry==Nothing && not (List.any effect closeEffects))
            ,check "OtherPopupRetiresList" (other.jumpEntry==Nothing && other.systemMenuOpen)
            ,check "StaleViewCannotSubmit" (List.isEmpty old)
            ,check "NativeRendererAcceptsJumpMode" (SurfaceRenderer.decode frame |> Result.map (SurfaceRenderer.mode >> (==) "jump") |> Result.withDefault False)
            ,check "AllActionsNamed" (List.all (\c -> not (String.isEmpty c.ariaLabel)) (Surface.controls read))]
    in E.object [("checks",E.object checks),("frame",frame),("pendingFrame",Surface.packet (counter "2") (counter "1") {read | jumpList=pending.jumpList}),("unknownFrame",Surface.packet (counter "3") (counter "1") {read | jumpList=unknown.jumpList})]
main=Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
