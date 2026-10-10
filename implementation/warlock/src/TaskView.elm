module TaskView exposing (Workspace, groups, groupsWith, activeWorkspace)

import Effects
import ActionProjection as Scene
import GeometryProjection
import Shell
import Taskbar
import WorkspaceInventory

type alias Workspace = { identity : String, active : Bool, windows : List Taskbar.Family }

-- Geometry supplies membership; the action projection supplies family identity
-- and action eligibility. Enumeration never grants live paint/input authority.
groups : Shell.Model -> Maybe (List Workspace)
groups shell =
    case (shell.effects.observed,shell.geometry) of
        (Just observed,Just geometry) ->
            let rows = Scene.windows observed.scene
                matching row = GeometryProjection.window row.incarnation geometry
                    |> Maybe.map (\g -> g.owner==row.owner && g.minimized==row.minimized)
                    |> Maybe.withDefault False
                focusedWorkspace = Scene.focused observed.scene
                    |> Maybe.andThen (\identity -> GeometryProjection.window identity geometry)
                    |> Maybe.andThen .workspace
                families = Taskbar.groups observed.scene |> List.concatMap .families
                positive workspace = not (String.isEmpty workspace) && not (String.startsWith "-" workspace) && workspace/="0"
                add family accumulated =
                    case membership family.root shell geometry of
                        Just workspace ->
                            if not (positive workspace) then accumulated else
                            if List.any (\g -> g.identity==workspace) accumulated then
                                List.map (\g -> if g.identity==workspace then {g | windows=g.windows++[family]} else g) accumulated
                            else accumulated++[{identity=workspace,active=focusedWorkspace==Just workspace,windows=[family]}]
                        Nothing -> accumulated
                -- Action and geometry revision counters have different owners.
                -- Join only display metadata under the same native authority;
                -- choosing a window still refreshes its current action grant.
                sameAuthority = shell.binding==Just geometry.binding
                    && observed.context.lifetime==geometry.context.lifetime
                    && observed.context.epoch==geometry.context.epoch
                    && observed.context.output==geometry.context.output
                    && Scene.focused observed.scene==geometry.focused
                    && List.length rows==List.length geometry.windows && List.all matching rows
            in if not sameAuthority then Nothing else
                Just (List.foldl add [] families |> List.sortWith (\a b -> compare (String.length a.identity,a.identity) (String.length b.identity,b.identity)))
        _ -> Nothing

activeWorkspace : Shell.Model -> Maybe String
activeWorkspace shell = groups shell |> Maybe.andThen (List.filter .active >> List.head) |> Maybe.map .identity

-- A native observation can race ahead of its transfer receipt. Preserve the
-- admitted source membership while the exact transfer remains Pending/Unknown.
membership root shell geometry =
    let pending = shell.effects.unresolved |> List.filter (\t -> t.intent.incarnation==root && t.intent.context.lifetime==geometry.context.lifetime && List.member t.status [Effects.Pending,Effects.Unknown]) |> List.head
    in case pending |> Maybe.map (.intent >> .operation) of
        Just (Effects.TransferWorkspace p) -> Just p.source
        _ -> GeometryProjection.window root geometry |> Maybe.andThen .workspace

-- Native inventory makes empty workspaces visible. Existing window membership
-- still supplies families; stale inventory cannot be joined to newer geometry.
groupsWith inventory shell =
    case inventory of
        Nothing -> groups shell
        Just snapshot ->
            case (groups shell,shell.geometry) of
                (Just populated,Just geometry) ->
                    if not (WorkspaceInventory.coherent snapshot geometry) then Nothing else
                    let current=snapshot.rows |> List.map (\row -> {identity=row.identity,active=snapshot.active==Just row.identity,windows=populated |> List.filter (\group -> group.identity==row.identity) |> List.concatMap .windows})
                        retained=populated |> List.filter (\group -> not (List.any (\row -> row.identity==group.identity) snapshot.rows)) |> List.map (\group -> {group | active=False})
                    in Just (current++retained |> List.sortWith (\a b -> compare (String.length a.identity,a.identity) (String.length b.identity,b.identity)))
                _ -> Nothing
