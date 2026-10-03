# official/packages/elm-explorations/test/1.2.1/docs.json
Source: https://package.elm-lang.org/packages/elm-explorations/test/1.2.1/docs.json

# Expect

 A library to create `Expectation`s, which describe a claim to be tested.


## Quick Reference

  - [`equal`](#equal) `(arg2 == arg1)`
  - [`notEqual`](#notEqual) `(arg2 /= arg1)`
  - [`lessThan`](#lessThan) `(arg2 < arg1)`
  - [`atMost`](#atMost) `(arg2 <= arg1)`
  - [`greaterThan`](#greaterThan) `(arg2 > arg1)`
  - [`atLeast`](#atLeast) `(arg2 >= arg1)`
  - [`true`](#true) `(arg == True)`
  - [`false`](#false) `(arg == False)`
  - [Floating Point Comparisons](#floating-point-comparisons)


## Basic Expectations

@docs Expectation, equal, notEqual, all


## Numeric Comparisons

@docs lessThan, atMost, greaterThan, atLeast


## Floating Point Comparisons

These functions allow you to compare `Float` values up to a specified rounding error, which may be relative, absolute,
or both. For an in-depth look, see our [Guide to Floating Point Comparison](#guide-to-floating-point-comparison).

@docs FloatingPointTolerance, within, notWithin


## Booleans

@docs true, false


## Collections

@docs ok, err, equalLists, equalDicts, equalSets


## Customizing

These functions will let you build your own expectations.

@docs pass, fail, onFail


## Guide to Floating Point Comparison

In general, if you are multiplying, you want relative tolerance, and if you're adding,
you want absolute tolerance. If you are doing both, you want both kinds of tolerance,
or to split the calculation into smaller parts for testing.


### Absolute Tolerance

Let's say we want to figure out if our estimation of pi is precise enough.

Is `3.14` within `0.01` of `pi`? Yes, because `3.13 < pi < 3.15`.

    test "3.14 approximates pi with absolute precision" <|
        \_ ->
            3.14 |> Expect.within (Absolute 0.01) pi


### Relative Tolerance

What if we also want to know if our circle circumference estimation is close enough?

Let's say our circle has a radius of `r` meters. The formula for circle circumference is `C=2*r*pi`.
To make the calculations a bit easier ([ahem](https://tauday.com/tau-manifesto)), we'll look at half the circumference; `C/2=r*pi`.
Is `r * 3.14` within `0.01` of `r * pi`?
That depends, what does `r` equal? If `r` is `0.01`mm, or `0.00001` meters, we're comparing
`0.00001 * 3.14 - 0.01 < r * pi < 0.00001 * 3.14 + 0.01` or `-0.0099686 < 0.0000314159 < 0.0100314`.
That's a huge tolerance! A circumference that is _a thousand times longer_ than we expected would pass that test!

On the other hand, if `r` is very large, we're going to need many more digits of pi.
For an absolute tolerance of `0.01` and a pi estimation of `3.14`, this expectation only passes if `r < 2*pi`.

If we use a relative tolerance of `0.01` instead, the circle area comparison becomes much better. Is `r * 3.14` within
`1%` of `r * pi`? Yes! In fact, three digits of pi approximation is always good enough for a 0.1% relative tolerance,
as long as `r` isn't [too close to zero](https://en.wikipedia.org/wiki/Denormal_number).

    fuzz
        (floatRange 0.000001 100000)
        "Circle half-circumference with relative tolerance"
        (\r -> r * 3.14 |> Expect.within (Relative 0.001) (r * pi))


### Trouble with Numbers Near Zero

If you are adding things near zero, you probably want absolute tolerance. If you're comparing values between `-1` and `1`, you should consider using absolute tolerance.

For example: Is `1 + 2 - 3` within `1%` of `0`? Well, if `1`, `2` and `3` have any amount of rounding error, you might not get exactly zero. What is `1%` above and below `0`? Zero. We just lost all tolerance. Even if we hard-code the numbers, we might not get exactly zero; `0.1 + 0.2` rounds to a value just above `0.3`, since computers, counting in binary, cannot write down any of those three numbers using a finite number of digits, just like we cannot write `0.333...` exactly in base 10.

Another example is comparing values that are on either side of zero. `0.0001` is more than `100%` away from `-0.0001`. In fact, `infinity` is closer to `0.0001` than `0.0001` is to `-0.0001`, if you are using a relative tolerance. Twice as close, actually. So even though both `0.0001` and `-0.0001` could be considered very close to zero, they are very far apart relative to each other. The same argument applies for any number of zeroes.



## Expectation

```elm
type alias Expectation =
    Test.Expectation.Expectation
```

 The result of a single test run: either a [`pass`](#pass) or a
[`fail`](#fail).


## FloatingPointTolerance

```elm
type FloatingPointTolerance
    = Absolute (Basics.Float)
    | Relative (Basics.Float)
    | AbsoluteOrRelative (Basics.Float) (Basics.Float)
```

 A type to describe how close a floating point number must be to the expected value for the test to pass. This may be
specified as absolute or relative.

`AbsoluteOrRelative` tolerance uses a logical OR between the absolute (specified first) and relative tolerance. If you
want a logical AND, use [`Expect.all`](#all).



## all

```elm
all : List.List (subject -> Expect.Expectation) -> subject -> Expect.Expectation
```

 Passes if each of the given functions passes when applied to the subject.

Passing an empty list is assumed to be a mistake, so `Expect.all []`
will always return a failed expectation no matter what else it is passed.

    Expect.all
        [ Expect.greaterThan -2
        , Expect.lessThan 5
        ]
        (List.length [])
    -- Passes because (0 > -2) is True and (0 < 5) is also True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because (0 < -10) is False
    List.length []
        |> Expect.all
            [ Expect.greaterThan -2
            , Expect.lessThan -10
            , Expect.equal 0
            ]
    {-
    0
    ╷
    │ Expect.lessThan
    ╵
    -10
    -}



## atLeast

```elm
atLeast : comparable -> comparable -> Expect.Expectation
```

 Passes if the second argument is greater than or equal to the first.

    Expect.atLeast -2 (List.length [])

    -- Passes because (0 >= -2) is True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because (0 >= 3) is False
    List.length []
        |> Expect.atLeast 3

    {-

    0
    ╷
    │ Expect.atLeast
    ╵
    3

    -}



## atMost

```elm
atMost : comparable -> comparable -> Expect.Expectation
```

 Passes if the second argument is less than or equal to the first.

    Expect.atMost 1 (List.length [])

    -- Passes because (0 <= 1) is True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because (0 <= -3) is False
    List.length []
        |> Expect.atMost -3

    {-

    0
    ╷
    │ Expect.atMost
    ╵
    -3

    -}



## equal

```elm
equal : a -> a -> Expect.Expectation
```

 Passes if the arguments are equal.

    Expect.equal 0 (List.length [])

    -- Passes because (0 == 0) is True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because the expected value didn't split the space in "Betty Botter"
    String.split " " "Betty Botter bought some butter"
        |> Expect.equal [ "Betty Botter", "bought", "some", "butter" ]

    {-

    [ "Betty", "Botter", "bought", "some", "butter" ]
    ╷
    │ Expect.equal
    ╵
    [ "Betty Botter", "bought", "some", "butter" ]

    -}

Do not equate `Float` values; use [`within`](#within) instead.



## equalDicts

```elm
equalDicts : Dict.Dict comparable a -> Dict.Dict comparable a -> Expect.Expectation
```

 Passes if the arguments are equal dicts.

    -- Passes
    Dict.fromList [ ( 1, "one" ), ( 2, "two" ) ]
        |> Expect.equalDicts (Dict.fromList [ ( 1, "one" ), ( 2, "two" ) ])

Failures resemble code written in pipeline style, so you can tell
which argument is which, and reports which keys were missing from
or added to each dict:

    -- Fails
    (Dict.fromList [ ( 1, "one" ), ( 2, "too" ) ])
        |> Expect.equalDicts (Dict.fromList [ ( 1, "one" ), ( 2, "two" ), ( 3, "three" ) ])

    {-

    Dict.fromList [(1,"one"),(2,"too")]
    diff: -[ (2,"two"), (3,"three") ] +[ (2,"too") ]
    ╷
    │ Expect.equalDicts
    ╵
    diff: +[ (2,"two"), (3,"three") ] -[ (2,"too") ]
    Dict.fromList [(1,"one"),(2,"two"),(3,"three")]

    -}



## equalLists

```elm
equalLists : List.List a -> List.List a -> Expect.Expectation
```

 Passes if the arguments are equal lists.

    -- Passes
    [ 1, 2, 3 ]
        |> Expect.equalLists [ 1, 2, 3 ]

Failures resemble code written in pipeline style, so you can tell
which argument is which, and reports which index the lists first
differed at or which list was longer:

    -- Fails
    [ 1, 2, 4, 6 ]
        |> Expect.equalLists [ 1, 2, 5 ]

    {-

    [1,2,4,6]
    first diff at index index 2: +`4`, -`5`
    ╷
    │ Expect.equalLists
    ╵
    first diff at index index 2: +`5`, -`4`
    [1,2,5]

    -}



## equalSets

```elm
equalSets : Set.Set comparable -> Set.Set comparable -> Expect.Expectation
```

 Passes if the arguments are equal sets.

    -- Passes
    Set.fromList [ 1, 2 ]
        |> Expect.equalSets (Set.fromList [ 1, 2 ])

Failures resemble code written in pipeline style, so you can tell
which argument is which, and reports which keys were missing from
or added to each set:

    -- Fails
    (Set.fromList [ 1, 2, 4, 6 ])
        |> Expect.equalSets (Set.fromList [ 1, 2, 5 ])

    {-

    Set.fromList [1,2,4,6]
    diff: -[ 5 ] +[ 4, 6 ]
    ╷
    │ Expect.equalSets
    ╵
    diff: +[ 5 ] -[ 4, 6 ]
    Set.fromList [1,2,5]

    -}



## err

```elm
err : Result.Result a b -> Expect.Expectation
```

 Passes if the
[`Result`](http://package.elm-lang.org/packages/elm-lang/core/latest/Result) is
an `Err` rather than `Ok`. This is useful for tests where you expect to get an
error but you don't care what the actual error is.

_(Tip: If your function returns a `Maybe` instead, consider `Expect.equal Nothing`.)_

    -- Passes
    String.toInt "not an int"
        |> Expect.err

Test failures will be printed with the unexpected `Ok` value contrasting with
any `Err`.

    -- Fails
    String.toInt "20"
        |> Expect.err

    {-

    Ok 20
    ╷
    │ Expect.err
    ╵
    Err _

    -}



## fail

```elm
fail : String.String -> Expect.Expectation
```

 Fails with the given message.

    import Json.Decode exposing (decodeString, int)
    import Test exposing (test)
    import Expect


    test "Json.Decode.int can decode the number 42." <|
        \_ ->
            case decodeString int "42" of
                Ok _ ->
                    Expect.pass

                Err err ->
                    Expect.fail err



## false

```elm
false : String.String -> Basics.Bool -> Expect.Expectation
```

 Passes if the argument is 'False', and otherwise fails with the given message.

    Expect.false "Expected the list not to be empty." (List.isEmpty [ 42 ])

    -- Passes because (List.isEmpty [ 42 ]) is False

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because (List.isEmpty []) is True
    List.isEmpty []
        |> Expect.false "Expected the list not to be empty."

    {-

    Expected the list not to be empty.

    -}



## greaterThan

```elm
greaterThan : comparable -> comparable -> Expect.Expectation
```

 Passes if the second argument is greater than the first.

    Expect.greaterThan -2 List.length []

    -- Passes because (0 > -2) is True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because (0 > 1) is False
    List.length []
        |> Expect.greaterThan 1

    {-

    0
    ╷
    │ Expect.greaterThan
    ╵
    1

    -}



## lessThan

```elm
lessThan : comparable -> comparable -> Expect.Expectation
```

 Passes if the second argument is less than the first.

    Expect.lessThan 1 (List.length [])

    -- Passes because (0 < 1) is True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because (0 < -1) is False
    List.length []
        |> Expect.lessThan -1


    {-

    0
    ╷
    │ Expect.lessThan
    ╵
    -1

    -}

Do not equate `Float` values; use [`notWithin`](#notWithin) instead.



## notEqual

```elm
notEqual : a -> a -> Expect.Expectation
```

 Passes if the arguments are not equal.

    -- Passes because (11 /= 100) is True
    90 + 10
        |> Expect.notEqual 11


    -- Fails because (100 /= 100) is False
    90 + 10
        |> Expect.notEqual 100

    {-

    100
    ╷
    │ Expect.notEqual
    ╵
    100

    -}



## notWithin

```elm
notWithin : Expect.FloatingPointTolerance -> Basics.Float -> Basics.Float -> Expect.Expectation
```

 Passes if (and only if) a call to `within` with the same arguments would have failed.


## ok

```elm
ok : Result.Result a b -> Expect.Expectation
```

 Passes if the
[`Result`](https://package.elm-lang.org/packages/lang/core/latest/Result) is
an `Ok` rather than `Err`. This is useful for tests where you expect not to see
an error, but you don't care what the actual result is.

_(Tip: If your function returns a `Maybe` instead, consider `Expect.notEqual Nothing`.)_

    -- Passes
    String.toInt "not an int"
        |> Expect.err

Test failures will be printed with the unexpected `Ok` value contrasting with
any `Err`.

    -- Fails
    String.toInt "20"
        |> Expect.err

    {-

    Ok 20
    ╷
    │ Expect.err
    ╵
    Err _

    -}



## onFail

```elm
onFail : String.String -> Expect.Expectation -> Expect.Expectation
```

 If the given expectation fails, replace its failure message with a custom one.

    "something"
        |> Expect.equal "something else"
        |> Expect.onFail "thought those two strings would be the same"



## pass

```elm
pass : Expect.Expectation
```

 Always passes.

    import Json.Decode exposing (decodeString, int)
    import Test exposing (test)
    import Expect


    test "Json.Decode.int can decode the number 42." <|
        \_ ->
            case decodeString int "42" of
                Ok _ ->
                    Expect.pass

                Err err ->
                    Expect.fail err



## true

```elm
true : String.String -> Basics.Bool -> Expect.Expectation
```

 Passes if the argument is 'True', and otherwise fails with the given message.

    Expect.true "Expected the list to be empty." (List.isEmpty [])

    -- Passes because (List.isEmpty []) is True

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because List.isEmpty returns False, but we expect True.
    List.isEmpty [ 42 ]
        |> Expect.true "Expected the list to be empty."

    {-

    Expected the list to be empty.

    -}



## within

```elm
within : Expect.FloatingPointTolerance -> Basics.Float -> Basics.Float -> Expect.Expectation
```

 Passes if the second and third arguments are equal within a tolerance
specified by the first argument. This is intended to avoid failing because of
minor inaccuracies introduced by floating point arithmetic.

    -- Fails because 0.1 + 0.2 == 0.30000000000000004 (0.1 is non-terminating in base 2)
    0.1 + 0.2 |> Expect.equal 0.3

    -- So instead write this test, which passes
    0.1 + 0.2 |> Expect.within (Absolute 0.000000001) 0.3

Failures resemble code written in pipeline style, so you can tell
which argument is which:

    -- Fails because 3.14 is not close enough to pi
    3.14 |> Expect.within (Absolute 0.0001) pi

    {-

    3.14
    ╷
    │ Expect.within Absolute 0.0001
    ╵
    3.141592653589793

    -}



# Fuzz

 This is a library of _fuzzers_ you can use to supply values to your fuzz
tests. You can typically pick out which ones you need according to their types.

A `Fuzzer a` knows how to create values of type `a` in two different ways. It
can create them randomly, so that your test's expectations are run against many
values. Fuzzers will often generate edge cases likely to find bugs. If the
fuzzer can make your test fail, it also knows how to "shrink" that failing input
into more minimal examples, some of which might also cause the tests to fail. In
this way, fuzzers can usually find the smallest or simplest input that
reproduces a bug.


## Common Fuzzers

@docs int, intRange, float, floatRange, percentage, string, bool, maybe, result, list, array


## Working with Fuzzers

@docs Fuzzer, oneOf, constant, map, map2, map3, map4, map5, andMap, frequency


## Tuple Fuzzers

Instead of using a tuple, consider using `fuzzN`.

@docs tuple, tuple3


## Uncommon Fuzzers

@docs custom, char, unit, order, invalid



## Fuzzer

```elm
type alias Fuzzer a =
    Fuzz.Internal.Fuzzer a
```

 The representation of fuzzers is opaque. Conceptually, a `Fuzzer a`
consists of a way to randomly generate values of type `a`, and a way to shrink
those values.


## andMap

```elm
andMap : Fuzz.Fuzzer a -> Fuzz.Fuzzer (a -> b) -> Fuzz.Fuzzer b
```

 Map over many fuzzers. This can act as `mapN` for `N > 5`.
The argument order is meant to accommodate chaining:

    map f aFuzzer
        |> andMap anotherFuzzer
        |> andMap aThirdFuzzer

Note that shrinking may be better using `mapN`.



## array

```elm
array : Fuzz.Fuzzer a -> Fuzz.Fuzzer (Array.Array a)
```

 Given a fuzzer of a type, create a fuzzer of an array of that type.
Generates random arrays of varying length, favoring shorter arrays.


## bool

```elm
bool : Fuzz.Fuzzer Basics.Bool
```

 A fuzzer for boolean values. It's useful when building up fuzzers of complex
types that contain a boolean somewhere.

We recommend against writing tests fuzzing over booleans. Write a unit test for
the true and false cases explicitly.



## char

```elm
char : Fuzz.Fuzzer Char.Char
```

 A fuzzer for char values. Generates random ascii chars disregarding the control
characters and the extended character set.


## constant

```elm
constant : a -> Fuzz.Fuzzer a
```

 Create a fuzzer that only and always returns the value provided, and performs no shrinking. This is hardly random,
and so this function is best used as a helper when creating more complicated fuzzers.


## custom

```elm
custom : Random.Generator a -> Shrink.Shrinker a -> Fuzz.Fuzzer a
```

 Build a custom `Fuzzer a` by providing a `Generator a` and a `Shrinker a`. Generators are defined in
[`elm/random`](http://package.elm-lang.org/packages/elm/random/latest). Shrinkers are defined in the [`Shrink`
module](https://package.elm-lang.org/packages/elm-explorations/test/latest/Shrink). It is not possible to extract the
generator and shrinker from an existing fuzzer.

This function should be considered for advanced uses. It's often easier to use `map` and other functions in this
module to create a fuzzer.

Here is an example for a record:

    import Random
    import Shrink

    type alias Position =
        { x : Int, y : Int }

    position : Fuzzer Position
    position =
        Fuzz.custom
            (Random.map2 Position (Random.int -100 100) (Random.int -100 100))
            (\{ x, y } -> Shrink.map Position (Shrink.int x) |> Shrink.andMap (Shrink.int y))

Here is an example for a custom union type, assuming there is already a `genName : Generator String` defined:

    type Question
        = Name String
        | Age Int

    question =
        let
            generator =
                Random.bool
                    |> Random.andThen
                        (\b ->
                            if b then
                                Random.map Name genName

                            else
                                Random.map Age (Random.int 0 120)
                        )

            shrinker question =
                case question of
                    Name n ->
                        Shrink.string n |> Shrink.map Name

                    Age i ->
                        Shrink.int i |> Shrink.map Age
        in
        Fuzz.custom generator shrinker



## float

```elm
float : Fuzz.Fuzzer Basics.Float
```

 A fuzzer for float values. It will never produce `NaN`, `Infinity`, or `-Infinity`.

It's possible for this fuzzer to generate any other floating-point value, but it
favors numbers between -50 and 50, numbers between -1 and 1, and especially zero.



## floatRange

```elm
floatRange : Basics.Float -> Basics.Float -> Fuzz.Fuzzer Basics.Float
```

 A fuzzer for float values within between a given minimum and maximum
value, inclusive. Shrunken values will also be within the range.


## frequency

```elm
frequency : List.List ( Basics.Float, Fuzz.Fuzzer a ) -> Fuzz.Fuzzer a
```

 Create a new `Fuzzer` by providing a list of probabilistic weights to use
with other fuzzers.
For example, to create a `Fuzzer` that has a 1/4 chance of generating an int
between -1 and -100, and a 3/4 chance of generating one between 1 and 100,
you could do this:

    Fuzz.frequency
        [ ( 1, Fuzz.intRange -100 -1 )
        , ( 3, Fuzz.intRange 1 100 )
        ]

There are a few circumstances in which this function will return an invalid
fuzzer, which causes it to fail any test that uses it:

  - If you provide an empty list of frequencies
  - If any of the weights are less than 0
  - If the weights sum to 0

Be careful recursively using this fuzzer in its arguments. Often using `map`
is a better way to do what you want. If you are fuzzing a tree-like data
structure, you should include a depth limit so to avoid infinite recursion, like
so:

    type Tree
        = Leaf
        | Branch Tree Tree

    tree : Int -> Fuzzer Tree
    tree i =
        if i <= 0 then
            Fuzz.constant Leaf

        else
            Fuzz.frequency
                [ ( 1, Fuzz.constant Leaf )
                , ( 2, Fuzz.map2 Branch (tree (i - 1)) (tree (i - 1)) )
                ]



## int

```elm
int : Fuzz.Fuzzer Basics.Int
```

 A fuzzer for int values. It will never produce `NaN`, `Infinity`, or `-Infinity`.

It's possible for this fuzzer to generate any 32-bit integer, signed or unsigned, but it favors
numbers between -50 and 50 and especially zero.



## intRange

```elm
intRange : Basics.Int -> Basics.Int -> Fuzz.Fuzzer Basics.Int
```

 A fuzzer for int values between a given minimum and maximum value,
inclusive. Shrunken values will also be within the range.

Remember that [Random.maxInt](http://package.elm-lang.org/packages/elm-lang/core/latest/Random#maxInt)
is the maximum possible int value, so you can do `intRange x Random.maxInt` to get all
the ints x or bigger.



## invalid

```elm
invalid : String.String -> Fuzz.Fuzzer a
```

 A fuzzer that is invalid for the provided reason. Any fuzzers built with it
are also invalid. Any tests using an invalid fuzzer fail.


## list

```elm
list : Fuzz.Fuzzer a -> Fuzz.Fuzzer (List.List a)
```

 Given a fuzzer of a type, create a fuzzer of a list of that type.
Generates random lists of varying length, favoring shorter lists.


## map

```elm
map : (a -> b) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b
```

 Map a function over a fuzzer. This applies to both the generated and the shrunken values.


## map2

```elm
map2 : (a -> b -> c) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c
```

 Map over two fuzzers.


## map3

```elm
map3 : (a -> b -> c -> d) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c -> Fuzz.Fuzzer d
```

 Map over three fuzzers.


## map4

```elm
map4 : (a -> b -> c -> d -> e) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c -> Fuzz.Fuzzer d -> Fuzz.Fuzzer e
```

 Map over four fuzzers.


## map5

```elm
map5 : (a -> b -> c -> d -> e -> f) -> Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c -> Fuzz.Fuzzer d -> Fuzz.Fuzzer e -> Fuzz.Fuzzer f
```

 Map over five fuzzers.


## maybe

```elm
maybe : Fuzz.Fuzzer a -> Fuzz.Fuzzer (Maybe.Maybe a)
```

 Given a fuzzer of a type, create a fuzzer of a maybe for that type.


## oneOf

```elm
oneOf : List.List (Fuzz.Fuzzer a) -> Fuzz.Fuzzer a
```

 Choose one of the given fuzzers at random. Each fuzzer has an equal chance
of being chosen; to customize the probabilities, use [`frequency`](#frequency).

    Fuzz.oneOf
        [ Fuzz.intRange 0 3
        , Fuzz.intRange 7 9
        ]



## order

```elm
order : Fuzz.Fuzzer Basics.Order
```

 A fuzzer for order values.


## percentage

```elm
percentage : Fuzz.Fuzzer Basics.Float
```

 A fuzzer for percentage values. Generates random floats between `0.0` and
`1.0`. It will test zero and one about 10% of the time each.


## result

```elm
result : Fuzz.Fuzzer error -> Fuzz.Fuzzer value -> Fuzz.Fuzzer (Result.Result error value)
```

 Given fuzzers for an error type and a success type, create a fuzzer for
a result.


## string

```elm
string : Fuzz.Fuzzer String.String
```

 Generates random printable ASCII strings of up to 1000 characters.

Shorter strings are more common, especially the empty string.



## tuple

```elm
tuple : ( Fuzz.Fuzzer a, Fuzz.Fuzzer b ) -> Fuzz.Fuzzer ( a, b )
```

 Turn a tuple of fuzzers into a fuzzer of tuples.


## tuple3

```elm
tuple3 : ( Fuzz.Fuzzer a, Fuzz.Fuzzer b, Fuzz.Fuzzer c ) -> Fuzz.Fuzzer ( a, b, c )
```

 Turn a 3-tuple of fuzzers into a fuzzer of 3-tuples.


## unit

```elm
unit : Fuzz.Fuzzer ()
```

 A fuzzer for the unit value. Unit is a type with only one value, commonly
used as a placeholder.


# Shrink

 Library containing a collection of basic shrinkers and helper functions to
make your own.

Shrinking is part of fuzzing, and the provided fuzzers have shrinkers already
built into them. You really only have to write your own shrinkers if you use
`Fuzz.custom`.


## Quick Reference

  - [Shrinking Basics](#shrinking-basics)
  - [Readymade Shrinkers](#readymade-shrinkers)
  - [Functions on Shrinkers](#functions-on-shrinkers)
  - [What are Shrinkers and why do we need them?](#what-are-shrinkers-and-why-do-we-need-them)


## Shrinking Basics

@docs Shrinker, shrink


## Readymade Shrinkers

@docs noShrink, unit, bool, order, int, atLeastInt, float, atLeastFloat, char, atLeastChar, character, string, maybe, result, lazylist, list, array, tuple, tuple3


## Functions on Shrinkers

@docs convert, keepIf, dropIf, merge, map, andMap


## What are Shrinkers and why do we need them?

Fuzzers consist of two parts; a Generator and a Shrinker.

The Generator takes a random Seed as input and returns a random value of
the desired type, based on the Seed. When a test fails on one of those random
values, the shrinker takes the failing value and makes it smaller/simpler for
you so you can guess more easily what property of that value caused the test
to fail.

Shrinking is a way to try and find the "smallest", "simplest" example that
fails, in order to give the tester better feedback on what went wrong.

Shrinkers are functions that, given a failing value, offer "smaller", "simpler"
values to test against.


### What is "small" (or "simple")?

That's kind of arbitrary, and depends on what kind of values you're fuzzing.
When you write your own Shrinker, you decide what is small for the kind of data
you're testing with.

Let's say I'm writing a Fuzzer for binary trees:

    -- randomly-generated binary trees might soon become unreadable
    type Tree a
        = Node (Tree a) (Tree a)
        | Leaf a

Now let's say its random Generator produced the following tree that makes the
test fail:

    Node
        (Node
            (Node
                (Node
                    (Leaf 888)
                    (Leaf 9090)
                )
                (Node
                    (Leaf -1)
                    (Node
                        (Leaf 731)
                        (Node
                            (Leaf 9621)
                            (Leaf -12)
                        )
                    )
                )
            )
            (Node
                (Leaf -350)
                (Leaf 124)
            )
        )
        (Node
            (Leaf 45)
            (Node
                (Leaf 123)
                (Node
                    (Leaf 999111)
                    (Leaf -148148)
                )
            )
        )

This is a pretty big tree, there are many nodes and leaves, and it's difficult
to tell which is responsible for the failing. If we don't attempt to shrink it,
the developer will have a hard time pointing out why it fails.

Now let's pass it through a shrinker, and test the resulting value until we find
this new value that still fails the test:

    Leaf -1

Nice, looks like a negative number in a `Leaf` could be the issue.


### How does shrinking work?

A shrinker takes a value and returns a short list of smaller values.

Once elm-test finds a failing fuzz test, it tries to shrink the input using
the shrinker. We'll then try the smaller values as inputs to that test. If one
of the smaller values also fail, we continue shrinking from there instead.
Once the shrinker says that there are no smaller values, or no smaller values
fail the fuzz test, we stop shrinking.

It's helpful to think of Shrinkers as returning simpler values rather than
smaller values. For example, 1 is smaller/simpler than 47142, and -1 is
smaller/simpler than -47142.

Whether or not the shrunken value is actually smaller isn't that important,
as long as we aren't shrinking in a loop. The bool shrinker shrinks True to
False, but not vice versa. If it did, and your test failed no matter if this
variable was True or False, there would always be a smaller/simpler value, so
we'd never stop shrinking! We would just re-test the same values over and over
again, forever!


### How do I make my own Shrinkers?

Shrinkers are deterministic, since they do not have access to a random number
generator. It's the generator part of the fuzzer that's meant to find the rare
edge cases; it's the shrinkers job to make the failures as understandable as
possible.

Shrinkers have to return a LazyList, something that works a bit like a list.
That LazyList may or may not have another element each time we ask for one,
and doesn't necessarily have them all committed to memory. That allows it to
take less space (interesting since there may be quite a lot of elements).

That LazyList should also provide a finite number of shrunk values (if it
provided an infinite number of them, tests using it might continue indefinitely
at the shrinking phase).

Shrinkers must never shrink values in a circle, like:

    loopinBooleanShrinker True == [ False ]

    loopinBooleanShrinker False == [ True ]

Doing so will also result in tests looping indefinitely, testing and re-testing
the same values in a circle.



## Shrinker

```elm
type alias Shrinker a =
    a -> Lazy.List.LazyList a
```

 The shrinker type.
A shrinker is a function that takes a value and returns a lazy list of values
that are in some sense "smaller" than the given value. If no such values exist,
then the shrinker should just return the empty list.


## andMap

```elm
andMap : Lazy.List.LazyList a -> Lazy.List.LazyList (a -> b) -> Lazy.List.LazyList b
```

 Apply a lazy list of functions on a lazy list of values.

The argument order is so that it is easy to use in `|>` chains.



## array

```elm
array : Shrink.Shrinker a -> Shrink.Shrinker (Array.Array a)
```

 Array shrinker constructor.
Takes a shrinker of values and returns a shrinker of Arrays.


## atLeastChar

```elm
atLeastChar : Char.Char -> Shrink.Shrinker Char.Char
```

 Construct a shrinker of chars which considers the given char to
be most minimal.


## atLeastFloat

```elm
atLeastFloat : Basics.Float -> Basics.Float -> Lazy.List.LazyList Basics.Float
```

 Construct a shrinker of floats which considers the given float to
be most minimal.


## atLeastInt

```elm
atLeastInt : Basics.Int -> Basics.Int -> Lazy.List.LazyList Basics.Int
```

 Construct a shrinker of ints which considers the given int to
be most minimal.


## bool

```elm
bool : Basics.Bool -> Lazy.List.LazyList Basics.Bool
```

 Shrinker of bools.


## char

```elm
char : Shrink.Shrinker Char.Char
```

 Shrinker of chars.


## character

```elm
character : Shrink.Shrinker Char.Char
```

 Shrinker of chars which considers the empty space as the most
minimal char and omits the control key codes.

Equivalent to:

    atLeastChar (Char.fromCode 32)



## convert

```elm
convert : (a -> b) -> (b -> a) -> Shrink.Shrinker a -> b -> Lazy.List.LazyList b
```

 Convert a Shrinker of a's into a Shrinker of b's using two inverse functions.
)
If you use this function as follows:

    shrinkerB =
        convert f g shrinkerA

Make sure that:

    `f(g(x)) == x` for all x
    -- (putting something into g then feeding the output into f must give back
    -- just that original something, whatever it is)

Or else this process will generate garbage.



## dropIf

```elm
dropIf : (a -> Basics.Bool) -> Shrink.Shrinker a -> Shrink.Shrinker a
```

 Filter out the results of a shrinker. The resulting shrinker
will only throw away shrinks which satisfy the given predicate.


## float

```elm
float : Basics.Float -> Lazy.List.LazyList Basics.Float
```

 Shrinker of floats.


## int

```elm
int : Basics.Int -> Lazy.List.LazyList Basics.Int
```

 Shrinker of integers.


## keepIf

```elm
keepIf : (a -> Basics.Bool) -> Shrink.Shrinker a -> a -> Lazy.List.LazyList a
```

 Filter out the results of a shrinker. The resulting shrinker
will only produce shrinks which satisfy the given predicate.


## lazylist

```elm
lazylist : Shrink.Shrinker a -> Lazy.List.LazyList a -> Lazy.List.LazyList (Lazy.List.LazyList a)
```

 Lazy List shrinker constructor. Takes a shrinker of values and returns a
shrinker of Lazy Lists. The lazy list being shrunk must be finite. (I mean
really, how do you shrink infinity?)


## list

```elm
list : Shrink.Shrinker a -> Shrink.Shrinker (List.List a)
```

 List shrinker constructor.
Takes a shrinker of values and returns a shrinker of Lists.


## map

```elm
map : (a -> b) -> Lazy.List.LazyList a -> Lazy.List.LazyList b
```

 Re-export of `Lazy.List.map`
This is useful in order to compose shrinkers, especially when used in
conjunction with `andMap`. For example:

    type alias Vector =
        { x : Float
        , y : Float
        , z : Float
        }

    vector : Shrinker Vector
    vector { x, y, z } =
        Vector
            |> map (float x)
            |> andMap (float y)
            |> andMap (float z)



## maybe

```elm
maybe : Shrink.Shrinker a -> Maybe.Maybe a -> Lazy.List.LazyList (Maybe.Maybe a)
```

 Maybe shrinker constructor.
Takes a shrinker of values and returns a shrinker of Maybes.


## merge

```elm
merge : Shrink.Shrinker a -> Shrink.Shrinker a -> a -> Lazy.List.LazyList a
```

 Merge two shrinkers. Generates all the values in the first
shrinker, and then all the non-duplicated values in the second
shrinker.


## noShrink

```elm
noShrink : a -> Lazy.List.LazyList a
```

 Perform no shrinking. Equivalent to the empty lazy list.


## order

```elm
order : Basics.Order -> Lazy.List.LazyList Basics.Order
```

 Shrinker of `Order` values.


## result

```elm
result : Shrink.Shrinker error -> Shrink.Shrinker value -> Result.Result error value -> Lazy.List.LazyList (Result.Result error value)
```

 Result shrinker constructor. Takes a shrinker of errors and a shrinker of
values and returns a shrinker of Results.


## shrink

```elm
shrink : (a -> Basics.Bool) -> Shrink.Shrinker a -> a -> a
```

 Perform shrinking. Takes a predicate that returns `True` if you want
shrinking to continue (most likely the failing test for which we are attempting
to shrink the value). Also takes the shrinker and the value to shrink.

It returns the shrunken value, or the input value if no shrunken values that
satisfy the predicate are found.



## string

```elm
string : Shrink.Shrinker String.String
```

 Shrinker of strings. Considers the empty string to be the most
minimal string and the space to be the most minimal char.

Equivalent to:

    convert String.fromList String.toList (list character)



## tuple

```elm
tuple : ( Shrink.Shrinker a, Shrink.Shrinker b ) -> ( a, b ) -> Lazy.List.LazyList ( a, b )
```

 2-Tuple shrinker constructor.
Takes a tuple of shrinkers and returns a shrinker of tuples.


## tuple3

```elm
tuple3 : ( Shrink.Shrinker a, Shrink.Shrinker b, Shrink.Shrinker c ) -> ( a, b, c ) -> Lazy.List.LazyList ( a, b, c )
```

 3-Tuple shrinker constructor.
Takes a tuple of shrinkers and returns a shrinker of tuples.


## unit

```elm
unit : Shrink.Shrinker ()
```

 Shrink the empty tuple. Equivalent to `noShrink`.


# Test

 A module containing functions for creating and managing tests.

@docs Test, test


## Organizing Tests

@docs describe, concat, todo, skip, only


## Fuzz Testing

@docs fuzz, fuzz2, fuzz3, fuzzWith, FuzzOptions



## FuzzOptions

```elm
type alias FuzzOptions =
    { runs : Basics.Int }
```

 Options [`fuzzWith`](#fuzzWith) accepts. Currently there is only one but this
API is designed so that it can accept more in the future.


### `runs`

The number of times to run each fuzz test. (Default is 100.)

    import Test exposing (fuzzWith)
    import Fuzz exposing (list, int)
    import Expect


    fuzzWith { runs = 350 } (list int) "List.length should always be positive" <|
        -- This anonymous function will be run 350 times, each time with a
        -- randomly-generated fuzzList value. (It will always be a list of ints
        -- because of (list int) above.)
        \fuzzList ->
            fuzzList
                |> List.length
                |> Expect.atLeast 0



## Test

```elm
type alias Test =
    Test.Internal.Test
```

 A test which has yet to be evaluated. When evaluated, it produces one
or more [`Expectation`](../Expect#Expectation)s.

See [`test`](#test) and [`fuzz`](#fuzz) for some ways to create a `Test`.



## concat

```elm
concat : List.List Test.Test -> Test.Test
```

 Run each of the given tests.

    concat [ testDecoder, testSorting ]



## describe

```elm
describe : String.String -> List.List Test.Test -> Test.Test
```

 Apply a description to a list of tests.

    import Test exposing (describe, test, fuzz)
    import Fuzz exposing (int)
    import Expect


    describe "List"
        [ describe "reverse"
            [ test "has no effect on an empty list" <|
                \_ ->
                    List.reverse []
                        |> Expect.equal []
            , fuzz int "has no effect on a one-item list" <|
                \num ->
                     List.reverse [ num ]
                        |> Expect.equal [ num ]
            ]
        ]

Passing an empty list will result in a failing test, because you either made a
mistake or are creating a placeholder.



## fuzz

```elm
fuzz : Fuzz.Fuzzer a -> String.String -> (a -> Expect.Expectation) -> Test.Test
```

 Take a function that produces a test, and calls it several (usually 100) times, using a randomly-generated input
from a [`Fuzzer`](http://package.elm-lang.org/packages/elm-community/elm-test/latest/Fuzz) each time. This allows you to
test that a property that should always be true is indeed true under a wide variety of conditions. The function also
takes a string describing the test.

These are called "[fuzz tests](https://en.wikipedia.org/wiki/Fuzz_testing)" because of the randomness.
You may find them elsewhere called [property-based tests](http://blog.jessitron.com/2013/04/property-based-testing-what-is-it.html),
[generative tests](http://www.pivotaltracker.com/community/tracker-blog/generative-testing), or
[QuickCheck-style tests](https://en.wikipedia.org/wiki/QuickCheck).

    import Test exposing (fuzz)
    import Fuzz exposing (list, int)
    import Expect


    fuzz (list int) "List.length should always be positive" <|
        -- This anonymous function will be run 100 times, each time with a
        -- randomly-generated fuzzList value.
        \fuzzList ->
            fuzzList
                |> List.length
                |> Expect.atLeast 0



## fuzz2

```elm
fuzz2 : Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> String.String -> (a -> b -> Expect.Expectation) -> Test.Test
```

 Run a [fuzz test](#fuzz) using two random inputs.

This is a convenience function that lets you skip calling [`Fuzz.tuple`](Fuzz#tuple).

See [`fuzzWith`](#fuzzWith) for an example of writing this in tuple style.

    import Test exposing (fuzz2)
    import Fuzz exposing (list, int)


    fuzz2 (list int) int "List.reverse never influences List.member" <|
        \nums target ->
            List.member target (List.reverse nums)
                |> Expect.equal (List.member target nums)



## fuzz3

```elm
fuzz3 : Fuzz.Fuzzer a -> Fuzz.Fuzzer b -> Fuzz.Fuzzer c -> String.String -> (a -> b -> c -> Expect.Expectation) -> Test.Test
```

 Run a [fuzz test](#fuzz) using three random inputs.

This is a convenience function that lets you skip calling [`Fuzz.tuple3`](Fuzz#tuple3).



## fuzzWith

```elm
fuzzWith : Test.FuzzOptions -> Fuzz.Fuzzer a -> String.String -> (a -> Expect.Expectation) -> Test.Test
```

 Run a [`fuzz`](#fuzz) test with the given [`FuzzOptions`](#FuzzOptions).

Note that there is no `fuzzWith2`, but you can always pass more fuzz values in
using [`Fuzz.tuple`](Fuzz#tuple), [`Fuzz.tuple3`](Fuzz#tuple3),
for example like this:

    import Test exposing (fuzzWith)
    import Fuzz exposing (tuple, list, int)
    import Expect


    fuzzWith { runs = 4200 }
        (tuple ( list int, int ))
        "List.reverse never influences List.member" <|
            \(nums, target) ->
                List.member target (List.reverse nums)
                    |> Expect.equal (List.member target nums)



## only

```elm
only : Test.Test -> Test.Test
```

 Returns a [`Test`](#Test) that causes other tests to be skipped, and
only runs the given one.

Calls to `only` aren't meant to be committed to version control. Instead, use
them when you want to focus on getting a particular subset of your tests to pass.
If you use `only`, your entire test suite will fail, even if
each of the individual tests pass. This is to help avoid accidentally
committing a `only` to version control.

If you you use `only` on multiple tests, only those tests will run. If you
put a `only` inside another `only`, only the outermost `only`
will affect which tests gets run.

See also [`skip`](#skip). Note that `skip` takes precedence over `only`;
if you use a `skip` inside an `only`, it will still get skipped, and if you use
an `only` inside a `skip`, it will also get skipped.

    describe "List"
        [ only <|
            describe "reverse"
                [ test "has no effect on an empty list" <|
                    \_ ->
                        List.reverse []
                            |> Expect.equal []
                , fuzz int "has no effect on a one-item list" <|
                    \num ->
                        List.reverse [ num ]
                            |> Expect.equal [ num ]
                ]
        , test "This will not get run, because of the `only` above!" <|
            \_ ->
                List.length []
                    |> Expect.equal 0
        ]



## skip

```elm
skip : Test.Test -> Test.Test
```

 Returns a [`Test`](#Test) that gets skipped.

Calls to `skip` aren't meant to be committed to version control. Instead, use
it when you want to focus on getting a particular subset of your tests to
pass. If you use `skip`, your entire test suite will fail, even if
each of the individual tests pass. This is to help avoid accidentally
committing a `skip` to version control.

See also [`only`](#only). Note that `skip` takes precedence over `only`;
if you use a `skip` inside an `only`, it will still get skipped, and if you use
an `only` inside a `skip`, it will also get skipped.

    describe "List"
        [ skip <|
            describe "reverse"
                [ test "has no effect on an empty list" <|
                    \_ ->
                        List.reverse []
                            |> Expect.equal []
                , fuzz int "has no effect on a one-item list" <|
                    \num ->
                        List.reverse [ num ]
                            |> Expect.equal [ num ]
                ]
        , test "This is the only test that will get run; the other was skipped!" <|
            \_ ->
                List.length []
                    |> Expect.equal 0
        ]



## test

```elm
test : String.String -> (() -> Expect.Expectation) -> Test.Test
```

 Return a [`Test`](#Test) that evaluates a single
[`Expectation`](../Expect#Expectation).

    import Test exposing (fuzz)
    import Expect


    test "the empty list has 0 length" <|
        \_ ->
            List.length []
                |> Expect.equal 0



## todo

```elm
todo : String.String -> Test.Test
```

 Returns a [`Test`](#Test) that is "TODO" (not yet implemented). These tests
always fail, but test runners will only include them in their output if there
are no other failures.

These tests aren't meant to be committed to version control. Instead, use them
when you're brainstorming lots of tests you'd like to write, but you can't
implement them all at once. When you replace `todo` with a real test, you'll be
able to see if it fails without clutter from tests still not implemented. But,
unlike leaving yourself comments, you'll be prompted to implement these tests
because your suite will fail.

    describe "a new thing"
        [ todo "does what is expected in the common case"
        , todo "correctly handles an edge case I just thought of"
        ]

This functionality is similar to "pending" tests in other frameworks, except
that a TODO test is considered failing but a pending test often is not.



# Test.Html.Event

 This module lets you simulate events on `Html` values and expect that
they result in certain `Msg` values being sent to `update`.


## Simulating Events

@docs Event, simulate, expect, toResult


## Event Builders

@docs custom, click, doubleClick, mouseDown, mouseUp, mouseEnter, mouseLeave, mouseOver, mouseOut, input, check, submit, blur, focus



## Event

```elm
-- Opaque type: Event msg (constructors not exposed)
```

 A simulated event.

See [`simulate`](#simulate).



## blur

```elm
blur : ( String.String, Json.Encode.Value )
```

 A [`blur`](https://developer.mozilla.org/en-US/docs/Web/Events/blur) event.


## check

```elm
check : Basics.Bool -> ( String.String, Json.Encode.Value )
```

 A [`change`](https://developer.mozilla.org/en-US/docs/Web/Events/change) event
where `event.target.checked` is set to the given `Bool` value.


## click

```elm
click : ( String.String, Json.Encode.Value )
```

 A [`click`](https://developer.mozilla.org/en-US/docs/Web/Events/click) event.


## custom

```elm
custom : String.String -> Json.Encode.Value -> ( String.String, Json.Encode.Value )
```

 Simulate a custom event. The `String` is the event name, and the `Value` is the event object
the browser would send to the event listener callback.

    import Test.Html.Event as Event
    import Json.Encode as Encode exposing (Value)


    type Msg
        = Change String


    test "Input produces expected Msg" <|
        \() ->
            let
                simulatedEventObject : Value
                simulatedEventObject =
                    Encode.object
                        [ ( "target"
                          , Encode.object [ ( "value", Encode.string "cats" ) ]
                          )
                        ]
            in
                Html.input [ onInput Change ] [ ]
                    |> Query.fromHtml
                    |> Event.simulate (Event.custom "input" simulatedEventObject)
                    |> Event.expect (Change "cats")



## doubleClick

```elm
doubleClick : ( String.String, Json.Encode.Value )
```

 A [`dblclick`](https://developer.mozilla.org/en-US/docs/Web/Events/dblclick) event.


## expect

```elm
expect : msg -> Test.Html.Event.Event msg -> Expect.Expectation
```

 Passes if the given message is triggered by the simulated event.

    import Test.Html.Event as Event

    type Msg
        = Change String


    test "Input produces expected Msg" <|
        \() ->
            Html.input [ onInput Change ] [ ]
                |> Query.fromHtml
                |> Event.simulate (Event.input "cats")
                |> Event.expect (Change "cats")



## focus

```elm
focus : ( String.String, Json.Encode.Value )
```

 A [`focus`](https://developer.mozilla.org/en-US/docs/Web/Events/focus) event.


## input

```elm
input : String.String -> ( String.String, Json.Encode.Value )
```

 An [`input`](https://developer.mozilla.org/en-US/docs/Web/Events/input) event.


## mouseDown

```elm
mouseDown : ( String.String, Json.Encode.Value )
```

 A [`mousedown`](https://developer.mozilla.org/en-US/docs/Web/Events/mousedown) event.


## mouseEnter

```elm
mouseEnter : ( String.String, Json.Encode.Value )
```

 A [`mouseenter`](https://developer.mozilla.org/en-US/docs/Web/Events/mouseenter) event.


## mouseLeave

```elm
mouseLeave : ( String.String, Json.Encode.Value )
```

 A [`mouseleave`](https://developer.mozilla.org/en-US/docs/Web/Events/mouseleave) event.


## mouseOut

```elm
mouseOut : ( String.String, Json.Encode.Value )
```

 A [`mouseout`](https://developer.mozilla.org/en-US/docs/Web/Events/mouseout) event.


## mouseOver

```elm
mouseOver : ( String.String, Json.Encode.Value )
```

 A [`mouseover`](https://developer.mozilla.org/en-US/docs/Web/Events/mouseover) event.


## mouseUp

```elm
mouseUp : ( String.String, Json.Encode.Value )
```

 A [`mouseup`](https://developer.mozilla.org/en-US/docs/Web/Events/mouseup) event.


## simulate

```elm
simulate : ( String.String, Json.Encode.Value ) -> Test.Html.Query.Single msg -> Test.Html.Event.Event msg
```

 Simulate an event on a node.

    import Test.Html.Event as Event

    type Msg
        = Change String


    test "Input produces expected Msg" <|
        \() ->
            Html.input [ onInput Change ] [ ]
                |> Query.fromHtml
                |> Event.simulate (Event.input "cats")
                |> Event.expect (Change "cats")



## submit

```elm
submit : ( String.String, Json.Encode.Value )
```

 A [`submit`](https://developer.mozilla.org/en-US/docs/Web/Events/submit) event.


## toResult

```elm
toResult : Test.Html.Event.Event msg -> Result.Result String.String msg
```

 Returns a Result with the Msg produced by the event simulated on a node.
Note that Event.expect gives nicer messages; this is generally more useful
when testing that an event handler is _not_ present.

    import Test.Html.Event as Event


    test "Input produces expected Msg" <|
        \() ->
            Html.input [ onInput Change ] [ ]
                |> Query.fromHtml
                |> Event.simulate (Event.input "cats")
                |> Event.toResult
                |> Expect.equal (Ok (Change "cats"))



# Test.Html.Query

 Querying HTML structure.

@docs Single, Multiple, fromHtml


## Querying

@docs find, findAll, children, first, index, keep


## Expecting

@docs count, contains, has, hasNot, each



## Multiple

```elm
type alias Multiple msg =
    Test.Html.Query.Internal.Multiple msg
```

 A query that may find any number of elements, including zero.

Contrast with [`Single`](#Single).



## Single

```elm
type alias Single msg =
    Test.Html.Query.Internal.Single msg
```

 A query that expects to find exactly one element.

Contrast with [`Multiple`](#Multiple).



## children

```elm
children : List.List Test.Html.Selector.Internal.Selector -> Test.Html.Query.Single msg -> Test.Html.Query.Multiple msg
```

 Return the matched element's immediate child elements.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The <ul> only has <li> children" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [ class "item"] [ text "first item" ]
                    , li [ class "item selected"] [ text "second item" ]
                    , li [ class "item"] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.find [ class "items" ]
                |> Query.children [ class "selected" ]
                |> Query.count (Expect.equal 1)



## contains

```elm
contains : List.List (Html.Html msg) -> Test.Html.Query.Single msg -> Expect.Expectation
```

 Expect the element to have at least one descendant matching

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The list has two li: one with the text \"third item\" and \
        another one with \"first item\"" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.contains
                    [ li [] [ text "third item" ]
                    , li [] [ text "first item" ]
                    ]



## count

```elm
count : (Basics.Int -> Expect.Expectation) -> Test.Html.Query.Multiple msg -> Expect.Expectation
```

 Expect the number of elements matching the query fits the given expectation.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag)
    import Expect


    test "The list has three items" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.findAll [ tag "li" ]
                |> Query.count (Expect.equal 3)



## each

```elm
each : (Test.Html.Query.Single msg -> Expect.Expectation) -> Test.Html.Query.Multiple msg -> Expect.Expectation
```

 Expect that a [`Single`](#Single) expectation will hold true for each of the
[`Multiple`](#Multiple) matched elements.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The list has both the classes 'items' and 'active'" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.findAll [ tag "ul" ]
                |> Query.each
                    (Expect.all
                        [ Query.has [ tag "ul" ]
                        , Query.has [ classes [ "items", "active" ] ]
                        ]
                    )



## find

```elm
find : List.List Test.Html.Selector.Internal.Selector -> Test.Html.Query.Single msg -> Test.Html.Query.Single msg
```

 Find exactly one descendant element which matches all the given selectors.
If no descendants match, or if more than one matches, the test will fail.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The list has both the classes 'items' and 'active'" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.find [ tag "ul" ]
                |> Query.has [ classes [ "items", "active" ] ]



## findAll

```elm
findAll : List.List Test.Html.Selector.Internal.Selector -> Test.Html.Query.Single msg -> Test.Html.Query.Multiple msg
```

 Find the descendant elements which match all the given selectors.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag)
    import Expect


    test "The list has three items" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.findAll [ tag "li" ]
                |> Query.count (Expect.equal 3)



## first

```elm
first : Test.Html.Query.Multiple msg -> Test.Html.Query.Single msg
```

 Return the first element in a match. If there were no matches, the test
will fail.

`Query.first` is a shorthand for `Query.index 0` - they do the same thing.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The first <li> is called 'first item'" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.findAll [ tag "li" ]
                |> Query.first
                |> Query.has [ text "first item" ]



## fromHtml

```elm
fromHtml : Html.Html msg -> Test.Html.Query.Single msg
```

 Translate a `Html` value into a `Single` query. This is how queries
typically begin.

    import Html
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (text)


    test "Button has the expected text" <|
        \() ->
            Html.button [] [ Html.text "I'm a button!" ]
                |> Query.fromHtml
                |> Query.has [ text "I'm a button!" ]



## has

```elm
has : List.List Test.Html.Selector.Internal.Selector -> Test.Html.Query.Single msg -> Expect.Expectation
```

 Expect the element to match all of the given selectors.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The list has both the classes 'items' and 'active'" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.find [ tag "ul" ]
                |> Query.has [ tag "ul", classes [ "items", "active" ] ]



## hasNot

```elm
hasNot : List.List Test.Html.Selector.Internal.Selector -> Test.Html.Query.Single msg -> Expect.Expectation
```

 Expect the element to **not** match all of the given selectors.

    import Html exposing (div)
    import Html.Attributes as Attributes
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, class)


    test "The div element has no progress-bar class" <|
        \() ->
            div [ Attributes.class "button" ] []
                |> Query.fromHtml
                |> Query.find [ tag "div" ]
                |> Query.hasNot [ tag "div", class "progress-bar" ]



## index

```elm
index : Basics.Int -> Test.Html.Query.Multiple msg -> Test.Html.Query.Single msg
```

 Return the element in a match at the given index. For example,
`Query.index 0` would match the first element, and `Query.index 1` would match
the second element.

You can pass negative numbers to get elements from the end - for example, `Query.index -1`
will match the last element, and `Query.index -2` will match the second-to-last.

If the index falls outside the bounds of the match, the test will fail.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, classes)


    test "The second <li> is called 'second item'" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ text "first item" ]
                    , li [] [ text "second item" ]
                    , li [] [ text "third item" ]
                    ]
                ]
                |> Query.fromHtml
                |> Query.findAll [ tag "li" ]
                |> Query.index 1
                |> Query.has [ text "second item" ]



## keep

```elm
keep : Test.Html.Selector.Internal.Selector -> Test.Html.Query.Multiple msg -> Test.Html.Query.Multiple msg
```

 Find the descendant elements of the result of `findAll` which match all the given selectors.

    import Html exposing (div, ul, li)
    import Html.Attributes exposing (class)
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag)
    import Expect


    test "The list has three items" <|
        \() ->
            div []
                [ ul [ class "items active" ]
                    [ li [] [ a [] [ text "first item" ]]
                    , li [] [ a [] [ text "second item" ]]
                    , li [] [ a [] [ text "third item" ]]
                    , li [] [ button [] [ text "button" ]]
                    ]
                ]
                |> Query.fromHtml
                |> Query.findAll [ tag "li" ]
                |> Query.keep ( tag "a" )
                |> Expect.all
                    [ Query.each (Query.has [ tag "a" ])
                    , Query.first >> Query.has [ text "first item" ]
                    ]



# Test.Html.Selector

 Selecting HTML elements.

@docs Selector


## General Selectors

@docs tag, text, containing, attribute, all


## Attributes

@docs id, class, classes, exactClassName, style, checked, selected, disabled



## Selector

```elm
type alias Selector =
    Test.Html.Selector.Internal.Selector
```

 A selector used to filter sets of elements.


## all

```elm
all : List.List Test.Html.Selector.Selector -> Test.Html.Selector.Selector
```

 Combine the given selectors into one which requires all of them to match.

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (class, text, all, Selector)


    replyBtnSelector : Selector
    replyBtnSelector =
        all [ class "btn", text "Reply" ]


    test "Button has the class 'btn' and the text 'Reply'" <|
        \() ->
            Html.button [ Attr.class "btn btn-large" ] [ Html.text "Reply" ]
                |> Query.fromHtml
                |> Query.has [ replyBtnSelector ]



## attribute

```elm
attribute : Html.Attribute Basics.Never -> Test.Html.Selector.Selector
```

 Matches elements that have the given attribute in a way that makes sense
given their semantics in `Html`.


## checked

```elm
checked : Basics.Bool -> Test.Html.Selector.Selector
```

 Matches elements that have a
[`checked`](http://package.elm-lang.org/packages/elm-lang/html/latest/Html-Attributes#checked)
attribute with the given value.


## class

```elm
class : String.String -> Test.Html.Selector.Selector
```

 Matches elements that have the given class (and possibly others as well).

To match multiple classes at once, use [`classes`](#classes) instead.

To match the element's exact class attribute string, use [`exactClassName`](#exactClassName).

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (class)


    test "Button has the class btn-large" <|
        \() ->
            Html.button [ Attr.class "btn btn-large" ] [ Html.text "Reply" ]
                |> Query.fromHtml
                |> Query.has [ class "btn-large" ]



## classes

```elm
classes : List.List String.String -> Test.Html.Selector.Selector
```

 Matches elements that have all the given classes (and possibly others as well).

When you only care about one class instead of several, you can use
[`class`](#class) instead of passing this function a list with one value in it.

To match the element's exact class attribute string, use [`exactClassName`](#exactClassName).

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (classes)


    test "Button has the classes btn and btn-large" <|
        \() ->
            Html.button [ Attr.class "btn btn-large" ] [ Html.text "Reply" ]
                |> Query.fromHtml
                |> Query.has [ classes [ "btn", "btn-large" ] ]



## containing

```elm
containing : List.List Test.Html.Selector.Selector -> Test.Html.Selector.Selector
```

 Matches elements whose descendants match the given selectors.

(You will get the element and **not** the descendant.)

This is especially useful to find elements which contain specific
text somewhere in their descendants.

    import Html
    import Html.Events exposing (onClick)
    import Test exposing (test)
    import Test.Html.Event as Event
    import Test.Html.Query as Query
    import Test.Html.Selector exposing (containing, tag)

    test : Test
    test =
        test "..." <|
            Html.div []
                [ Html.button [ onClick NopeMsg ] [ Html.text "not me" ]
                , Html.button [ onClick ClickedMsg ] [ Html.text "click me" ]
                ]
                |> Query.find
                    [ tag "button"
                    , containing [ text "click me" ]
                    ]
                |> Event.simulate Event.click
                |> Event.expect ClickedMsg



## disabled

```elm
disabled : Basics.Bool -> Test.Html.Selector.Selector
```

 Matches elements that have a
[`disabled`](http://package.elm-lang.org/packages/elm-lang/html/latest/Html-Attributes#disabled)
attribute with the given value.


## exactClassName

```elm
exactClassName : String.String -> Test.Html.Selector.Selector
```

 Matches the element's exact class attribute string.

This is used less often than [`class`](#class), [`classes`](#classes) or
[`attribute`](#attribute), which check for the _presence_ of a class as opposed
to matching the entire class attribute exactly.

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (exactClassName)


    test "Button has the exact class 'btn btn-large'" <|
        \() ->
            Html.button [ Attr.class "btn btn-large" ] [ Html.text "Reply" ]
                |> Query.fromHtml
                |> Query.has [ exactClassName "btn btn-large" ]



## id

```elm
id : String.String -> Test.Html.Selector.Selector
```

 Matches elements that have the given `id` attribute.

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (id, text)


    test "the welcome <h1> says hello!" <|
        \() ->
            Html.div []
                [ Html.h1 [ Attr.id "welcome" ] [ Html.text "Hello!" ] ]
                |> Query.fromHtml
                |> Query.find [ id "welcome" ]
                |> Query.has [ text "Hello!" ]



## selected

```elm
selected : Basics.Bool -> Test.Html.Selector.Selector
```

 Matches elements that have a
[`selected`](http://package.elm-lang.org/packages/elm-lang/html/latest/Html-Attributes#selected)
attribute with the given value.


## style

```elm
style : String.String -> String.String -> Test.Html.Selector.Selector
```

 Matches elements that have the given style properties (and possibly others as well).

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (classes)


    test "the Reply button has red text" <|
        \() ->
            Html.div []
                [ Html.button
                    [ Attr.style "color" "red" ]
                    [ Html.text "Reply" ]
                ]
                |> Query.has [ style "color" "red" ]



## tag

```elm
tag : String.String -> Test.Html.Selector.Selector
```

 Matches elements that have the given tag.

    import Html
    import Html.Attributes as Attr
    import Test.Html.Query as Query
    import Test exposing (test)
    import Test.Html.Selector exposing (tag, text)


    test "the welcome <h1> says hello!" <|
        \() ->
            Html.div []
                [ Html.h1 [ Attr.id "welcome" ] [ Html.text "Hello!" ] ]
                |> Query.fromHtml
                |> Query.find [ tag "h1" ]
                |> Query.has [ text "Hello!" ]



## text

```elm
text : String.String -> Test.Html.Selector.Selector
```

 Matches elements that have a
[`text`](http://package.elm-lang.org/packages/elm-lang/html/latest/Html-Attributes#text)
attribute with the given value.


# Test.Runner

 This is an "experts only" module that exposes functions needed to run and
display tests. A typical user will use an existing runner library for Node or
the browser, which is implemented using this interface. A list of these runners
can be found in the `README`.


## Runner

@docs Runner, SeededRunners, fromTest


## Expectations

@docs getFailureReason, isTodo


## Formatting

@docs formatLabels


## Fuzzers

These functions give you the ability to run fuzzers separate of running fuzz tests.

@docs Shrinkable, fuzz, shrink



## Runner

```elm
type alias Runner =
    { run : () -> List.List Expect.Expectation, labels : List.List String.String }
```

 A function which, when evaluated, produces a list of expectations. Also a
list of labels which apply to this outcome.


## SeededRunners

```elm
type SeededRunners
    = Plain (List.List Test.Runner.Runner)
    | Only (List.List Test.Runner.Runner)
    | Skipping (List.List Test.Runner.Runner)
    | Invalid (String.String)
```

 Test Runners which have had seeds distributed to them, and which are now
either invalid or are ready to run. Seeded runners include some metadata:

  - `Invalid` runners had a problem (e.g. two sibling tests had the same description) making them un-runnable.
  - `Only` runners can be run, but `Test.only` was used somewhere, so ultimately they will lead to a failed test run even if each test that gets run passes.
  - `Skipping` runners can be run, but `Test.skip` was used somewhere, so ultimately they will lead to a failed test run even if each test that gets run passes.
  - `Plain` runners are ready to run, and have none of these issues.



## Shrinkable

```elm
-- Opaque type: Shrinkable a (constructors not exposed)
```

 A `Shrinkable a` is an opaque type that allows you to obtain a value of type
`a` that is smaller than the one you've previously obtained.


## formatLabels

```elm
formatLabels : (String.String -> format) -> (String.String -> format) -> List.List String.String -> List.List format
```

 A standard way to format descriptions and test labels, to keep things
consistent across test runner implementations.

The HTML, Node, String, and Log runners all use this.

What it does:

  - drop any labels that are empty strings
  - format the first label differently from the others
  - reverse the resulting list

Example:

    [ "the actual test that failed"
    , "nested description failure"
    , "top-level description failure"
    ]
    |> formatLabels ((++) "↓ ") ((++) "✗ ")

    {-
    [ "↓ top-level description failure"
    , "↓ nested description failure"
    , "✗ the actual test that failed"
    ]
    -}



## fromTest

```elm
fromTest : Basics.Int -> Random.Seed -> Test.Test -> Test.Runner.SeededRunners
```

 Convert a `Test` into `SeededRunners`.

In order to run any fuzz tests that the `Test` may have, it requires a default run count as well
as an initial `Random.Seed`. `100` is a good run count. To obtain a good random seed, pass a
random 32-bit integer to `Random.initialSeed`. You can obtain such an integer by running
`Math.floor(Math.random()*0xFFFFFFFF)` in Node. It's typically fine to hard-code this value into
your Elm code; it's easy and makes your tests reproducible.



## fuzz

```elm
fuzz : Fuzz.Fuzzer a -> Result.Result String.String (Random.Generator ( a, Test.Runner.Shrinkable a ))
```

 Given a fuzzer, return a random generator to produce a value and a
Shrinkable. The value is what a fuzz test would have received as input.


## getFailureReason

```elm
getFailureReason : Expect.Expectation -> Maybe.Maybe { given : Maybe.Maybe String.String, description : String.String, reason : Test.Runner.Failure.Reason }
```

 Return `Nothing` if the given [`Expectation`](#Expectation) is a [`pass`](#pass).

If it is a [`fail`](#fail), return a record containing the expectation
description, the [`Reason`](#Reason) the test failed, and the given inputs if
it was a fuzz test. (If it was not a fuzz test, the record's `given` field
will be `Nothing`).

For example:

    getFailureReason (Expect.equal 1 2)
    -- Just { reason = Equal 1 2, description = "Expect.equal", given = Nothing }

    getFailureReason (Expect.equal 1 1)
    -- Nothing



## isTodo

```elm
isTodo : Expect.Expectation -> Basics.Bool
```

 Determine if an expectation was created by a call to `Test.todo`. Runners
may treat these tests differently in their output.


## shrink

```elm
shrink : Basics.Bool -> Test.Runner.Shrinkable a -> Maybe.Maybe ( a, Test.Runner.Shrinkable a )
```

 Given a Shrinkable, attempt to shrink the value further. Pass `False` to
indicate that the last value you've seen (from either `fuzz` or this function)
caused the test to **fail**. This will attempt to find a smaller value. Pass
`True` if the test passed. If you have already seen a failure, this will attempt
to shrink that failure in another way. In both cases, it may be impossible to
shrink the value, represented by `Nothing`.


# Test.Runner.Failure

 The reason a test failed.

@docs Reason, InvalidReason, format



## InvalidReason

```elm
type InvalidReason
    = EmptyList
    | NonpositiveFuzzCount
    | InvalidFuzzer
    | BadDescription
    | DuplicatedName
```

 The reason a test run was invalid.

Test runners should report these to the user in whatever format is appropriate.



## Reason

```elm
type Reason
    = Custom
    | Equality (String.String) (String.String)
    | Comparison (String.String) (String.String)
    | ListDiff (List.List String.String) (List.List String.String)
    | CollectionDiff ({ expected : String.String, actual : String.String, extra : List.List String.String, missing : List.List String.String })
    | TODO
    | Invalid (Test.Runner.Failure.InvalidReason)
```

 The reason a test failed.

Test runners can use this to provide nice output, e.g. by doing diffs on the
two parts of an `Expect.equal` failure.



## format

```elm
format : String.String -> Test.Runner.Failure.Reason -> String.String
```

 DEPRECATED. In the future, test runners should implement versions of this
that make sense for their own environments.

Format test run failures in a reasonable way.


