module Snap exposing (Choice, Region(..), Proposal, regions, name, identity, open, valid, select, proposal, encodeProposal, proposalDecoder, matches)

import Json.Decode as D
import Json.Encode as E
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


encodeProposal : Proposal -> E.Value
encodeProposal proposed = E.object
    [("region",E.string proposed.region),("geometry",E.list E.float proposed.geometry)
    ,("monitor",E.string (UInt64.string proposed.monitor))
    ,("outputOwnershipGeneration",E.string (UInt64.string proposed.outputOwnershipGeneration))
    ,("workAreaRevision",E.string (UInt64.string proposed.workAreaRevision))
    ,("workspaceGeneration",E.string (UInt64.string proposed.workspaceGeneration))]

proposalDecoder : Geometry.Context -> D.Decoder Proposal
proposalDecoder context =
    let positive=UInt64.decoder |> D.andThen (\n -> if n==UInt64.zero then D.fail "Zero placement generation" else D.succeed n)
        region=D.string |> D.andThen (\value -> if List.any (identity >> (==) value) regions then D.succeed value else D.fail "Unsupported snap region")
        rectangle=D.list D.float |> D.andThen (\values -> case values of
            [x,y,w,h] -> if List.all (\n -> not (isNaN n || isInfinite n) && abs n<=2147483647) values && w>0 && h>0 then D.succeed values else D.fail "Invalid snap rectangle"
            _ -> D.fail "Invalid snap rectangle shape")
        fields=["region","geometry","monitor","outputOwnershipGeneration","workAreaRevision","workspaceGeneration"]
    in D.keyValuePairs D.value |> D.andThen (\pairs ->
        if List.sort (List.map Tuple.first pairs)/=List.sort fields then D.fail "Snap placement fields" else
        D.map6 (\regionName geometry monitor output area workspace -> {region=regionName,geometry=geometry,monitor=monitor,outputOwnershipGeneration=output,workAreaRevision=area,workspaceGeneration=workspace,context=context})
            (D.field "region" region) (D.field "geometry" rectangle) (D.field "monitor" UInt64.decoder)
            (D.field "outputOwnershipGeneration" positive) (D.field "workAreaRevision" positive) (D.field "workspaceGeneration" positive))

matches : Geometry.Snapshot -> Counter -> Proposal -> Bool
matches snapshot target proposed =
    case List.filter (identity >> (==) proposed.region) regions |> List.head of
        Nothing -> False
        Just region -> open snapshot target |> Maybe.map (\choice -> proposal {choice|selected=region}==Just proposed) |> Maybe.withDefault False
