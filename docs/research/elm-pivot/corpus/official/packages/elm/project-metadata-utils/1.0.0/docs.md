# official/packages/elm/project-metadata-utils/1.0.0/docs.json
Source: https://package.elm-lang.org/packages/elm/project-metadata-utils/1.0.0/docs.json

# Elm.Constraint

 Helpers for working with version constraint strings in `elm.json` files.

# Constraint
@docs Constraint, check

# String Conversions
@docs toString, fromString

# JSON Conversions
@docs encode, decoder



## Constraint

```elm
-- Opaque type: Constraint (constructors not exposed)
```

 A guaranteed valid Elm constraint. That means the lower bound `v1` and
the upper bound `v2` are both valid `Elm.Version` versions, and `v1 <= v2` is
guaranteed.


## check

```elm
check : Elm.Version.Version -> Elm.Constraint.Constraint -> Basics.Bool
```

 Check if a version is within the given constraint:

    import Elm.Version as V

    oneToTwo = fromString "1.0.0 <= v < 2.0.0"
    sixToTen = fromString "6.0.0 <= v < 10.0.0"

    -- Maybe.map (check V.one) oneToTwo == Just True
    -- Maybe.map (check V.one) sixToTen == Just False


## decoder

```elm
decoder : Json.Decode.Decoder Elm.Constraint.Constraint
```

 Decode the constraint strings that appear in `elm.json`


## encode

```elm
encode : Elm.Constraint.Constraint -> Json.Encode.Value
```

 Turn a `Constraint` into a string for use in `elm.json`


## fromString

```elm
fromString : String.String -> Maybe.Maybe Elm.Constraint.Constraint
```

 Try to convert a `String` into a `Constraint`:

    fromString "1.0.0 <= v < 2.0.0"   == Just ...
    fromString "1.0.0 <= v < 10.0.0"  == Just ...
    fromString "1.0.0 <= v <= 1.0.0"  == Just ...

    fromString "1.0.0"                == Nothing
    fromString "1.0.0 <= 2.0.0"       == Nothing
    fromString "1.0.0 <=  v  < 2.0.0" == Nothing -- extra spaces
    fromString "1.0.0 <= vsn < 2.0.0" == Nothing -- not "v" only
    fromString "2.0.0 <= v < 1.0.0"   == Nothing -- unsatisfiable


## toString

```elm
toString : Elm.Constraint.Constraint -> String.String
```

 Convert a `Constraint` to a `String` that works in `elm.json`


# Elm.Docs

 When packages are published to `package.elm-lang.org`, documentation
is generated for all of the exposed modules (and all of the exposed values).
These docs are formatted as JSON for easy consumption by anyone.

This module helps you decode the JSON docs into nice Elm values! It is
currently used by `package.elm-lang.org` to help turn JSON into nice
web pages!

# Decode Docs
@docs decoder

# Work with Docs
@docs Module, Alias, Union, Value, Binop, Associativity

# Split Docs into Blocks
@docs toBlocks, Block



## Alias

```elm
type alias Alias =
    { name : String.String, comment : String.String, args : List.List String.String, tipe : Elm.Type.Type }
```

 Documentation for a type alias. For example, if you had the source code:

    {-| pair of values -}
    type alias Pair a = ( a, a )

When it became an `Alias` it would be like this:

    { name = "Pair"
    , comment = " pair of values "
    , args = ["a"]
    , tipe = Tuple [ Var "a", Var "a" ]
    }


## Binop

```elm
type alias Binop =
    { name : String.String, comment : String.String, tipe : Elm.Type.Type, associativity : Elm.Docs.Associativity, precedence : Basics.Int }
```

 Documentation for binary operators. The content for `(+)` might look
something like this:

    { name = "+"
    , comment = "Add numbers"
    , tipe = Lambda (Var "number") (Lambda (Var "number") (Var "number"))
    , associativity = Left
    , precedence = 6
    }8


## Module

```elm
type alias Module =
    { name : String.String, comment : String.String, unions : List.List Elm.Docs.Union, aliases : List.List Elm.Docs.Alias, values : List.List Elm.Docs.Value, binops : List.List Elm.Docs.Binop }
```

 All the documentation for a particular module.

  * `name` is the module name
  * `comment` is the module comment

The actual exposed stuff is broken into categories.


## Union

```elm
type alias Union =
    { name : String.String, comment : String.String, args : List.List String.String, tags : List.List ( String.String, List.List Elm.Type.Type ) }
```

 Documentation for a union type. For example, if you had the source code:

    {-| maybe -}
    type Maybe a = Nothing | Just a

When it became a `Union` it would be like this:

    { name = "Maybe"
    , comment = " maybe "
    , args = ["a"]
    , tipe =
        [ ("Nothing", [])
        , ("Just", [Var "a"])
        ]
    }


## Value

```elm
type alias Value =
    { name : String.String, comment : String.String, tipe : Elm.Type.Type }
```

 Documentation for values and functions. For example, if you had the source
code:

    {-| do not do anything -}
    identity : a -> a
    identity value =
      value

The `Value` would look like this:

    { name = "identity"
    , comment = " do not do anything "
    , tipe = Lambda (Var "a") (Var "a")
    }


## Associativity

```elm
type Associativity
    = Left
    | None
    | Right
```

 The [associativity][] of an infix operator. This determines how we add
parentheses around everything. Here are some examples:

    1 + 2 + 3 + 4

We have to do the operations in *some* order, so which of these interpretations
should we choose?

    ((1 + 2) + 3) + 4   -- left-associative
    1 + (2 + (3 + 4))   -- right-associative

This is really important for operators like `(|>)`!

Some operators are non-associative though, meaning we do not try to add
missing parentheses. `(==)` is a nice example. `1 == 2 == 3` just is not
allowed!

[associativity]: https://en.wikipedia.org/wiki/Operator_associativity



## Block

```elm
type Block
    = MarkdownBlock (String.String)
    | UnionBlock (Elm.Docs.Union)
    | AliasBlock (Elm.Docs.Alias)
    | ValueBlock (Elm.Docs.Value)
    | BinopBlock (Elm.Docs.Binop)
    | UnknownBlock (String.String)
```

 This type represents a `Block` of documentation to show to the user.
After getting a `List Block` from `toBlocks`, everything is in the right order
and you can focus on turning the blocks into HTML exactly how you want.

**Note:** This should never produce an `UnknownBlock` but I figured it
would be better to let the block visualizer decide what to do in that case.


## decoder

```elm
decoder : Json.Decode.Decoder Elm.Docs.Module
```

 Decode the JSON documentation produced by `elm-make` for an individual
module. The documentation for a whole package is an array of module docs,
so you may need to say `(Decode.list Docs.decoder)` depending on what you
want to do.


## toBlocks

```elm
toBlocks : Elm.Docs.Module -> List.List Elm.Docs.Block
```

 The module comment describes exactly how the generated docs should look.
It is a mix of markdown and `@docs` declarations that specify when other
documentation should appear. Matching all this information up is somewhat
tricky though.

So calling `toBlocks` on a `Module` gives you a `List Block` with all the
information necessary to visualize the docs as intended.


# Elm.Error

 When `elm make --report=json` fails, this module helps you turn the
resulting JSON into HTML.

# Compile Errors
@docs decoder, Error, BadModule, Problem

# Styled Text
@docs Chunk, Style, Color

# Code Regions
@docs Region, Position



## BadModule

```elm
type alias BadModule =
    { path : String.String, name : String.String, problems : List.List Elm.Error.Problem }
```

 When I cannot compile a module, I am able to report a bunch of problems at
once. So you may see a bunch of naming errors or type errors.


## Position

```elm
type alias Position =
    { line : Basics.Int, column : Basics.Int }
```

 A line and column in the source file. Both are one-indexed, so every file
starts at `{ line = 1, column = 1 }` and increases from there.


## Problem

```elm
type alias Problem =
    { title : String.String, region : Elm.Error.Region, message : List.List Elm.Error.Chunk }
```

 A problem in an Elm module.


## Region

```elm
type alias Region =
    { start : Elm.Error.Position, end : Elm.Error.Position }
```

 Every `Problem` is caused by code in a specific `Region`.


## Style

```elm
type alias Style =
    { bold : Basics.Bool, underline : Basics.Bool, color : Maybe.Maybe Elm.Error.Color }
```

 Widely supported styles for ANSI text. Bold and underline are used very
rarely in Elm output. Mainly for a `Note` or a `Hint` about something. Colors
are used relatively infrequently, primarily to draw attention to the most
important information. Red is the problem, yellow is distilled advice, etc.


## Chunk

```elm
type Chunk
    = Unstyled (String.String)
    | Styled (Elm.Error.Style) (String.String)
```

 A chunk of text to show. Chunks will contain newlines here and there, so
I recommend using `white-space: pre` to make sure everything looks alright.

The error messages are designed to look nice in 80 columns, and the only way
any line will be longer than that is if a code snippet from the user is longer.
Anyway, please try to get a presentation that matches the terminal pretty well.
It will look alright, and the consistency will be more valuable than any small
changes.


## Color

```elm
type Color
    = Red
    | RED
    | Magenta
    | MAGENTA
    | Yellow
    | YELLOW
    | Green
    | GREEN
    | Cyan
    | CYAN
    | Blue
    | BLUE
    | White
    | WHITE
    | Black
    | BLACK
```

 Error messages use colors to emphasize the most useful information. This
helps people resolve their problems quicker! Because the errors need to work
on the terminal as well, the colors are limited to ANSI colors that are
widely supported by different terminal softwark.

So there are eight colors, each with a `Dull` and `VIVID` version.

**Note:** I have tried to make the _meaning_ of each color consistent across
all error messages (red is problem, yellow is decent advice, green is great
advice, cyan is helpful information, etc.) so please use colors that actually
match the color names! I think consistency is worth a lot within the ecosystem.


## Error

```elm
type Error
    = GeneralProblem ({ path : Maybe.Maybe String.String, title : String.String, message : List.List Elm.Error.Chunk })
    | ModuleProblems (List.List Elm.Error.BadModule)
```

 When `elm make --report=json` fails, there are two major categories of
error. Usually you have `ModuleProblems` like an unknown variable name or type
mismatch, but you can also get a `GeneralProblem` like cyclic modules or an
invalid `elm.json` file. The latter are much less common, but because they
never have a `Region` they need to be handled separately.


## decoder

```elm
decoder : Json.Decode.Decoder Elm.Error.Error
```

 Decode the JSON produced when `elm make --report=json` fails. The goal is
to get the data in a format that can be presented in HTML.

**Note:** Please follow the design advice in the rest of the docs, like for
[`Chunk`](#Chunk) and [`Color`](#Color). Consistent presentation of errors
means that once you learn how to read errors, you have that ability with any
tool you use in Elm.


# Elm.License

 The `elm.json` for packages always has a `"license"` field. That field
must contain an OSI approved license in the [SPDX](https://spdx.org/licenses/) format.

This module helps verify that licenses are acceptable.


# Licenses
@docs License, bsd3, toDetails, osiApprovedSpdxLicenses

# String Conversions
@docs toString, fromString

# JSON Conversions
@docs encode, decoder


## License

```elm
-- Opaque type: License (constructors not exposed)
```

 An OSI approved license in the [SPDX](https://spdx.org/licenses/) format.
It is impossible to construct an invalid `License` value.


## bsd3

```elm
bsd3 : Elm.License.License
```

 Easy access to a license commonly used in the Elm ecosystem.

  - `name` = `BSD 3-clause "New" or "Revised" License`
  - `spdx` = `BSD-3-Clause`



## decoder

```elm
decoder : Json.Decode.Decoder Elm.License.License
```

 Decode a SPDX string from `elm.json` into a `License`


## encode

```elm
encode : Elm.License.License -> Json.Encode.Value
```

 Encode a `License` into a SPDX string for use in `elm.json`


## fromString

```elm
fromString : String.String -> Maybe.Maybe Elm.License.License
```

 Convert an arbitrary `String` into a `License`:

    fromString "BSD-3-Clause" == Just bsd3
    fromString "BSD3"         == Nothing

Notice that this function only succeds when given an OSI approved license
in its SPDX abbreviation. Go [here](https://spdx.org/licenses/) for a full
list of such licenses.


## osiApprovedSpdxLicenses

```elm
osiApprovedSpdxLicenses : List.List Elm.License.License
```

 OSI approved licenses in [SPDX format](https://spdx.org/licenses/).


## toDetails

```elm
toDetails : Elm.License.License -> { name : String.String, spdx : String.String }
```

 Extract the common `name` of a `License`, along with its standardized
`spdx` abbreviation.

    toDetails bsd3
    -- { name = "BSD 3-clause \"New\" or \"Revised\" License"
    -- , spdx = "BSD-3-Clause"
    -- }


## toString

```elm
toString : Elm.License.License -> String.String
```

 Convert a `License` to its SPDX abbreviation:

    toString bsd3 == "BSD-3-Clause"


# Elm.Module

 Helpers for working with module name strings in `elm.json` files.

# Modules
@docs Name

# String Conversions
@docs toString, fromString

# JSON Conversions
@docs encode, decoder



## Name

```elm
-- Opaque type: Name (constructors not exposed)
```

 A guaranteed valid Elm module name.


## decoder

```elm
decoder : Json.Decode.Decoder Elm.Module.Name
```

 Decode the module name strings that appear in `elm.json`


## encode

```elm
encode : Elm.Module.Name -> Json.Encode.Value
```

 Turn a `Name` into a string for use in `elm.json`


## fromString

```elm
fromString : String.String -> Maybe.Maybe Elm.Module.Name
```

 Try to convert a `String` into a `Name`:

    fromString "Maybe"       == Just ...
    fromString "Elm.Name"  == Just ...
    fromString "Json.Decode" == Just ...
    fromString "json.decode" == Nothing
    fromString "Json_Decode" == Nothing


## toString

```elm
toString : Elm.Module.Name -> String.String
```

 Convert a `Name` to a `String` that works in `elm.json`


# Elm.Package

 Helpers for working with package name strings in `elm.json` files.

# Packages
@docs Name

# String Conversions
@docs toString, fromString

# JSON Conversions
@docs encode, decoder



## Name

```elm
-- Opaque type: Name (constructors not exposed)
```

 A guaranteed valid Elm package name.


## decoder

```elm
decoder : Json.Decode.Decoder Elm.Package.Name
```

 Decode the module name strings that appear in `elm.json`


## encode

```elm
encode : Elm.Package.Name -> Json.Encode.Value
```

 Turn a `Name` into a string for use in `elm.json`


## fromString

```elm
fromString : String.String -> Maybe.Maybe Elm.Package.Name
```

 Try to convert a `String` into a `Name`:

    fromString "elm/core"    == Just ...
    fromString "elm/html"    == Just ...
    fromString "tom/elm-css" == Just ...
    fromString "tom/elm_css" == Nothing
    fromString "tom/x.js"    == Nothing
    fromString "elm"         == Nothing
    fromString "html"        == Nothing


## toString

```elm
toString : Elm.Package.Name -> String.String
```

 Convert a `Name` to a `String` that works in `elm.json`


# Elm.Project

 Turn `elm.json` files into data that is nice to use in Elm.

# Projects
@docs Project, ApplicationInfo, Deps, PackageInfo, Exposed

# JSON Conversions
@docs encode, decoder



## ApplicationInfo

```elm
type alias ApplicationInfo =
    { elm : Elm.Version.Version, dirs : List.List String.String, depsDirect : Elm.Project.Deps Elm.Version.Version, depsIndirect : Elm.Project.Deps Elm.Version.Version, testDepsDirect : Elm.Project.Deps Elm.Version.Version, testDepsIndirect : Elm.Project.Deps Elm.Version.Version }
```

 The contents of an `elm.json` with `"type": "application"`.


## Deps

```elm
type alias Deps constraint =
    List.List ( Elm.Package.Name, constraint )
```

 The dependencies for a project. The order is preserved from JSON.


## PackageInfo

```elm
type alias PackageInfo =
    { name : Elm.Package.Name, summary : String.String, license : Elm.License.License, version : Elm.Version.Version, exposed : Elm.Project.Exposed, deps : Elm.Project.Deps Elm.Constraint.Constraint, testDeps : Elm.Project.Deps Elm.Constraint.Constraint, elm : Elm.Constraint.Constraint }
```

 The contents of an `elm.json` with `"type": "package"`.


## Exposed

```elm
type Exposed
    = ExposedList (List.List Elm.Module.Name)
    | ExposedDict (List.List ( String.String, List.List Elm.Module.Name ))
```

 There are two ways to specify `"exposed-modules"` field in an `elm.json`
for packages. In one you just list the exposed modules. In the other, you
provide headers for chunks of module names. In either case, the package website
preserves this information to make the presentation nicer.


## Project

```elm
type Project
    = Application (Elm.Project.ApplicationInfo)
    | Package (Elm.Project.PackageInfo)
```

 There are two types of Elm projects, one for applications and another one
for packages. The `elm.json` is different in each case, so we they are modeled
as [`ApplicationInfo`](#ApplicationInfo) and [`PackageInfo`](#PackageInfo) types.


## decoder

```elm
decoder : Json.Decode.Decoder Elm.Project.Project
```

 Decode the contents of `elm.json` into a `Project`.


## encode

```elm
encode : Elm.Project.Project -> Json.Encode.Value
```

 Turn a `Project` into the JSON that goes in `elm.json`


# Elm.Type

 This is specifically for handling the types that appear in
documentation generated by `elm-make`. If you are looking to parse
arbitrary type signatures with creative indentation (e.g. newlines
and comments) this library will not do what you want. Instead,
check out the source code and go from there. It's not too tough!

@docs Type, decoder



## Type

```elm
type Type
    = Var (String.String)
    | Lambda (Elm.Type.Type) (Elm.Type.Type)
    | Tuple (List.List Elm.Type.Type)
    | Type (String.String) (List.List Elm.Type.Type)
    | Record (List.List ( String.String, Elm.Type.Type )) (Maybe.Maybe String.String)
```

 Represent Elm types as values! Here are some examples:

    Int            ==> Type "Int" []

    a -> b         ==> Lambda (Var "a") (Var "b")

    ( a, b )       ==> Tuple [ Var "a", Var "b" ]

    Maybe a        ==> Type "Maybe" [ Var "a" ]

    { x : Float }  ==> Record [("x", Type "Float" [])] Nothing


## decoder

```elm
decoder : Json.Decode.Decoder Elm.Type.Type
```

 Decode the JSON representation of `Type` values.


# Elm.Version

 Helpers for working with version strings in `elm.json` files.

# Versions
@docs Version, one, compare

# String Conversions
@docs toString, fromString

# JSON Conversions
@docs encode, decoder

# Tuple Conversions
@docs toTuple, fromTuple



## Version

```elm
-- Opaque type: Version (constructors not exposed)
```

 A guaranteed valid Elm version. All versions are `1.0.0` or greater.


## compare

```elm
compare : Elm.Version.Version -> Elm.Version.Version -> Basics.Order
```

 Compare two versions:

    v1 = fromString "1.0.0"
    v2 = fromString "2.0.0"
    v3 = fromString "3.0.0"

    -- Maybe.map2 compare v1 v2 == Just LT
    -- Maybe.map2 compare v2 v2 == Just EQ
    -- Maybe.map2 compare v2 v1 == Just GT



## decoder

```elm
decoder : Json.Decode.Decoder Elm.Version.Version
```

 Decode the version strings that appear in `elm.json`


## encode

```elm
encode : Elm.Version.Version -> Json.Encode.Value
```

 Turn a `Version` into a string for use in `elm.json`


## fromString

```elm
fromString : String.String -> Maybe.Maybe Elm.Version.Version
```

 Try to convert a `String` into a `Version`. The major, minor, and patch
numbers must all appear separated by dots:

    fromString "1.0.0" == Just one
    fromString "2.0.0" == Just ...
    fromString "3-0-0" == Nothing
    fromString "3.0"   == Nothing


## fromTuple

```elm
fromTuple : ( Basics.Int, Basics.Int, Basics.Int ) -> Maybe.Maybe Elm.Version.Version
```

 Try to make a `Version` from given numbers. This way you do not need
to turn things into strings for no reason. It can still fail if you give
negative numbers or versions below `1.0.0`:

    fromTuple (1, 0, 0) == Just one
    fromTuple (2, 0, 1) == Just ...
    fromTuple (0, 0, 1) == Nothing


## one

```elm
one : Elm.Version.Version
```

 Version `1.0.0` for easy access.


## toString

```elm
toString : Elm.Version.Version -> String.String
```

 Convert a `Version` to a `String` that works in `elm.json`

    toString one == "1.0.0"


## toTuple

```elm
toTuple : Elm.Version.Version -> ( Basics.Int, Basics.Int, Basics.Int )
```

 Turn a `Version` into a tuple to extract the numbers as integers.

    toTuple one == (1, 0, 0)

    Maybe.map toTuple (fromString "2.0.4" ) == Just (2, 0, 4)
    Maybe.map toTuple (fromString "7.3.10") == Just (7, 3, 10)

