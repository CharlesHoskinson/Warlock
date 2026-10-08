module Switcher exposing (Model, Direction(..), Phase(..), initial, generation, phase, entries, selected, lastStep, step, release, ready, readyFrozen, reconcile, navigate, choose, commit, cancel)

import Dict exposing (Dict)
import Taskbar exposing (Family)
import UInt64 exposing (Counter)

type Direction = Forward | Reverse
type Phase = Idle | Waiting | Browsing | Resolved | Cancelled
type Model = Model
    { generation : Counter
    , phase : Phase
    , steps : Dict Int Direction
    , released : Maybe Int
    , ready : Bool
    , entries : List Family
    , ring : List Counter
    , origin : Maybe Counter
    , selected : Int
    , baseline : Maybe { root : Counter, through : Int }
    }

initial : Model
initial = Model {generation=UInt64.zero,phase=Idle,steps=Dict.empty,released=Nothing,ready=False,entries=[],ring=[],origin=Nothing,selected=0,baseline=Nothing}

generation (Model model) = model.generation
phase (Model model) = model.phase
entries (Model model) = model.entries
selected (Model model) = List.drop model.selected model.entries |> List.head
lastStep (Model model) = lastOrdinal model

writable model = List.member model.phase [Waiting,Browsing]
fresh token = case initial of
    Model model -> {model | generation=token,phase=Waiting}

prepare token model =
    case UInt64.compare token model.generation of
        GT -> if token==UInt64.zero then Nothing else Just (fresh token)
        EQ -> if writable model then Just model else Nothing
        LT -> Nothing

index root rows = rows |> List.indexedMap Tuple.pair |> List.filter (\(_,row) -> row.root==root) |> List.head |> Maybe.map Tuple.first
lastOrdinal model = Dict.keys model.steps |> List.maximum |> Maybe.withDefault 0
contiguous through model = through>0 && List.all (\ordinal -> Dict.member ordinal model.steps) (List.range 1 through)
delta direction = if direction==Forward then 1 else -1

-- Resolving a chord returns at most one identity. This module never emits a
-- native mutation: the integration root refreshes the existing effect grant.
settle model =
    let complete = model.released |> Maybe.map (\ordinal -> contiguous ordinal model) |> Maybe.withDefault (contiguous (lastOrdinal model) model)
    in if not model.ready || not complete then (Model {model | phase=Waiting},Nothing)
       else if List.isEmpty model.entries then (Model {model | phase=Resolved},Nothing)
       else if model.released/=Nothing then
           let current=Model {model | phase=Resolved}
           in (current,selected current)
       else (Model {model | phase=Browsing},Nothing)

advanceSelection model =
    let ring=if model.baseline==Nothing then model.ring else List.map .root model.entries
        size=List.length ring
        anchor=(model.baseline |> Maybe.map .root |> Maybe.withDefault (model.origin |> Maybe.withDefault UInt64.zero))
            |> (\root -> ring |> List.indexedMap Tuple.pair |> List.filter (\(_,identity) -> identity==root) |> List.head |> Maybe.map Tuple.first)
            |> Maybe.withDefault (if Dict.get 1 model.steps==Just Forward then -1 else 0)
        through=model.baseline |> Maybe.map .through |> Maybe.withDefault 0
        total=Dict.toList model.steps |> List.filter (\(number,_) -> number>through) |> List.map (Tuple.second >> delta) |> List.sum
        position=if size==0 then 0 else modBy size (anchor+total)
        -- Buffered steps keep their entry-time positions even when a member
        -- retires before Ready. Only then advance to the next surviving root.
        survivor=(List.drop position ring++List.take position ring)
            |> List.filter (\identity -> List.any (\row -> row.root==identity) model.entries) |> List.head
    in {model | selected=survivor |> Maybe.andThen (\identity -> index identity model.entries) |> Maybe.withDefault 0}

step : Counter -> Int -> Direction -> Model -> (Model,Maybe Family)
step token ordinal direction ((Model current) as original) =
    if ordinal<1 || ordinal>4096 then (original,Nothing) else
    case prepare token current of
        Nothing -> (original,Nothing)
        Just model ->
            if model.released |> Maybe.map (\final -> ordinal>final) |> Maybe.withDefault False then (original,Nothing) else
            case Dict.get ordinal model.steps of
                Just previous ->
                    if previous==direction then (original,Nothing)
                    else (Model {model | phase=Cancelled,entries=[]},Nothing)
                Nothing ->
                    let next={model | steps=Dict.insert ordinal direction model.steps}
                    in settle (if next.ready then advanceSelection next else next)

release : Counter -> Int -> Model -> (Model,Maybe Family)
release token ordinal ((Model current) as original) =
    if ordinal<1 || ordinal>4096 then (original,Nothing) else
    case prepare token current of
        Nothing -> (original,Nothing)
        Just model ->
            if ordinal<lastOrdinal model then (original,Nothing) else
            case model.released of
                Just _ -> (original,Nothing)
                Nothing -> settle {model | released=Just ordinal}

ready : Counter -> List Counter -> List Family -> Maybe Counter -> Model -> (Model,Maybe Family)
ready = readyWith Nothing

readyFrozen : Counter -> List Counter -> List Counter -> List Family -> Maybe Counter -> Model -> (Model,Maybe Family)
readyFrozen token roots = readyWith (Just roots) token

readyWith frozenRoots token history candidates origin ((Model model) as original) =
    if token/=model.generation || not (writable model) || model.ready then (original,Nothing) else
    let eligible=List.filter (\row -> row.available && (frozenRoots |> Maybe.map (List.member row.root) |> Maybe.withDefault True)) candidates
        unique rows = List.foldl (\row accumulated -> if List.any (\old -> old.root==row.root) accumulated then accumulated else accumulated++[row]) [] rows
        known=List.filterMap (\root -> List.filter (\row -> row.root==root) eligible |> List.head) history |> unique
        unranked=eligible |> List.filter (\row -> not (List.any (\old -> old.root==row.root) known)) |> unique |> List.sortWith (\a b -> UInt64.compare a.root b.root)
        frozen=known++unranked
        ring=frozenRoots |> Maybe.map (\roots -> List.filter (\identity -> List.member identity roots) history
            ++ (roots |> List.filter (\identity -> not (List.member identity history)) |> List.sortWith UInt64.compare))
            |> Maybe.withDefault (List.map .root frozen)
    in if List.length candidates>256 || List.length ring>256 then (Model {model | phase=Cancelled},Nothing) else
        settle (advanceSelection {model | ready=True,entries=frozen,ring=ring,origin=origin})

-- Retire from the frozen ring, updating only surviving identities. Arrivals
-- cannot enter this chord and replacement native incarnations never alias it.
reconcile : List Family -> Model -> Model
reconcile candidates ((Model model) as original) =
    if not (writable model) || not model.ready then original else
    let current old = List.filter (\row -> row.available && row.root==old.root && row.application==old.application) candidates |> List.head
        surviving=List.filterMap current model.entries
        prior=selected original |> Maybe.map .root
        after=List.drop model.selected model.entries++List.take model.selected model.entries
        fallback=after |> List.filterMap (\old -> current old |> Maybe.map .root) |> List.head
        root=prior |> Maybe.andThen (\identity -> if List.any (\row -> row.root==identity) surviving then Just identity else Nothing) |> Maybe.withDefault (fallback |> Maybe.withDefault UInt64.zero)
        position=index root surviving |> Maybe.withDefault 0
        baseline=if model.phase==Browsing then Just {root=root,through=lastOrdinal model} else model.baseline
    in Model {model | entries=surviving,selected=position,baseline=baseline,phase=if List.isEmpty surviving then Cancelled else model.phase}

-- Pointer/local controls move the selection baseline without minting another
-- native ordinal. The next admitted physical step still has its original ID.
navigate : Direction -> Model -> Model
navigate direction ((Model model) as original) =
    if model.phase/=Browsing || model.released/=Nothing || List.isEmpty model.entries then original else
    let position=modBy (List.length model.entries) (model.selected+delta direction)
        root=List.drop position model.entries |> List.head |> Maybe.map .root |> Maybe.withDefault UInt64.zero
    in Model {model | selected=position,baseline=Just {root=root,through=lastOrdinal model}}

choose : Counter -> Counter -> Model -> Model
choose token root ((Model model) as original) =
    if token/=model.generation || model.phase/=Browsing || model.released/=Nothing then original else
    index root model.entries |> Maybe.map (\position -> Model {model | selected=position,baseline=Just {root=root,through=lastOrdinal model}}) |> Maybe.withDefault original

commit : Counter -> Model -> (Model,Maybe Family)
commit token ((Model model) as original) =
    if token/=model.generation || model.phase/=Browsing then (original,Nothing)
    else release token (lastOrdinal model) original

cancel : Counter -> Model -> Model
cancel token ((Model model) as original) =
    if token/=model.generation || not (writable model) then original
    else Model {model | phase=Cancelled,entries=[]}
