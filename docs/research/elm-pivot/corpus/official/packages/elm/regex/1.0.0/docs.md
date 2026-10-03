# official/packages/elm/regex/1.0.0/docs.json
Source: https://package.elm-lang.org/packages/elm/regex/1.0.0/docs.json

# Regex

 A library for working with regex. The syntax matches the [`RegExp`][js]
library from JavaScript.

[js]: https://developer.mozilla.org/en/docs/Web/JavaScript/Guide/Regular_Expressions

# Create
@docs Regex, fromString, fromStringWith, Options, never

# Use
@docs contains, split, find, replace, Match

# Fancier Uses
@docs splitAtMost, findAtMost, replaceAtMost



## Match

```elm
type alias Match =
    { match : String.String, index : Basics.Int, number : Basics.Int, submatches : List.List (Maybe.Maybe String.String) }
```

 The details about a particular match:

  * `match` &mdash; the full string of the match.
  * `index` &mdash; the index of the match in the original string.
  * `number` &mdash; if you find many matches, you can think of each one
    as being labeled with a `number` starting at one. So the first time you
    find a match, that is match `number` one. Second time is match `number` two.
    This is useful when paired with `replace` if replacement is dependent on how
    many times a pattern has appeared before.
  * `submatches` &mdash; a `Regex` can have [subpatterns][sub], sup-parts that
    are in parentheses. This is a list of all these submatches. This is kind of
    garbage to use, and using a package like [`elm/parser`][parser] is
    probably easier.

[sub]: https://developer.mozilla.org/en/docs/Web/JavaScript/Guide/Regular_Expressions#Using_Parenthesized_Substring_Matches
[parser]: /packages/elm/parser/latest



## Options

```elm
type alias Options =
    { caseInsensitive : Basics.Bool, multiline : Basics.Bool }
```



## Regex

```elm
-- Opaque type: Regex (constructors not exposed)
```

 A regular expression [as specified in JavaScript][js].

[js]: https://developer.mozilla.org/en/docs/Web/JavaScript/Guide/Regular_Expressions



## contains

```elm
contains : Regex.Regex -> String.String -> Basics.Bool
```

 Check to see if a Regex is contained in a string.

    import Regex

    digit : Regex.Regex
    digit =
      Maybe.withDefault Regex.never <|
        Regex.fromString "[0-9]"

    -- Regex.contains digit "abc123" == True
    -- Regex.contains digit "abcxyz" == False


## find

```elm
find : Regex.Regex -> String.String -> List.List Regex.Match
```

 Find matches in a string:

    import Regex

    location : Regex.Regex
    location =
      Maybe.withDefault Regex.never <|
        Regex.fromString "[oi]n a (\\w+)"

    places : List Regex.Match
    places =
      Regex.find location "I am on a boat in a lake."

    -- map .match      places == [ "on a boat", "in a lake" ]
    -- map .submatches places == [ [Just "boat"], [Just "lake"] ]

If you need `submatches` for some reason, a library like
[`elm/parser`][parser] will probably lead to better code in the long run.

[parser]: /packages/elm/parser/latest


## findAtMost

```elm
findAtMost : Basics.Int -> Regex.Regex -> String.String -> List.List Regex.Match
```

 Just like `find` but it stops after some number of matches.

A library like [`elm/parser`][parser] will probably lead to better code in
the long run.

[parser]: /packages/elm/parser/latest


## fromString

```elm
fromString : String.String -> Maybe.Maybe Regex.Regex
```

 Try to create a `Regex`. Not all strings are valid though, so you get a
`Maybe' back. This means you can safely accept input from users.

    import Regex

    lowerCase : Regex.Regex
    lowerCase =
      Maybe.withDefault Regex.never <|
        Regex.fromString "[a-z]+"

**Note:** There are some [shorthand character classes][short] like `\w` for
word characters, `\s` for whitespace characters, and `\d` for digits. **Make
sure they are properly escaped!** If you specify them directly in your code,
they would look like `"\\w\\s\\d"`.

[short]: https://www.regular-expressions.info/shorthand.html


## fromStringWith

```elm
fromStringWith : Regex.Options -> String.String -> Maybe.Maybe Regex.Regex
```

 Create a `Regex` with some additional options. For example, you can define
`fromString` like this:

    import Regex

    fromString : String -> Maybe Regex.Regex
    fromString string =
      fromStringWith { caseInsensitive = False, multiline = False } string



## never

```elm
never : Regex.Regex
```

 A regular expression that never matches any string.


## replace

```elm
replace : Regex.Regex -> (Regex.Match -> String.String) -> String.String -> String.String
```

 Replace matches. The function from `Match` to `String` lets
you use the details of a specific match when making replacements.

    import Regex

    userReplace : String -> (Regex.Match -> String) -> String -> String
    userReplace userRegex replacer string =
      case Regex.fromString userRegex of
        Nothing ->
          string

        Just regex ->
          Regex.replace regex replacer string

    devowel : String -> String
    devowel string =
      userReplace "[aeiou]" (\_ -> "") string

    -- devowel "The quick brown fox" == "Th qck brwn fx"

    reverseWords : String -> String
    reverseWords string =
      userReplace "\\w+" (.match >> String.reverse) string

    -- reverseWords "deliver mined parts" == "reviled denim strap"


## replaceAtMost

```elm
replaceAtMost : Basics.Int -> Regex.Regex -> (Regex.Match -> String.String) -> String.String -> String.String
```

 Just like `replace` but it stops after some number of matches.

A library like [`elm/parser`][parser] will probably lead to better code in
the long run.

[parser]: /packages/elm/parser/latest


## split

```elm
split : Regex.Regex -> String.String -> List.List String.String
```

 Split a string. The following example will split on commas and tolerate
whitespace on either side of the comma:

    import Regex

    comma : Regex.Regex
    comma =
      Maybe.withDefault Regex.never <|
        Regex.fromString " *, *"

    -- Regex.split comma "tom,99,90,85"     == ["tom","99","90","85"]
    -- Regex.split comma "tom, 99, 90, 85"  == ["tom","99","90","85"]
    -- Regex.split comma "tom , 99, 90, 85" == ["tom","99","90","85"]

If you want some really fancy splits, a library like
[`elm/parser`][parser] will probably be easier to use.

[parser]: /packages/elm/parser/latest


## splitAtMost

```elm
splitAtMost : Basics.Int -> Regex.Regex -> String.String -> List.List String.String
```

 Just like `split` but it stops after some number of matches.

A library like [`elm/parser`][parser] will probably lead to better code in
the long run.

[parser]: /packages/elm/parser/latest

