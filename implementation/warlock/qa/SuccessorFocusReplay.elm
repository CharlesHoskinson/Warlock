port module SuccessorFocusReplay exposing (main)

{- Deterministic synthetic reducer and renderer guard source. No native focus,
   accessibility observation, adapter authority or physical mutation is implied. -}
import Binding
import Desktop
import Json.Decode as D
import Json.Encode as E
import NativePointerFixture
import Platform
import Presentation
import Surface
import SurfaceRenderer
import SystemMenu
import UInt64

port outgoing : E.Value -> Cmd msg

counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
binding = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",binding)]
snapshot = E.object [("service",E.string "9"),("revision",E.string "1"),("volume",E.object [("percent",E.int 100),("muted",E.bool False),("label",E.string "Warlock private audio")]),("network",E.null),("power",E.object [("suspend",E.string "yes"),("reboot",E.string "yes"),("poweroff",E.string "no")]),("session",E.object [("name",E.string "Warlock private session"),("state",E.string "active"),("locked",E.bool False)])]
loaded request = E.object [("protocolVersion",E.int 3),("kind",E.string "system-menu-snapshot"),("binding",binding),("requestId",E.string (UInt64.string request)),("snapshot",snapshot)]
apply build model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (build stamp) model) |> Maybe.withDefault (model,[])
focus effects = List.filterMap (\item -> case item of
    Desktop.Focus target -> Just target
    _ -> Nothing) effects
systemEffect effects = List.any (\item -> case item of
    Desktop.Send wire -> D.decodeValue (D.field "kind" D.string) wire==Ok "system-menu-effect"
    _ -> False) effects
check name ok = (name,E.bool ok)
frame model = Surface.packet (counter "1") (counter "1") model
focusPacket target publication lease surface = E.object [("focusProtocol",E.int 1),("kind",E.string "focus"),("surface",E.string surface),("publication",E.string publication),("lease",E.string lease),("domId",E.string target)]
eligible id model = Surface.controls model |> List.filter (\row -> row.id==id && row.enabled) |> List.map .domId

result =
    let ready = NativePointerFixture.incoming attached Desktop.initial |> Tuple.first
        (opened,_) = apply Desktop.OpenSystemMenu ready
        request = opened.systemMenuExpected |> Maybe.withDefault UInt64.zero
        (shown,_) = Desktop.update (Desktop.Incoming (loaded request)) opened
        parsed = D.decodeValue SystemMenu.decoder snapshot
    in case parsed of
        Err _ -> E.object [("fixtureError",E.string "snapshot"),("checks",E.object [("fixture-snapshot-decode",E.bool False)])]
        Ok current ->
            let restart = SystemMenu.intent current SystemMenu.Reboot 0
                network = SystemMenu.intent current SystemMenu.Network 0
                (refusedNetwork,networkEffects) = apply (\stamp -> Desktop.SystemChange stamp network) shown
                (prompt,promptEffects) = apply (\stamp -> Desktop.SystemChange stamp restart) refusedNetwork
                (cancelled,cancelEffects) = apply Desktop.CancelSystemChange prompt
                (closed,closeEffects) = apply Desktop.CloseSystemMenu cancelled
                stale = Desktop.capture shown |> Maybe.map (\stamp -> Desktop.update (Desktop.CancelSystemChange stamp) prompt) |> Maybe.withDefault (prompt,[])
                (afterStale,afterStaleEffects) = apply Desktop.CancelSystemChange (Tuple.first stale)
                (repeatCancel,repeatEffects) = apply Desktop.CancelSystemChange cancelled
                foreign = D.decodeValue Binding.decoder (E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "2")]) |> Result.toMaybe
                win=prompt.windows
                sh=win.shell
                foreignModel={prompt | windows={win | shell={sh | binding=foreign}}}
                foreignAttempt=Desktop.capture prompt |> Maybe.map (\stamp -> Desktop.update (Desktop.CancelSystemChange stamp) foreignModel) |> Maybe.withDefault (foreignModel,[])
                maxModel={prompt | presentation=Just (counter "18446744073709551615")}
                (exhausted,exhaustedEffects)=apply Desktop.CancelSystemChange maxModel
                expectedCancel="applications:{\"lifetime\":\"1\",\"session\":\"1\",\"frontend\":\"1\"}:5:system:cancel"
                expectedClose="applications:{\"lifetime\":\"1\",\"session\":\"1\",\"frontend\":\"1\"}:6:system:close"
                expectedOpener="applications:{\"lifetime\":\"1\",\"session\":\"1\",\"frontend\":\"1\"}:7:system:opener"
                presentation=Presentation.accept (frame prompt) Presentation.initial
                rendererChecks=case SurfaceRenderer.decode (frame prompt) of
                    Err _ -> False
                    Ok view -> SurfaceRenderer.mode view=="system" && Presentation.focusTarget True (focusPacket expectedCancel "1" "1" "popup") presentation==Just expectedCancel && Presentation.focusTarget True (focusPacket expectedCancel "1" "2" "popup") presentation==Nothing && Presentation.focusTarget True (focusPacket expectedCancel "1" "1" "bar") presentation==Nothing && Presentation.focusTarget True (focusPacket "foreign" "1" "1" "popup") presentation==Nothing && Presentation.focusTarget True (focusPacket expectedCancel "1" "1" "popup") presentation==Just expectedCancel
                controls=Surface.controls shown
                checks =
                    [check "opened-current-available-snapshot" (opened.systemMenuExpected/=Nothing && shown.systemMenuOpen && shown.systemMenu.snapshot==Just current && shown.systemMenuExpected==Nothing)
                    ,check "unavailable-network-refused-no-send" (List.any (\row -> row.id=="system:network:state" && row.label=="Network unavailable" && not row.enabled && row.message==Nothing) controls && refusedNetwork==shown && List.isEmpty networkEffects)
                    ,check "remaining-observed-state" (List.any (\row -> String.startsWith "Volume 100%" row.label) controls && List.any (\row -> String.startsWith "Session Warlock private session" row.label) controls && List.any (\row -> row.id=="system:reboot:0" && row.enabled) controls)
                    ,check "prompt-focus-matches-literal-successor-and-enabled-row" (promptEffects==[Desktop.Focus expectedCancel] && focus promptEffects==[expectedCancel] && eligible "system:cancel" prompt==[expectedCancel] && Desktop.key shown "system:cancel"/=expectedCancel && not (systemEffect promptEffects))
                    ,check "cancel-focus-matches-literal-successor-and-enabled-row" (cancelEffects==[Desktop.Focus expectedClose] && focus cancelEffects==[expectedClose] && eligible "control:close" cancelled==[expectedClose] && Desktop.key prompt "system:close"/=expectedClose && not (systemEffect cancelEffects))
                    ,check "stale-refused-then-valid-cancel" (Tuple.first stale==prompt && List.isEmpty (Tuple.second stale) && afterStale==cancelled && focus afterStaleEffects==[expectedClose])
                    ,check "duplicate-cancel-stutters" (repeatCancel==cancelled && List.isEmpty repeatEffects)
                    ,check "foreign-binding-old-stamp-refused" (foreign/=Nothing && Tuple.first foreignAttempt==foreignModel && List.isEmpty (Tuple.second foreignAttempt))
                    ,check "exhaustion-emits-no-focus" (exhausted.presentation==Nothing && List.isEmpty (focus exhaustedEffects))
                    ,check "close-requests-current-system-opener" (not closed.systemMenuOpen && focus closeEffects==[expectedOpener] && Desktop.key closed "system:opener"==expectedOpener && not (systemEffect closeEffects))
                    ,check "renderer-rejects-foreign-and-stale-then-valid" rendererChecks]
            in E.object [("requirements",E.list E.string ["ELM-UI-011","ELM-UX-024","ELM-UX-032"]),("scope",E.string "synthetic reducer and frame only; no native or AT focus"),("checks",E.object checks)]
main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
