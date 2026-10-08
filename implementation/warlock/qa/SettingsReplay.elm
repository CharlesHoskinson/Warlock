port module SettingsReplay exposing (main)

import Desktop
import Settings
import Surface
import SurfaceRenderer
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64

port outgoing : E.Value -> Cmd msg
counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
native raw model = Desktop.update (Desktop.Incoming raw) model |> Tuple.first
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
snapshot revision theme scale = E.object [("schema",E.int 1),("revision",E.string revision),("values",E.object [("theme",E.string theme),("textScale",E.int scale)])]
loaded request value = E.object [("protocolVersion",E.int 3),("kind",E.string "shell-settings"),("binding",bound),("requestId",E.string (UInt64.string request)),("snapshot",value)]
outcome request status value = E.object [("protocolVersion",E.int 3),("kind",E.string "shell-settings-outcome"),("binding",bound),("requestId",E.string (UInt64.string request)),("status",E.string status),("snapshot",value)]
dispatch build model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (build stamp) model) |> Maybe.withDefault (model,[])
result =
    let attachedModel=native attached Desktop.initial
        ready=native (loaded (counter "2") (snapshot "1" "night" 100)) attachedModel
        (opened,_)=dispatch Desktop.OpenSettings ready
        current=opened.settingsExpected |> Maybe.withDefault UInt64.zero
        (read,readEffects)=Desktop.update (Desktop.Incoming (loaded current (snapshot "1" "night" 100))) opened
        (edited,_)=dispatch (\stamp -> Desktop.EditSettings stamp {theme=Settings.Dawn,textScale=150}) read
        (saving,effects)=dispatch Desktop.SaveSettings edited
        request=saving.settings.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero
        (twice,duplicate)=dispatch Desktop.SaveSettings saving
        wrong=native (outcome (counter "99") "Saved" (snapshot "2" "dawn" 150)) saving
        mismatch=native (outcome request "Saved" (snapshot "2" "night" 150)) saving
        committed=native (outcome request "Saved" (snapshot "2" "dawn" 150)) saving
        repeated=native (outcome request "Saved" (snapshot "2" "dawn" 150)) committed
        unknown=native (outcome request "Unknown" E.null) saving
        (_,noReplay)=dispatch Desktop.SaveSettings unknown
        (rereading,readCommands)=dispatch Desktop.RefreshSettings unknown
        unknownRead=native (loaded (rereading.settingsExpected |> Maybe.withDefault UInt64.zero) (snapshot "2" "dawn" 150)) rereading
        (refreshing,_)=dispatch Desktop.RefreshSettings committed
        (_,ordinaryReadEffects)=Desktop.update (Desktop.Incoming (loaded (refreshing.settingsExpected |> Maybe.withDefault UInt64.zero) (snapshot "2" "dawn" 150))) refreshing
        restarted=native (loaded (counter "2") (snapshot "2" "dawn" 150)) (native attached Desktop.initial)
        (invalid,invalidEffects)=dispatch (\stamp -> Desktop.EditSettings stamp {theme=Settings.Dawn,textScale=77}) read
        stale=case Desktop.capture read of
            Just stamp -> Desktop.update (Desktop.EditSettings stamp {theme=Settings.Night,textScale=200}) edited |> Tuple.first
            Nothing -> edited
        frame=Surface.packet (counter "1") (counter "1") read
        savedFrame=Surface.packet (counter "2") (counter "1") committed
        checked name value=(name,E.bool value)
        appearance model=model.settings.snapshot |> Maybe.map .values
        write effect=case effect of
            Desktop.Send wire -> D.decodeValue (D.field "kind" D.string) wire==Ok "shell-settings-write"
            _ -> False
        checks=[checked "openingReadFocusUsesCurrentControl" (List.any (\effect -> case effect of
                Desktop.Focus target -> Surface.controls read |> List.any (\control -> control.id=="control:close" && control.enabled && control.domId==target)
                _ -> False) readEffects)
            ,checked "settingsOpenerIsIntegrated" (D.decodeValue (D.field "bar" (D.list (D.field "id" D.string))) frame |> Result.map (List.member "bar:settings") |> Result.withDefault False)
            ,checked "settingsFrameAcceptedByRenderer" (SurfaceRenderer.decode frame |> Result.map (SurfaceRenderer.mode >> (==) "settings") |> Result.withDefault False)
            ,checked "draftDoesNotApplyAppearance" (appearance edited==Just Settings.defaults)
            ,checked "oneExplicitWrite" (List.length (List.filter write effects)==1)
            ,checked "pendingWriteCannotRepeat" (twice==saving && List.isEmpty duplicate)
            ,checked "wrongReceiptCannotApply" (wrong==saving)
            ,checked "sameRequestWrongValuesCannotApply" (appearance mismatch==Just Settings.defaults && mismatch.settings.pending/=Nothing)
            ,checked "exactSavedValuesApply" (appearance committed==Just {theme=Settings.Dawn,textScale=150} && committed.settings.pending==Nothing)
            ,checked "duplicateReceiptIsInert" (repeated==committed)
            ,checked "unknownRetainsNoReplay" (unknown.settings.pending/=Nothing && List.isEmpty noReplay && appearance unknown==Just Settings.defaults)
            ,checked "explicitReadReconcilesUnknown" (unknownRead.settings.pending==Nothing && appearance unknownRead==Just {theme=Settings.Dawn,textScale=150})
            ,checked "ordinaryRefreshDoesNotMoveFocus" (List.isEmpty ordinaryReadEffects)
            ,checked "unknownRefreshOnlyReads" (List.length readCommands==1 && not (List.any write readCommands))
            ,checked "restartUsesStoredValues" (appearance restarted==Just {theme=Settings.Dawn,textScale=150})
            ,checked "invalidScaleCannotEditOrApply" (invalid.settings==read.settings && List.isEmpty invalidEffects)
            ,checked "invalidScaleDecoderRejects" (D.decodeValue Settings.decoder (snapshot "2" "dawn" 77) |> Result.toMaybe |> (==) Nothing)
            ,checked "staleViewCannotEdit" (stale==edited)
            ,checked "allSettingsHaveNames" (List.all (\c -> not (String.isEmpty c.ariaLabel)) (Surface.controls read))]
    in E.object [("checks",E.object checks),("frame",frame),("savedFrame",savedFrame)]
main = Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
