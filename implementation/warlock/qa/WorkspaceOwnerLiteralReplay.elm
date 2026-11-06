port module WorkspaceOwnerLiteralReplay exposing (main)

{- Synthetic replay of the public owner route. It asserts data and effects,
   not host issuance, keyboard input, accessibility focus or native outcomes. -}
import Desktop
import DesktopPolicy as Policy
import Json.Decode as D
import Json.Encode as E
import OutputController as Outputs
import OutputRetirementReplay as Fixture
import Platform
import Shell
import Surface
import SurfaceController as Controller
import UInt64
import Switcher

port outgoing : E.Value -> Cmd msg

field name model = D.decodeValue (D.at ["frame",name] D.string) (Outputs.frame model) |> Result.withDefault "0"
scope id generation = E.object [("id",E.string id),("generation",E.string generation)]
action owner generation shown token id trigger = E.object
    [("viewProtocol",E.int 1),("kind",E.string "view-action"),("scope",scope owner generation)
    ,("action",E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string "popup"),("publication",E.string shown),("lease",E.string token),("id",E.string id),("trigger",E.string trigger)])]
bridge payload = E.object [("bridgeProtocol",E.int 1),("kind",E.string "view-action"),("payload",payload)]
escape owner generation shown token = E.object [("scope",scope owner generation),("publication",E.string shown),("lease",E.string token)]
mutations effects = effects |> List.filterMap (\effect -> case effect of
    Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> D.decodeValue (D.field "kind" D.string) wire |> Result.toMaybe
    Controller.DesktopEffect (Desktop.Send wire) -> D.decodeValue (D.field "kind" D.string) wire |> Result.toMaybe
    _ -> Nothing) |> List.filter (\kind -> List.member kind ["window-effect","workspace-navigation","application-launch","taskbar-pins-write"])

result =
    let
        ready=Fixture.base [("1",Fixture.left)]
        (opened,openEffects)=Desktop.capture (Fixture.desktop ready) |> Maybe.map (\stamp -> Outputs.update (Outputs.Interaction (Desktop.OpenOverview stamp)) ready) |> Maybe.withDefault (ready,[])
        publication=field "publication" opened
        token=field "lease" opened
        rows=Surface.controls (Fixture.desktop opened) |> List.filter (\c -> List.member c.id ["overview:workspace-create","overview:workspace-delete","overview:workspace-rename"])
        summary=List.map (\c -> (c.id,c.ariaLabel,(c.detail,c.enabled,c.message==Nothing))) rows
        expected=[("overview:workspace-create","Create workspace; unavailable",("Not supported by the workspace adapter",False,True)),("overview:workspace-delete","Delete workspace; unavailable",("Not supported by the workspace adapter",False,True)),("overview:workspace-rename","Rename workspace; unavailable",("Not supported by the workspace adapter",False,True))]
        (create,createEffects)=Outputs.update (Outputs.Renderer (action "1" "1" publication token "overview:workspace-create" "keyboard")) opened
        (delete,deleteEffects)=Outputs.update (Outputs.Renderer (action "1" "1" publication token "overview:workspace-delete" "pointer")) create
        (rename,renameEffects)=Outputs.update (Outputs.Renderer (action "1" "1" publication token "overview:workspace-rename" "keyboard")) delete
        (foreign,foreignEffects)=Outputs.update (Outputs.Renderer (action "2" "1" publication token "overview:workspace-create" "keyboard")) rename
        (replacement,replacementEffects)=Outputs.update (Outputs.Renderer (action "1" "2" publication token "overview:workspace-create" "keyboard")) foreign
        (stale,staleEffects)=Outputs.update (Outputs.Renderer (action "1" "1" "0" token "overview:workspace-create" "keyboard")) replacement
        (foreignClose,foreignCloseEffects)=Outputs.update (Outputs.Renderer (action "2" "1" publication token "control:close" "keyboard")) stale
        (replacementClose,replacementCloseEffects)=Outputs.update (Outputs.Renderer (action "1" "2" publication token "control:close" "keyboard")) foreignClose
        (staleClose,staleCloseEffects)=Outputs.update (Outputs.Renderer (action "1" "1" "0" token "control:close" "keyboard")) replacementClose
        (validClose,validCloseEffects)=Outputs.update (Outputs.Renderer (action "1" "1" publication token "control:close" "keyboard")) staleClose
        (duplicateClose,duplicateCloseEffects)=Outputs.update (Outputs.Renderer (action "1" "1" publication token "control:close" "keyboard")) validClose
        policyGiven={controller=opened}
        (policyForeign,policyForeignEffects)=Policy.update (Policy.Incoming (bridge (action "2" "1" publication token "control:close" "keyboard"))) policyGiven
        (policyReplacement,policyReplacementEffects)=Policy.update (Policy.Incoming (bridge (action "1" "2" publication token "control:close" "keyboard"))) policyForeign
        (policyStale,policyStaleEffects)=Policy.update (Policy.Incoming (bridge (action "1" "1" "0" token "control:close" "keyboard"))) policyReplacement
        (closed,closeEffects)=Outputs.update (Outputs.Escape (escape "1" "1" publication token)) stale
        (duplicate,duplicateEffects)=Outputs.update (Outputs.Escape (escape "1" "1" publication token)) closed
        (empty,emptyEffects)=Outputs.update (Outputs.Topology (Fixture.topology "2" [])) opened
        (retiredAction,retiredEffects)=Outputs.update (Outputs.Renderer (action "1" "1" publication token "overview:workspace-create" "keyboard")) empty
        (returned,returnEffects)=Outputs.update (Outputs.Topology (Fixture.topology "3" [("2",Fixture.right)])) retiredAction
        (oldOwner,oldOwnerEffects)=Outputs.update (Outputs.Renderer (action "1" "1" publication token "overview:workspace-create" "keyboard")) returned
        (registeredEmpty,emptyCommand)=Outputs.register retiredEffects retiredAction
        -- Explicit literals are derived from Fixture.base and the frozen policy.
        zero = UInt64.zero
        one = UInt64.next zero |> Maybe.withDefault zero
        two = UInt64.next one |> Maybe.withDefault zero
        three = UInt64.next two |> Maybe.withDefault zero
        four = UInt64.next three |> Maybe.withDefault zero
        five = UInt64.next four |> Maybe.withDefault zero
        readyDesktop=Fixture.desktop ready
        readyWindows=readyDesktop.windows
        readyShell=readyWindows.shell
        expectedOpened={readyDesktop | overview=True,presentation=Just four,expected=Nothing}
        expectedShell={readyShell | request=two,expected=Just two,phase=Shell.Reconciling,projectionRetryQueued=False}
        expectedWindows={readyWindows | shell=expectedShell}
        expectedClosed={expectedOpened | overview=False,presentation=Just five,returnFocus=Nothing,windows=expectedWindows}
        observedClosed=Fixture.desktop closed
        normalizedClosed={observedClosed | returnFocus=Nothing}
        expectedTarget=E.object [("binding",E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]),("destination",E.string "overview-opener"),("output",E.string "1")]
        openFocus="applications:{\"lifetime\":\"1\",\"session\":\"1\",\"frontend\":\"1\"}:4:overview:all"
        closeFocus="applications:{\"lifetime\":\"1\",\"session\":\"1\",\"frontend\":\"1\"}:5:control:overview-opener"
        effectName effect=case effect of
            Controller.Publish _ -> "publish"
            Controller.DesktopEffect (Desktop.Focus target) -> "focus:"++target
            Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send raw)) -> D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault "invalid"
            _ -> "other"
        replaceField name value raw=D.decodeValue (D.keyValuePairs D.value) raw |> Result.map (List.map (\(key,old) -> (key,if key==name then value else old)) >> E.object) |> Result.withDefault raw
        refreshedProjection=replaceField "requestId" (E.string "2") Fixture.projection
        (returnedFocus,returnFocusEffects)=Outputs.update (Outputs.Interaction (Desktop.Incoming refreshedProjection)) closed
        (duplicateRead,duplicateReadEffects)=Outputs.update (Outputs.Interaction (Desktop.Incoming refreshedProjection)) returnedFocus
        (registeredOpen,openPacket)=Outputs.register openEffects opened
        (registeredClose,closePacket)=Outputs.register closeEffects closed
        openPacketFocus=openPacket |> Maybe.andThen (D.decodeValue (D.field "focus" (D.list D.string)) >> Result.toMaybe)
        openPacketRequests=openPacket |> Maybe.andThen (D.decodeValue (D.field "requests" (D.list D.value)) >> Result.toMaybe)
        closePacketRequests=closePacket |> Maybe.andThen (D.decodeValue (D.field "requests" (D.list D.value)) >> Result.toMaybe) |> Maybe.withDefault []
        closeRequest=E.object [("protocolVersion",E.int 3),("kind",E.string "projection-request"),("binding",Fixture.bound),("requestId",E.string "2")]
        checks=
            [ ("literalFixturePreconditions",readyDesktop.presentation==Just three && readyDesktop.expected==Just one && readyShell.request==one && readyDesktop.switcher==Switcher.initial && readyDesktop.returnFocus==Nothing && readyDesktop.overview==False)
            , ("completeOpenedDesktopMatchesBaselinePlusLiteralChanges",Fixture.desktop opened==expectedOpened)
            , ("orderedOpenEffectsArePublishThenLiteralFocus",List.map effectName openEffects==["publish","focus:"++openFocus])
            , ("completeClosedDesktopExceptOpaqueReturnFocus",normalizedClosed==expectedClosed && E.encode 0 (Desktop.testObserveReturnFocus observedClosed)==E.encode 0 expectedTarget)
            , ("orderedCloseEffectsArePublishThenOneRead",List.map effectName closeEffects==["publish","projection-request"])
            , ("registeredOpenHasExactFocusAndNoRequests",openPacketFocus==Just [openFocus] && (openPacketRequests |> Maybe.map List.isEmpty |> Maybe.withDefault False) && Outputs.pendingBatches registeredOpen==Outputs.pendingBatches opened)
            , ("registeredCloseHasExactReadAndNoMutation",List.map (E.encode 0) closePacketRequests==[E.encode 0 closeRequest] && Outputs.pendingBatches registeredClose==1)
            , ("matchedReadReturnsExactOriginalOpener",List.map effectName returnFocusEffects==["publish","focus:"++closeFocus] && E.encode 0 (Desktop.testObserveReturnFocus (Fixture.desktop returnedFocus))=="null")
            , ("duplicateReadCannotRepeatFocus",duplicateRead==returnedFocus && List.isEmpty duplicateReadEffects)
            , ("overviewOwnerAndLiteralUnsupportedControls",(Fixture.desktop opened).overview && Fixture.owner opened==Just "1" && summary==expected)
            , ("keyboardAndPointerUnsupportedCallbacksStutter",create==opened && delete==opened && rename==opened && List.isEmpty createEffects && List.isEmpty deleteEffects && List.isEmpty renameEffects)
            , ("foreignReplacementAndStaleCallbacksStutter",foreign==opened && replacement==opened && stale==opened && List.isEmpty foreignEffects && List.isEmpty replacementEffects && List.isEmpty staleEffects)
            , ("foreignEnabledCloseCannotDismiss",foreignClose==opened && List.isEmpty foreignCloseEffects)
            , ("replacementEnabledCloseCannotDismiss",replacementClose==opened && List.isEmpty replacementCloseEffects)
            , ("staleEnabledCloseCannotDismiss",staleClose==opened && List.isEmpty staleCloseEffects)
            , ("validEnabledCloseAfterRefusalsWorks",not (Fixture.desktop validClose).overview && List.isEmpty (mutations validCloseEffects))
            , ("duplicateEnabledCloseCannotReapply",duplicateClose==validClose && List.isEmpty duplicateCloseEffects)
            , ("policyRejectsInvalidScopesWithoutEffects",policyForeign==policyGiven && policyReplacement==policyGiven && policyStale==policyGiven && List.isEmpty policyForeignEffects && List.isEmpty policyReplacementEffects && List.isEmpty policyStaleEffects)
            , ("validEscapeAfterRefusalsClosesWithoutMutation",not (Fixture.desktop closed).overview && List.isEmpty (mutations (openEffects++closeEffects)))
            , ("zeroOutputRetiresUnsupportedOwner",Fixture.owner empty==Nothing && not (Fixture.desktop empty).overview && retiredAction==empty && List.isEmpty retiredEffects)
            , ("returnedOutputRejectsRetiredOwner",Fixture.owner returned==Just "2" && oldOwner==returned && List.isEmpty oldOwnerEffects)
            , ("noOpEffectsDoNotRegisterCommand",registeredEmpty==retiredAction && emptyCommand==Nothing)
            , ("topologyTransitionsDoNotMutateWorkspace",List.isEmpty (mutations (emptyEffects++returnEffects)))
            , ("duplicateEscapeIsInert",duplicate==closed && List.isEmpty duplicateEffects)
            ]
    in E.object [("requirement",E.string "ELM-UI-006"),("scenario",E.string "workspace-management-unavailable"),("scope",E.string "synthetic owner callbacks; local control and dismissal only"),("checks",E.object (List.map (Tuple.mapSecond E.bool) checks)),("checkNames",E.list (Tuple.first >> E.string) checks)]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
