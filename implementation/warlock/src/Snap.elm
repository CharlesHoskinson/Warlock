module Snap exposing (Choice, Region(..), Proposal, regions, name, identity, open, valid, select, proposal)

import GeometryProjection as Geometry
import UInt64 exposing (Counter)

type Region = LeftHalf | RightHalf | TopLeft | TopRight | BottomLeft | BottomRight
type alias Choice = { snapshot : Geometry.Snapshot, target : Counter, selected : Region }
type alias Proposal =
    { region : String, geometry : List Float, monitor : Counter
    , outputOwnershipGeneration : Counter, workAreaRevision : Counter
    , workspaceGeneration : Counter, context : Geometry.Context }

regions : List Region
regions = [LeftHalf,RightHalf,TopLeft,TopRight,BottomLeft,BottomRight]

identity : Region -> String
identity region = case region of
    LeftHalf -> "left-half"
    RightHalf -> "right-half"
    TopLeft -> "top-left"
    TopRight -> "top-right"
    BottomLeft -> "bottom-left"
    BottomRight -> "bottom-right"

name : Region -> String
name region = case region of
    LeftHalf -> "Left half"
    RightHalf -> "Right half"
    TopLeft -> "Top left quarter"
    TopRight -> "Top right quarter"
    BottomLeft -> "Bottom left quarter"
    BottomRight -> "Bottom right quarter"

open : Geometry.Snapshot -> Counter -> Maybe Choice
open snapshot target =
    Geometry.window target snapshot |> Maybe.andThen (\window ->
        let choice={snapshot=snapshot,target=target,selected=LeftHalf}
        in if snapshot.blocked || not window.eligible || window.minimized
            || window.nativeMode/=Geometry.Ordinary || window.clientMode/=Geometry.Ordinary
            || proposal choice==Nothing then Nothing else Just choice)

valid : Geometry.Snapshot -> Choice -> Bool
valid current choice =
    current.binding==choice.snapshot.binding
        && current.context.lifetime==choice.snapshot.context.lifetime
        && current.context.epoch==choice.snapshot.context.epoch
        && current.context.output==choice.snapshot.context.output
        && (Geometry.window choice.target current |> Maybe.map (\window ->
            -- A live shell popup can block native geometry effects. Retain
            -- only its pure preview in an unchanged scope; opening still
            -- requires eligibility, and this module emits no native effect.
            (current.blocked || window.eligible) && not window.minimized
                && window.floating && not window.grouped && not window.fixedSize
                && window.owner==Nothing && window.nativeMode==Geometry.Ordinary
                && window.clientMode==Geometry.Ordinary
                && (Geometry.window choice.target choice.snapshot |> Maybe.map .sizePolicy)==Just window.sizePolicy
                && proposal {choice|snapshot=current}==(proposal choice |> Maybe.map (\prior -> {prior|context=current.context}))) |> Maybe.withDefault False)

select : Geometry.Snapshot -> Region -> Choice -> Maybe Choice
select current region choice = if valid current choice then Just {choice|selected=region} else Nothing

proposal : Choice -> Maybe Proposal
proposal choice = Geometry.window choice.target choice.snapshot |> Maybe.andThen (\window ->
    case ((window.workArea,window.monitor),(window.outputOwnershipGeneration,window.workAreaRevision,window.workspaceGeneration)) of
        ((Just [x,y,width,height],Just monitor),(Just output,Just area,Just workspace)) ->
            let half=width/2
                quarter=height/2
                geometry=case choice.selected of
                    LeftHalf -> [x,y,half,height]
                    RightHalf -> [x+half,y,width-half,height]
                    TopLeft -> [x,y,half,quarter]
                    TopRight -> [x+half,y,width-half,quarter]
                    BottomLeft -> [x,y+quarter,half,height-quarter]
                    BottomRight -> [x+half,y+quarter,width-half,height-quarter]
            in Just {region=identity choice.selected,geometry=geometry,monitor=monitor,
                outputOwnershipGeneration=output,workAreaRevision=area,workspaceGeneration=workspace,
                context=choice.snapshot.context}
        _ -> Nothing)
