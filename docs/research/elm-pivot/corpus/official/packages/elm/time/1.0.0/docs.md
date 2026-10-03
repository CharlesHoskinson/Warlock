# official/packages/elm/time/1.0.0/docs.json
Source: https://package.elm-lang.org/packages/elm/time/1.0.0/docs.json

# Time

 Library for working with time and time zones.

# Time
@docs Posix, now, every, posixToMillis, millisToPosix

# Time Zones
@docs Zone, utc, here

# Human Times
@docs toYear, toMonth, toDay, toWeekday, toHour, toMinute, toSecond, toMillis

# Weeks and Months
@docs Weekday, Month

# For Package Authors
@docs customZone, getZoneName, ZoneName



## Month

```elm
type Month
    = Jan
    | Feb
    | Mar
    | Apr
    | May
    | Jun
    | Jul
    | Aug
    | Sep
    | Oct
    | Nov
    | Dec
```

 Represents a `Month` so that you can convert it to a `String` or `Int`
however you please. For example, if you need the Danish representation, you
can say:

    toDanishMonth : Month -> String
    toDanishMonth month =
      case month of
        Jan -> "januar"
        Feb -> "februar"
        Mar -> "marts"
        Apr -> "april"
        May -> "maj"
        Jun -> "juni"
        Jul -> "juli"
        Aug -> "august"
        Sep -> "september"
        Oct -> "oktober"
        Nov -> "november"
        Dec -> "december"


## Posix

```elm
-- Opaque type: Posix (constructors not exposed)
```

 A computer representation of time. It is the same all over Earth, so if we
have a phone call or meeting at a certain POSIX time, there is no ambiguity.

It is very hard for humans to _read_ a POSIX time though, so we use functions
like [`toHour`](#toHour) and [`toMinute`](#toMinute) to `view` them.


## Weekday

```elm
type Weekday
    = Mon
    | Tue
    | Wed
    | Thu
    | Fri
    | Sat
    | Sun
```

 Represents a `Weekday` so that you can convert it to a `String` or `Int`
however you please. For example, if you need the Japanese representation, you
can say:

    toJapaneseWeekday : Weekday -> String
    toJapaneseWeekday weekday =
      case weekday of
        Mon -> "月"
        Tue -> "火"
        Wed -> "水"
        Thu -> "木"
        Fri -> "金"
        Sat -> "土"
        Sun -> "日"


## Zone

```elm
-- Opaque type: Zone (constructors not exposed)
```

 Information about a particular time zone.

The [IANA Time Zone Database][iana] tracks things like UTC offsets and
daylight-saving rules so that you can turn a `Posix` time into local times
within a time zone.

See [`utc`](#utc), [`here`](#here), and [`Browser.Env`][env] to learn how to
obtain `Zone` values.

[iana]: https://www.iana.org/time-zones
[env]: /packages/elm/browser/latest/Browser#Env


## ZoneName

```elm
type ZoneName
    = Name (String.String)
    | Offset (Basics.Int)
```

 **Intended for package authors.**

The `getZoneName` function relies on a JavaScript API that is not supported
in all browsers yet, so it can return the following:

    -- in more recent browsers
    Name "Europe/Moscow"
    Name "America/Havana"

    -- in older browsers
    Offset 180
    Offset -300

So if the real info is not available, it will tell you the current UTC offset
in minutes, just like what `here` uses to make zones like `customZone -60 []`.


## customZone

```elm
customZone : Basics.Int -> List.List { start : Basics.Int, offset : Basics.Int } -> Time.Zone
```

 **Intended for package authors.**

The documentation of [`here`](#here) explains that it has certain accuracy
limitations that block on adding new APIs to JavaScript. The `customZone`
function is a stopgap that takes:

1. A default offset in minutes. So `Etc/GMT-5` is `customZone (-5 * 60) []`
and `Etc/GMT+9` is `customZone (9 * 60) []`.
2. A list of exceptions containing their `start` time in "minutes since the Unix
epoch" and their `offset` in "minutes from UTC"

Human times will be based on the nearest `start`, falling back on the default
offset if the time is older than all of the exceptions.

When paired with `getZoneName`, this allows you to load the real IANA time zone
database however you want: HTTP, cache, hardcode, etc.

**Note:** If you use this, please share your work in an Elm community forum!
I am sure others would like to hear about it, and more experience reports will
help me and the any potential TC39 proposal.


## every

```elm
every : Basics.Float -> (Time.Posix -> msg) -> Platform.Sub.Sub msg
```

 Get the current time periodically. How often though? Well, you provide an
interval in milliseconds (like `1000` for a second or `60 * 1000` for a minute
or `60 * 60 * 1000` for an hour) and that is how often you get a new time!

Check out [this example](https://elm-lang.org/examples/time) to see how to use
it in an application.

**This function is not for animation.** Use the [`onAnimationFrame`][af]
package for that sort of thing! It syncs up with repaints and will end up
being much smoother for any moving visuals.

[af]: /packages/elm/browser/latest/Browser-Events#onAnimationFrame


## getZoneName

```elm
getZoneName : Task.Task x Time.ZoneName
```

 **Intended for package authors.**

Use `Intl.DateTimeFormat().resolvedOptions().timeZone` to try to get names
like `Europe/Moscow` or `America/Havana`. From there you can look it up in any
IANA data you loaded yourself.


## here

```elm
here : Task.Task x Time.Zone
```

 Produce a `Zone` based on the current UTC offset. You can use this to figure
out what day it is where you are:

    import Task exposing (Task)
    import Time

    whatDayIsIt : Task x Int
    whatDayIsIt =
      Task.map2 Time.toDay Time.here Time.now

**Accuracy Note:** This function can only give time zones like `Etc/GMT+9` or
`Etc/GMT-6`. It cannot give you `Europe/Stockholm`, `Asia/Tokyo`, or any other
normal time zone from the [full list][tz] due to limitations in JavaScript.
For example, if you run `here` in New York City, the resulting `Zone` will
never be `America/New_York`. Instead you get `Etc/GMT-5` or `Etc/GMT-4`
depending on Daylight Saving Time. So even though browsers must have internal
access to `America/New_York` to figure out that offset, there is no public API
to get the full information. This means the `Zone` you get from this function
will act weird if (1) an application stays open across a Daylight Saving Time
boundary or (2) you try to use it on historical data.

**Future Note:** We can improve `here` when there is good browser support for
JavaScript functions that (1) expose the IANA time zone database and (2) let
you ask the time zone of the computer. The committee that reviews additions to
JavaScript is called TC39, and I encourage you to push for these capabilities! I
cannot do it myself unfortunately.

**Alternatives:** See the `customZone` docs to learn how to implement stopgaps.

[tz]: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones


## millisToPosix

```elm
millisToPosix : Basics.Int -> Time.Posix
```

 Turn milliseconds into a `Posix` time.


## now

```elm
now : Task.Task x Time.Posix
```

 Get the POSIX time at the moment when this task is run.


## posixToMillis

```elm
posixToMillis : Time.Posix -> Basics.Int
```

 Turn a `Posix` time into the number of milliseconds since 1970 January 1
at 00:00:00 UTC. It was a Thursday.


## toDay

```elm
toDay : Time.Zone -> Time.Posix -> Basics.Int
```

 What day is it?! (Days go from 1 to 31)

    import Time exposing (toDay, utc, millisToPosix)

    toDay utc (millisToPosix 0) == 1
    toDay nyc (millisToPosix 0) == 31

    -- pretend `nyc` is the `Zone` for America/New_York.



## toHour

```elm
toHour : Time.Zone -> Time.Posix -> Basics.Int
```

 What hour is it? (From 0 to 23)

    import Time exposing (toHour, utc, millisToPosix)

    toHour utc (millisToPosix 0) == 0  -- 12am
    toHour nyc (millisToPosix 0) == 19 -- 7pm

    -- pretend `nyc` is the `Zone` for America/New_York.


## toMillis

```elm
toMillis : Time.Zone -> Time.Posix -> Basics.Int
```


    import Time exposing (toMillis, utc, millisToPosix)

    toMillis utc (millisToPosix    0) == 0
    toMillis utc (millisToPosix 1234) == 234
    toMillis utc (millisToPosix 5678) == 678


## toMinute

```elm
toMinute : Time.Zone -> Time.Posix -> Basics.Int
```

 What minute is it? (From 0 to 59)

    import Time exposing (toMinute, utc, millisToPosix)

    toMinute utc (millisToPosix 0) == 0

This can be different in different time zones. Some time zones are offset
by 30 or 45 minutes!


## toMonth

```elm
toMonth : Time.Zone -> Time.Posix -> Time.Month
```

 What month is it?!

    import Time exposing (toMonth, utc, millisToPosix)

    toMonth utc (millisToPosix 0) == Jan
    toMonth nyc (millisToPosix 0) == Dec

    -- pretend `nyc` is the `Zone` for America/New_York.


## toSecond

```elm
toSecond : Time.Zone -> Time.Posix -> Basics.Int
```

 What second is it?

    import Time exposing (toSecond, utc, millisToPosix)

    toSecond utc (millisToPosix    0) == 0
    toSecond utc (millisToPosix 1234) == 1
    toSecond utc (millisToPosix 5678) == 5


## toWeekday

```elm
toWeekday : Time.Zone -> Time.Posix -> Time.Weekday
```

 What day of the week is it?

    import Time exposing (toWeekday, utc, millisToPosix)

    toWeekday utc (millisToPosix 0) == Thu
    toWeekday nyc (millisToPosix 0) == Wed

    -- pretend `nyc` is the `Zone` for America/New_York.


## toYear

```elm
toYear : Time.Zone -> Time.Posix -> Basics.Int
```

 What year is it?!

    import Time exposing (toYear, utc, millisToPosix)

    toYear utc (millisToPosix 0) == 1970
    toYear nyc (millisToPosix 0) == 1969

    -- pretend `nyc` is the `Zone` for America/New_York.


## utc

```elm
utc : Time.Zone
```

 The time zone for Coordinated Universal Time ([UTC][])

The `utc` zone has no time adjustments. It never observes daylight-saving
time and it never shifts around based on political restructuring.

[UTC]: https://en.wikipedia.org/wiki/Coordinated_Universal_Time

