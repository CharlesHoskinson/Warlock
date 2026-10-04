module NativeProvider exposing (Scope, fromShell)

{-| Publish supported window capabilities from the same admitted native facts
used by the existing Shell effect engine. The caller supplies real presentation
output and registered provider identities; output generation is not an output ID.
This does not authenticate transport or infer unsupported native operations.
-}

import ActionProjection
import GeometryProjection
import Binding
import Json.Decode as D
import Json.Encode as E
import Provider
import Shell
import UInt64 exposing (Counter)

type alias Scope =
    { outputId : Counter, providerId : Counter, capabilityGeneration : Counter }

counter : Counter -> E.Value
counter = UInt64.string >> E.string

legacyFromShell : Scope -> Counter -> Shell.Model -> Result String Provider.Snapshot
legacyFromShell scope incarnation shell =
    if scope.outputId == UInt64.zero || scope.providerId == UInt64.zero || scope.capabilityGeneration == UInt64.zero then
        Err "Missing registered provider/output identity"
    else if shell.phase /= Shell.Ready then
        Err "Native window facts are not ready"
    else
        case (shell.binding,shell.effects.observed) of
            (Just binding,Just observed) ->
                if not (Binding.matchesContext observed.context.lifetime observed.context.epoch binding) then
                    Err "Native observation binding mismatch"
                else
                    case ActionProjection.rootOf incarnation observed.scene
                        |> Maybe.andThen (\root -> List.filter (\window -> window.incarnation == root) (ActionProjection.windows observed.scene) |> List.head) of
                        Nothing -> Err "Native window no longer exists"
                        Just window ->
                            let
                                positive name = D.field name UInt64.decoder
                                identities = D.decodeValue (D.map3 (\life session frontend -> (life,session,frontend)) (positive "lifetime") (positive "session") (positive "frontend")) (Binding.encode binding)
                                item id label enabled kind = E.object
                                    [("id",E.string id),("label",E.string label),("enabled",E.bool enabled)
                                    ,("action",E.object [("kind",E.string kind)])]
                            in
                            case identities of
                                Err _ -> Err "Invalid native identity"
                                Ok (lifetime,session,frontend) ->
                                    Provider.decode (E.object
                                        [("protocolVersion",E.int 1)
                                        ,("providerId",counter scope.providerId)
                                        ,("capabilityGeneration",counter scope.capabilityGeneration)
                                        ,("binding",E.object
                                            [("lifetime",counter lifetime),("session",counter session)
                                            ,("frontend",counter frontend),("revision",counter observed.context.revision)
                                            ,("outputId",counter scope.outputId),("outputGeneration",counter observed.context.output)])
                                        ,("target",E.object [("lifetime",counter lifetime),("session",counter session),("incarnation",counter window.incarnation)])
                                        ,("title",E.string (if String.trim window.label == "" then "Window actions" else window.label))
                                        ,("capabilities",E.list E.string ["Restore","Minimize"])
                                        ,("items",E.list identity
                                            [item "1" "Restore" (window.available && window.minimized) "Restore"
                                            ,item "2" "Minimize" (window.available && not window.minimized) "Minimize"])
                                        ])
            _ -> Err "No admitted native window observation"

fromShell : Scope -> Counter -> Shell.Model -> Result String Provider.Snapshot
fromShell scope incarnation shell =
    legacyFromShell scope incarnation shell |> Result.andThen (\legacy ->
        case shell.geometryCaps of
            Nothing -> Ok legacy
            Just caps ->
                if not caps.effects then Maybe.withDefault (Ok legacy) (Maybe.map (\observed -> Provider.withGeometry {effects=True,operations=["maximize","restore-geometry"]} observed legacy) shell.geometry) else
                case (shell.geometry,shell.geometryExpected,shell.effects.observed) of
                    (Just observed,Nothing,Just legacyObserved) ->
                        let root=Provider.incarnation legacy
                            legacyMinimized=ActionProjection.minimized root legacyObserved.scene
                            geometryMinimized=GeometryProjection.window root observed |> Maybe.map .minimized
                        in if legacyMinimized/=geometryMinimized then Err "Independent geometry/legacy facts disagree" else Provider.withGeometry caps observed legacy
                    _ -> Err "Geometry facts are awaiting fresh observation")
