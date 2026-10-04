module WindowGeometry exposing (Action(..), Capabilities, Facts, Item, NativeMode(..), Resolution(..), authorize, exitFullscreen, items)

{-| Prototype policy for validated native facts. It does not advertise transport
support, infer native state from receipts, or allocate operation identities.

geometryEligible is the authority's semantic target eligibility (for example a
native root); it is not derived from labels, grouping, or this display policy.
-}


type NativeMode
    = Ordinary
    | Maximized
    | Fullscreen


type Resolution
    = Ready
    | Pending
    | Unknown


type Action
    = RestoreMinimized
    | RestoreGeometry
    | Move
    | Size
    | Minimize
    | Maximize
    | Close
    | ExitFullscreen


type alias Capabilities =
    { restoreMinimized : Bool
    , restoreGeometry : Bool
    , move : Bool
    , size : Bool
    , minimize : Bool
    , maximize : Bool
    , close : Bool
    , exitFullscreen : Bool
    }


type alias Facts =
    { mode : NativeMode
    , minimized : Bool
    , fixedSize : Bool
    , geometryEligible : Bool
    , resolution : Resolution
    , capabilities : Capabilities
    }


type alias Item =
    { label : String, action : Action, enabled : Bool }


row : Facts -> Bool -> Bool -> String -> Action -> Maybe Item
row facts supported enabled label action =
    if supported then
        Just { label = label, action = action, enabled = enabled && facts.resolution == Ready }

    else
        Nothing


items : Facts -> List Item
items facts =
    let
        caps =
            facts.capabilities

        ordinary =
            facts.mode == Ordinary && not facts.minimized

        restore =
            if facts.minimized then
                row facts caps.restoreMinimized True "Restore" RestoreMinimized

            else
                row facts caps.restoreGeometry (facts.geometryEligible && facts.mode == Maximized) "Restore" RestoreGeometry
    in
    List.filterMap identity
        [ restore
        , row facts caps.move (facts.geometryEligible && ordinary) "Move" Move
        , row facts caps.size (facts.geometryEligible && ordinary && not facts.fixedSize) "Size" Size
        , row facts caps.minimize (not facts.minimized) "Minimize" Minimize
        , row facts caps.maximize (facts.geometryEligible && ordinary && not facts.fixedSize) "Maximize" Maximize
        , row facts caps.close True "Close" Close
        ]


exitFullscreen : Facts -> Maybe Item
exitFullscreen facts =
    row facts facts.capabilities.exitFullscreen
        (facts.geometryEligible && facts.mode == Fullscreen && not facts.minimized)
        "Exit fullscreen"
        ExitFullscreen


authorize : Action -> Facts -> Bool
authorize action facts =
    (items facts ++ List.filterMap identity [ exitFullscreen facts ])
        |> List.any (\item -> item.action == action && item.enabled)
