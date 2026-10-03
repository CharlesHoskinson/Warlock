# official/packages/elm/svg/1.0.0/docs.json
Source: https://package.elm-lang.org/packages/elm/svg/1.0.0/docs.json

# Svg



# SVG Nodes
@docs Svg, Attribute, text, node, map

# HTML Embedding
@docs svg, foreignObject

# Graphics elements
@docs circle, ellipse, image, line, path, polygon, polyline, rect, use

# Animation elements
@docs animate, animateColor, animateMotion, animateTransform, mpath, set

# Descriptive elements
@docs desc, metadata, title

# Containers
@docs a, defs, g, marker, mask, pattern, switch, symbol

# Text
@docs altGlyph, altGlyphDef, altGlyphItem, glyph, glyphRef, textPath, text_,
  tref, tspan

# Fonts
@docs font

# Gradients
@docs linearGradient, radialGradient, stop

# Filters
@docs feBlend, feColorMatrix, feComponentTransfer, feComposite,
  feConvolveMatrix, feDiffuseLighting, feDisplacementMap, feFlood, feFuncA,
  feFuncB, feFuncG, feFuncR, feGaussianBlur, feImage, feMerge, feMergeNode,
  feMorphology, feOffset, feSpecularLighting, feTile, feTurbulence

# Light source elements
@docs feDistantLight, fePointLight, feSpotLight

# Miscellaneous
@docs clipPath, colorProfile, cursor, filter, style, view


## Attribute

```elm
type alias Attribute msg =
    VirtualDom.Attribute msg
```

 Set attributes on your `Svg`.


## Svg

```elm
type alias Svg msg =
    VirtualDom.Node msg
```

 The core building block to create SVG. This library is filled with helper
functions to create these `Svg` values.

This is backed by `VirtualDom.Node` in `evancz/virtual-dom`, but you do not
need to know any details about that to use this library!


## a

```elm
a : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```

 The SVG Anchor Element defines a hyperlink.


## altGlyph

```elm
altGlyph : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## altGlyphDef

```elm
altGlyphDef : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## altGlyphItem

```elm
altGlyphItem : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## animate

```elm
animate : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## animateColor

```elm
animateColor : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## animateMotion

```elm
animateMotion : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## animateTransform

```elm
animateTransform : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## circle

```elm
circle : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```

 The circle element is an SVG basic shape, used to create circles based on
a center point and a radius.

    circle [ cx "60", cy "60", r "50" ] []


## clipPath

```elm
clipPath : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## colorProfile

```elm
colorProfile : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## cursor

```elm
cursor : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## defs

```elm
defs : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## desc

```elm
desc : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## ellipse

```elm
ellipse : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feBlend

```elm
feBlend : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feColorMatrix

```elm
feColorMatrix : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feComponentTransfer

```elm
feComponentTransfer : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feComposite

```elm
feComposite : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feConvolveMatrix

```elm
feConvolveMatrix : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feDiffuseLighting

```elm
feDiffuseLighting : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feDisplacementMap

```elm
feDisplacementMap : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feDistantLight

```elm
feDistantLight : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feFlood

```elm
feFlood : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feFuncA

```elm
feFuncA : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feFuncB

```elm
feFuncB : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feFuncG

```elm
feFuncG : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feFuncR

```elm
feFuncR : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feGaussianBlur

```elm
feGaussianBlur : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feImage

```elm
feImage : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feMerge

```elm
feMerge : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feMergeNode

```elm
feMergeNode : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feMorphology

```elm
feMorphology : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feOffset

```elm
feOffset : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## fePointLight

```elm
fePointLight : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feSpecularLighting

```elm
feSpecularLighting : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feSpotLight

```elm
feSpotLight : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feTile

```elm
feTile : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## feTurbulence

```elm
feTurbulence : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## filter

```elm
filter : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## font

```elm
font : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## foreignObject

```elm
foreignObject : List.List (Svg.Attribute msg) -> List.List (Html.Html msg) -> Svg.Svg msg
```



## g

```elm
g : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## glyph

```elm
glyph : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## glyphRef

```elm
glyphRef : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## image

```elm
image : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## line

```elm
line : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## linearGradient

```elm
linearGradient : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## map

```elm
map : (a -> msg) -> Svg.Svg a -> Svg.Svg msg
```

 Transform the messages produced by some `Svg`.


## marker

```elm
marker : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## mask

```elm
mask : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## metadata

```elm
metadata : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## mpath

```elm
mpath : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## node

```elm
node : String.String -> List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```

 Create any SVG node. To create a `<rect>` helper function, you would write:

    rect : List (Attribute msg) -> List (Svg msg) -> Svg msg
    rect attributes children =
        node "rect" attributes children

You should always be able to use the helper functions already defined in this
library though!


## path

```elm
path : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## pattern

```elm
pattern : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## polygon

```elm
polygon : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## polyline

```elm
polyline : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```

 The polyline element is an SVG basic shape, used to create a series of
straight lines connecting several points. Typically a polyline is used to
create open shapes.

    polyline [ fill "none", stroke "black", points "20,100 40,60 70,80 100,20" ] []


## radialGradient

```elm
radialGradient : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## rect

```elm
rect : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## set

```elm
set : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## stop

```elm
stop : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## style

```elm
style : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## svg

```elm
svg : List.List (Html.Attribute msg) -> List.List (Svg.Svg msg) -> Html.Html msg
```

 The root `<svg>` node for any SVG scene. This example shows a scene
containing a rounded rectangle:

    import Svg exposing (..)
    import Svg.Attributes exposing (..)

    roundRect =
        svg
          [ width "120", height "120", viewBox "0 0 120 120" ]
          [ rect [ x "10", y "10", width "100", height "100", rx "15", ry "15" ] [] ]


## switch

```elm
switch : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## symbol

```elm
symbol : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## text

```elm
text : String.String -> Svg.Svg msg
```

 A simple text node, no tags at all.

Warning: not to be confused with `text_` which produces the SVG `<text>` tag!


## textPath

```elm
textPath : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## text_

```elm
text_ : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## title

```elm
title : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## tref

```elm
tref : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## tspan

```elm
tspan : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## use

```elm
use : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



## view

```elm
view : List.List (Svg.Attribute msg) -> List.List (Svg.Svg msg) -> Svg.Svg msg
```



# Svg.Attributes



# Regular attributes
@docs accentHeight, accelerate, accumulate, additive, alphabetic, allowReorder,
  amplitude, arabicForm, ascent, attributeName, attributeType, autoReverse,
  azimuth, baseFrequency, baseProfile, bbox, begin, bias, by, calcMode,
  capHeight, class, clipPathUnits, contentScriptType, contentStyleType, cx, cy,
  d, decelerate, descent, diffuseConstant, divisor, dur, dx, dy, edgeMode,
  elevation, end, exponent, externalResourcesRequired, filterRes, filterUnits,
  format, from, fx, fy, g1, g2, glyphName, glyphRef, gradientTransform,
  gradientUnits, hanging, height, horizAdvX, horizOriginX, horizOriginY, id,
  ideographic, in_, in2, intercept, k, k1, k2, k3, k4, kernelMatrix,
  kernelUnitLength, keyPoints, keySplines, keyTimes, lang, lengthAdjust,
  limitingConeAngle, local, markerHeight, markerUnits, markerWidth,
  maskContentUnits, maskUnits, mathematical, max, media, method, min, mode,
  name, numOctaves, offset, operator, order, orient, orientation, origin,
  overlinePosition, overlineThickness, panose1, path, pathLength,
  patternContentUnits, patternTransform, patternUnits, pointOrder, points,
  pointsAtX, pointsAtY, pointsAtZ, preserveAlpha, preserveAspectRatio,
  primitiveUnits, r, radius, refX, refY, renderingIntent, repeatCount,
  repeatDur, requiredExtensions, requiredFeatures, restart, result, rotate,
  rx, ry, scale, seed, slope, spacing, specularConstant, specularExponent,
  speed, spreadMethod, startOffset, stdDeviation, stemh, stemv, stitchTiles,
  strikethroughPosition, strikethroughThickness, string, style, surfaceScale,
  systemLanguage, tableValues, target, targetX, targetY, textLength, title, to,
  transform, type_, u1, u2, underlinePosition, underlineThickness, unicode,
  unicodeRange, unitsPerEm, vAlphabetic, vHanging, vIdeographic, vMathematical,
  values, version, vertAdvY, vertOriginX, vertOriginY, viewBox, viewTarget,
  width, widths, x, xHeight, x1, x2, xChannelSelector, xlinkActuate,
  xlinkArcrole, xlinkHref, xlinkRole, xlinkShow, xlinkTitle, xlinkType,
  xmlBase, xmlLang, xmlSpace, y, y1, y2, yChannelSelector, z, zoomAndPan

# Presentation attributes
@docs alignmentBaseline, baselineShift, clipPath, clipRule, clip,
  colorInterpolationFilters, colorInterpolation, colorProfile, colorRendering,
  color, cursor, direction, display, dominantBaseline, enableBackground,
  fillOpacity, fillRule, fill, filter, floodColor, floodOpacity, fontFamily,
  fontSizeAdjust, fontSize, fontStretch, fontStyle, fontVariant, fontWeight,
  glyphOrientationHorizontal, glyphOrientationVertical, imageRendering,
  kerning, letterSpacing, lightingColor, markerEnd, markerMid, markerStart,
  mask, opacity, overflow, pointerEvents, shapeRendering, stopColor,
  stopOpacity, strokeDasharray, strokeDashoffset, strokeLinecap,
  strokeLinejoin, strokeMiterlimit, strokeOpacity, strokeWidth, stroke,
  textAnchor, textDecoration, textRendering, unicodeBidi, visibility,
  wordSpacing, writingMode



## accelerate

```elm
accelerate : String.String -> Svg.Attribute msg
```



## accentHeight

```elm
accentHeight : String.String -> Svg.Attribute msg
```



## accumulate

```elm
accumulate : String.String -> Svg.Attribute msg
```



## additive

```elm
additive : String.String -> Svg.Attribute msg
```



## alignmentBaseline

```elm
alignmentBaseline : String.String -> Svg.Attribute msg
```



## allowReorder

```elm
allowReorder : String.String -> Svg.Attribute msg
```



## alphabetic

```elm
alphabetic : String.String -> Svg.Attribute msg
```



## amplitude

```elm
amplitude : String.String -> Svg.Attribute msg
```



## arabicForm

```elm
arabicForm : String.String -> Svg.Attribute msg
```



## ascent

```elm
ascent : String.String -> Svg.Attribute msg
```



## attributeName

```elm
attributeName : String.String -> Svg.Attribute msg
```



## attributeType

```elm
attributeType : String.String -> Svg.Attribute msg
```



## autoReverse

```elm
autoReverse : String.String -> Svg.Attribute msg
```



## azimuth

```elm
azimuth : String.String -> Svg.Attribute msg
```



## baseFrequency

```elm
baseFrequency : String.String -> Svg.Attribute msg
```



## baseProfile

```elm
baseProfile : String.String -> Svg.Attribute msg
```



## baselineShift

```elm
baselineShift : String.String -> Svg.Attribute msg
```



## bbox

```elm
bbox : String.String -> Svg.Attribute msg
```



## begin

```elm
begin : String.String -> Svg.Attribute msg
```



## bias

```elm
bias : String.String -> Svg.Attribute msg
```



## by

```elm
by : String.String -> Svg.Attribute msg
```



## calcMode

```elm
calcMode : String.String -> Svg.Attribute msg
```



## capHeight

```elm
capHeight : String.String -> Svg.Attribute msg
```



## class

```elm
class : String.String -> Svg.Attribute msg
```



## clip

```elm
clip : String.String -> Svg.Attribute msg
```



## clipPath

```elm
clipPath : String.String -> Svg.Attribute msg
```



## clipPathUnits

```elm
clipPathUnits : String.String -> Svg.Attribute msg
```



## clipRule

```elm
clipRule : String.String -> Svg.Attribute msg
```



## color

```elm
color : String.String -> Svg.Attribute msg
```



## colorInterpolation

```elm
colorInterpolation : String.String -> Svg.Attribute msg
```



## colorInterpolationFilters

```elm
colorInterpolationFilters : String.String -> Svg.Attribute msg
```



## colorProfile

```elm
colorProfile : String.String -> Svg.Attribute msg
```



## colorRendering

```elm
colorRendering : String.String -> Svg.Attribute msg
```



## contentScriptType

```elm
contentScriptType : String.String -> Svg.Attribute msg
```



## contentStyleType

```elm
contentStyleType : String.String -> Svg.Attribute msg
```



## cursor

```elm
cursor : String.String -> Svg.Attribute msg
```



## cx

```elm
cx : String.String -> Svg.Attribute msg
```



## cy

```elm
cy : String.String -> Svg.Attribute msg
```



## d

```elm
d : String.String -> Svg.Attribute msg
```



## decelerate

```elm
decelerate : String.String -> Svg.Attribute msg
```



## descent

```elm
descent : String.String -> Svg.Attribute msg
```



## diffuseConstant

```elm
diffuseConstant : String.String -> Svg.Attribute msg
```



## direction

```elm
direction : String.String -> Svg.Attribute msg
```



## display

```elm
display : String.String -> Svg.Attribute msg
```



## divisor

```elm
divisor : String.String -> Svg.Attribute msg
```



## dominantBaseline

```elm
dominantBaseline : String.String -> Svg.Attribute msg
```



## dur

```elm
dur : String.String -> Svg.Attribute msg
```



## dx

```elm
dx : String.String -> Svg.Attribute msg
```



## dy

```elm
dy : String.String -> Svg.Attribute msg
```



## edgeMode

```elm
edgeMode : String.String -> Svg.Attribute msg
```



## elevation

```elm
elevation : String.String -> Svg.Attribute msg
```



## enableBackground

```elm
enableBackground : String.String -> Svg.Attribute msg
```



## end

```elm
end : String.String -> Svg.Attribute msg
```



## exponent

```elm
exponent : String.String -> Svg.Attribute msg
```



## externalResourcesRequired

```elm
externalResourcesRequired : String.String -> Svg.Attribute msg
```



## fill

```elm
fill : String.String -> Svg.Attribute msg
```



## fillOpacity

```elm
fillOpacity : String.String -> Svg.Attribute msg
```



## fillRule

```elm
fillRule : String.String -> Svg.Attribute msg
```



## filter

```elm
filter : String.String -> Svg.Attribute msg
```



## filterRes

```elm
filterRes : String.String -> Svg.Attribute msg
```



## filterUnits

```elm
filterUnits : String.String -> Svg.Attribute msg
```



## floodColor

```elm
floodColor : String.String -> Svg.Attribute msg
```



## floodOpacity

```elm
floodOpacity : String.String -> Svg.Attribute msg
```



## fontFamily

```elm
fontFamily : String.String -> Svg.Attribute msg
```



## fontSize

```elm
fontSize : String.String -> Svg.Attribute msg
```



## fontSizeAdjust

```elm
fontSizeAdjust : String.String -> Svg.Attribute msg
```



## fontStretch

```elm
fontStretch : String.String -> Svg.Attribute msg
```



## fontStyle

```elm
fontStyle : String.String -> Svg.Attribute msg
```



## fontVariant

```elm
fontVariant : String.String -> Svg.Attribute msg
```



## fontWeight

```elm
fontWeight : String.String -> Svg.Attribute msg
```



## format

```elm
format : String.String -> Svg.Attribute msg
```



## from

```elm
from : String.String -> Svg.Attribute msg
```



## fx

```elm
fx : String.String -> Svg.Attribute msg
```



## fy

```elm
fy : String.String -> Svg.Attribute msg
```



## g1

```elm
g1 : String.String -> Svg.Attribute msg
```



## g2

```elm
g2 : String.String -> Svg.Attribute msg
```



## glyphName

```elm
glyphName : String.String -> Svg.Attribute msg
```



## glyphOrientationHorizontal

```elm
glyphOrientationHorizontal : String.String -> Svg.Attribute msg
```



## glyphOrientationVertical

```elm
glyphOrientationVertical : String.String -> Svg.Attribute msg
```



## glyphRef

```elm
glyphRef : String.String -> Svg.Attribute msg
```



## gradientTransform

```elm
gradientTransform : String.String -> Svg.Attribute msg
```



## gradientUnits

```elm
gradientUnits : String.String -> Svg.Attribute msg
```



## hanging

```elm
hanging : String.String -> Svg.Attribute msg
```



## height

```elm
height : String.String -> Svg.Attribute msg
```



## horizAdvX

```elm
horizAdvX : String.String -> Svg.Attribute msg
```



## horizOriginX

```elm
horizOriginX : String.String -> Svg.Attribute msg
```



## horizOriginY

```elm
horizOriginY : String.String -> Svg.Attribute msg
```



## id

```elm
id : String.String -> Svg.Attribute msg
```



## ideographic

```elm
ideographic : String.String -> Svg.Attribute msg
```



## imageRendering

```elm
imageRendering : String.String -> Svg.Attribute msg
```



## in2

```elm
in2 : String.String -> Svg.Attribute msg
```



## in_

```elm
in_ : String.String -> Svg.Attribute msg
```



## intercept

```elm
intercept : String.String -> Svg.Attribute msg
```



## k

```elm
k : String.String -> Svg.Attribute msg
```



## k1

```elm
k1 : String.String -> Svg.Attribute msg
```



## k2

```elm
k2 : String.String -> Svg.Attribute msg
```



## k3

```elm
k3 : String.String -> Svg.Attribute msg
```



## k4

```elm
k4 : String.String -> Svg.Attribute msg
```



## kernelMatrix

```elm
kernelMatrix : String.String -> Svg.Attribute msg
```



## kernelUnitLength

```elm
kernelUnitLength : String.String -> Svg.Attribute msg
```



## kerning

```elm
kerning : String.String -> Svg.Attribute msg
```



## keyPoints

```elm
keyPoints : String.String -> Svg.Attribute msg
```



## keySplines

```elm
keySplines : String.String -> Svg.Attribute msg
```



## keyTimes

```elm
keyTimes : String.String -> Svg.Attribute msg
```



## lang

```elm
lang : String.String -> Svg.Attribute msg
```



## lengthAdjust

```elm
lengthAdjust : String.String -> Svg.Attribute msg
```



## letterSpacing

```elm
letterSpacing : String.String -> Svg.Attribute msg
```



## lightingColor

```elm
lightingColor : String.String -> Svg.Attribute msg
```



## limitingConeAngle

```elm
limitingConeAngle : String.String -> Svg.Attribute msg
```



## local

```elm
local : String.String -> Svg.Attribute msg
```



## markerEnd

```elm
markerEnd : String.String -> Svg.Attribute msg
```



## markerHeight

```elm
markerHeight : String.String -> Svg.Attribute msg
```



## markerMid

```elm
markerMid : String.String -> Svg.Attribute msg
```



## markerStart

```elm
markerStart : String.String -> Svg.Attribute msg
```



## markerUnits

```elm
markerUnits : String.String -> Svg.Attribute msg
```



## markerWidth

```elm
markerWidth : String.String -> Svg.Attribute msg
```



## mask

```elm
mask : String.String -> Svg.Attribute msg
```



## maskContentUnits

```elm
maskContentUnits : String.String -> Svg.Attribute msg
```



## maskUnits

```elm
maskUnits : String.String -> Svg.Attribute msg
```



## mathematical

```elm
mathematical : String.String -> Svg.Attribute msg
```



## max

```elm
max : String.String -> Svg.Attribute msg
```



## media

```elm
media : String.String -> Svg.Attribute msg
```



## method

```elm
method : String.String -> Svg.Attribute msg
```



## min

```elm
min : String.String -> Svg.Attribute msg
```



## mode

```elm
mode : String.String -> Svg.Attribute msg
```



## name

```elm
name : String.String -> Svg.Attribute msg
```



## numOctaves

```elm
numOctaves : String.String -> Svg.Attribute msg
```



## offset

```elm
offset : String.String -> Svg.Attribute msg
```



## opacity

```elm
opacity : String.String -> Svg.Attribute msg
```



## operator

```elm
operator : String.String -> Svg.Attribute msg
```



## order

```elm
order : String.String -> Svg.Attribute msg
```



## orient

```elm
orient : String.String -> Svg.Attribute msg
```



## orientation

```elm
orientation : String.String -> Svg.Attribute msg
```



## origin

```elm
origin : String.String -> Svg.Attribute msg
```



## overflow

```elm
overflow : String.String -> Svg.Attribute msg
```



## overlinePosition

```elm
overlinePosition : String.String -> Svg.Attribute msg
```



## overlineThickness

```elm
overlineThickness : String.String -> Svg.Attribute msg
```



## panose1

```elm
panose1 : String.String -> Svg.Attribute msg
```



## path

```elm
path : String.String -> Svg.Attribute msg
```



## pathLength

```elm
pathLength : String.String -> Svg.Attribute msg
```



## patternContentUnits

```elm
patternContentUnits : String.String -> Svg.Attribute msg
```



## patternTransform

```elm
patternTransform : String.String -> Svg.Attribute msg
```



## patternUnits

```elm
patternUnits : String.String -> Svg.Attribute msg
```



## pointOrder

```elm
pointOrder : String.String -> Svg.Attribute msg
```



## pointerEvents

```elm
pointerEvents : String.String -> Svg.Attribute msg
```



## points

```elm
points : String.String -> Svg.Attribute msg
```



## pointsAtX

```elm
pointsAtX : String.String -> Svg.Attribute msg
```



## pointsAtY

```elm
pointsAtY : String.String -> Svg.Attribute msg
```



## pointsAtZ

```elm
pointsAtZ : String.String -> Svg.Attribute msg
```



## preserveAlpha

```elm
preserveAlpha : String.String -> Svg.Attribute msg
```



## preserveAspectRatio

```elm
preserveAspectRatio : String.String -> Svg.Attribute msg
```



## primitiveUnits

```elm
primitiveUnits : String.String -> Svg.Attribute msg
```



## r

```elm
r : String.String -> Svg.Attribute msg
```



## radius

```elm
radius : String.String -> Svg.Attribute msg
```



## refX

```elm
refX : String.String -> Svg.Attribute msg
```



## refY

```elm
refY : String.String -> Svg.Attribute msg
```



## renderingIntent

```elm
renderingIntent : String.String -> Svg.Attribute msg
```



## repeatCount

```elm
repeatCount : String.String -> Svg.Attribute msg
```



## repeatDur

```elm
repeatDur : String.String -> Svg.Attribute msg
```



## requiredExtensions

```elm
requiredExtensions : String.String -> Svg.Attribute msg
```



## requiredFeatures

```elm
requiredFeatures : String.String -> Svg.Attribute msg
```



## restart

```elm
restart : String.String -> Svg.Attribute msg
```



## result

```elm
result : String.String -> Svg.Attribute msg
```



## rotate

```elm
rotate : String.String -> Svg.Attribute msg
```



## rx

```elm
rx : String.String -> Svg.Attribute msg
```



## ry

```elm
ry : String.String -> Svg.Attribute msg
```



## scale

```elm
scale : String.String -> Svg.Attribute msg
```



## seed

```elm
seed : String.String -> Svg.Attribute msg
```



## shapeRendering

```elm
shapeRendering : String.String -> Svg.Attribute msg
```



## slope

```elm
slope : String.String -> Svg.Attribute msg
```



## spacing

```elm
spacing : String.String -> Svg.Attribute msg
```



## specularConstant

```elm
specularConstant : String.String -> Svg.Attribute msg
```



## specularExponent

```elm
specularExponent : String.String -> Svg.Attribute msg
```



## speed

```elm
speed : String.String -> Svg.Attribute msg
```



## spreadMethod

```elm
spreadMethod : String.String -> Svg.Attribute msg
```



## startOffset

```elm
startOffset : String.String -> Svg.Attribute msg
```



## stdDeviation

```elm
stdDeviation : String.String -> Svg.Attribute msg
```



## stemh

```elm
stemh : String.String -> Svg.Attribute msg
```



## stemv

```elm
stemv : String.String -> Svg.Attribute msg
```



## stitchTiles

```elm
stitchTiles : String.String -> Svg.Attribute msg
```



## stopColor

```elm
stopColor : String.String -> Svg.Attribute msg
```



## stopOpacity

```elm
stopOpacity : String.String -> Svg.Attribute msg
```



## strikethroughPosition

```elm
strikethroughPosition : String.String -> Svg.Attribute msg
```



## strikethroughThickness

```elm
strikethroughThickness : String.String -> Svg.Attribute msg
```



## string

```elm
string : String.String -> Svg.Attribute msg
```



## stroke

```elm
stroke : String.String -> Svg.Attribute msg
```



## strokeDasharray

```elm
strokeDasharray : String.String -> Svg.Attribute msg
```



## strokeDashoffset

```elm
strokeDashoffset : String.String -> Svg.Attribute msg
```



## strokeLinecap

```elm
strokeLinecap : String.String -> Svg.Attribute msg
```



## strokeLinejoin

```elm
strokeLinejoin : String.String -> Svg.Attribute msg
```



## strokeMiterlimit

```elm
strokeMiterlimit : String.String -> Svg.Attribute msg
```



## strokeOpacity

```elm
strokeOpacity : String.String -> Svg.Attribute msg
```



## strokeWidth

```elm
strokeWidth : String.String -> Svg.Attribute msg
```



## style

```elm
style : String.String -> Svg.Attribute msg
```



## surfaceScale

```elm
surfaceScale : String.String -> Svg.Attribute msg
```



## systemLanguage

```elm
systemLanguage : String.String -> Svg.Attribute msg
```



## tableValues

```elm
tableValues : String.String -> Svg.Attribute msg
```



## target

```elm
target : String.String -> Svg.Attribute msg
```



## targetX

```elm
targetX : String.String -> Svg.Attribute msg
```



## targetY

```elm
targetY : String.String -> Svg.Attribute msg
```



## textAnchor

```elm
textAnchor : String.String -> Svg.Attribute msg
```



## textDecoration

```elm
textDecoration : String.String -> Svg.Attribute msg
```



## textLength

```elm
textLength : String.String -> Svg.Attribute msg
```



## textRendering

```elm
textRendering : String.String -> Svg.Attribute msg
```



## title

```elm
title : String.String -> Svg.Attribute msg
```



## to

```elm
to : String.String -> Svg.Attribute msg
```



## transform

```elm
transform : String.String -> Svg.Attribute msg
```



## type_

```elm
type_ : String.String -> Svg.Attribute msg
```



## u1

```elm
u1 : String.String -> Svg.Attribute msg
```



## u2

```elm
u2 : String.String -> Svg.Attribute msg
```



## underlinePosition

```elm
underlinePosition : String.String -> Svg.Attribute msg
```



## underlineThickness

```elm
underlineThickness : String.String -> Svg.Attribute msg
```



## unicode

```elm
unicode : String.String -> Svg.Attribute msg
```



## unicodeBidi

```elm
unicodeBidi : String.String -> Svg.Attribute msg
```



## unicodeRange

```elm
unicodeRange : String.String -> Svg.Attribute msg
```



## unitsPerEm

```elm
unitsPerEm : String.String -> Svg.Attribute msg
```



## vAlphabetic

```elm
vAlphabetic : String.String -> Svg.Attribute msg
```



## vHanging

```elm
vHanging : String.String -> Svg.Attribute msg
```



## vIdeographic

```elm
vIdeographic : String.String -> Svg.Attribute msg
```



## vMathematical

```elm
vMathematical : String.String -> Svg.Attribute msg
```



## values

```elm
values : String.String -> Svg.Attribute msg
```



## version

```elm
version : String.String -> Svg.Attribute msg
```



## vertAdvY

```elm
vertAdvY : String.String -> Svg.Attribute msg
```



## vertOriginX

```elm
vertOriginX : String.String -> Svg.Attribute msg
```



## vertOriginY

```elm
vertOriginY : String.String -> Svg.Attribute msg
```



## viewBox

```elm
viewBox : String.String -> Svg.Attribute msg
```



## viewTarget

```elm
viewTarget : String.String -> Svg.Attribute msg
```



## visibility

```elm
visibility : String.String -> Svg.Attribute msg
```



## width

```elm
width : String.String -> Svg.Attribute msg
```



## widths

```elm
widths : String.String -> Svg.Attribute msg
```



## wordSpacing

```elm
wordSpacing : String.String -> Svg.Attribute msg
```



## writingMode

```elm
writingMode : String.String -> Svg.Attribute msg
```



## x

```elm
x : String.String -> Svg.Attribute msg
```



## x1

```elm
x1 : String.String -> Svg.Attribute msg
```



## x2

```elm
x2 : String.String -> Svg.Attribute msg
```



## xChannelSelector

```elm
xChannelSelector : String.String -> Svg.Attribute msg
```



## xHeight

```elm
xHeight : String.String -> Svg.Attribute msg
```



## xlinkActuate

```elm
xlinkActuate : String.String -> Svg.Attribute msg
```



## xlinkArcrole

```elm
xlinkArcrole : String.String -> Svg.Attribute msg
```



## xlinkHref

```elm
xlinkHref : String.String -> Svg.Attribute msg
```



## xlinkRole

```elm
xlinkRole : String.String -> Svg.Attribute msg
```



## xlinkShow

```elm
xlinkShow : String.String -> Svg.Attribute msg
```



## xlinkTitle

```elm
xlinkTitle : String.String -> Svg.Attribute msg
```



## xlinkType

```elm
xlinkType : String.String -> Svg.Attribute msg
```



## xmlBase

```elm
xmlBase : String.String -> Svg.Attribute msg
```



## xmlLang

```elm
xmlLang : String.String -> Svg.Attribute msg
```



## xmlSpace

```elm
xmlSpace : String.String -> Svg.Attribute msg
```



## y

```elm
y : String.String -> Svg.Attribute msg
```



## y1

```elm
y1 : String.String -> Svg.Attribute msg
```



## y2

```elm
y2 : String.String -> Svg.Attribute msg
```



## yChannelSelector

```elm
yChannelSelector : String.String -> Svg.Attribute msg
```



## z

```elm
z : String.String -> Svg.Attribute msg
```



## zoomAndPan

```elm
zoomAndPan : String.String -> Svg.Attribute msg
```



# Svg.Events



# Mouse
@docs onClick, onMouseDown, onMouseUp, onMouseOver, onMouseOut

# Custom
@docs on, stopPropagationOn, preventDefaultOn, custom



## custom

```elm
custom : String.String -> Json.Decode.Decoder { message : msg, stopPropagation : Basics.Bool, preventDefault : Basics.Bool } -> Svg.Attribute msg
```

 Create an event listener that may [`stopPropagation`][stop] or
[`preventDefault`][prevent].

[stop]: https://developer.mozilla.org/en-US/docs/Web/API/Event/stopPropagation
[prevent]: https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault

**Note:** If you need something even more custom (like capture phase) check
out the lower-level event API in `elm/virtual-dom`.


## on

```elm
on : String.String -> Json.Decode.Decoder msg -> Svg.Attribute msg
```

 Create a custom event listener. Normally this will not be necessary, but
you have the power! Here is how `onClick` is defined for example:

    import Json.Decode as Decode

    onClick : msg -> Attribute msg
    onClick message =
      on "click" (Decode.succeed message)

The first argument is the event name in the same format as with JavaScript's
[`addEventListener`][aEL] function.

The second argument is a JSON decoder. Read more about these [here][decoder].
When an event occurs, the decoder tries to turn the event object into an Elm
value. If successful, the value is routed to your `update` function. In the
case of `onClick` we always just succeed with the given `message`.

If this is confusing, work through the [Elm Architecture Tutorial][tutorial].
It really helps!

[aEL]: https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener
[decoder]: /packages/elm/json/latest/Json-Decode
[tutorial]: https://github.com/evancz/elm-architecture-tutorial/

**Note:** This creates a [passive][] event listener, enabling optimizations for
touch, scroll, and wheel events in some browsers.

[passive]: https://github.com/WICG/EventListenerOptions/blob/gh-pages/explainer.md


## onClick

```elm
onClick : msg -> Svg.Attribute msg
```



## onMouseDown

```elm
onMouseDown : msg -> Svg.Attribute msg
```



## onMouseOut

```elm
onMouseOut : msg -> Svg.Attribute msg
```



## onMouseOver

```elm
onMouseOver : msg -> Svg.Attribute msg
```



## onMouseUp

```elm
onMouseUp : msg -> Svg.Attribute msg
```



## preventDefaultOn

```elm
preventDefaultOn : String.String -> Json.Decode.Decoder ( msg, Basics.Bool ) -> Svg.Attribute msg
```

 Create an event listener that may [`preventDefault`][prevent]. Your decoder
must produce a message and a `Bool` that decides if `preventDefault` should
be called.

For example, the `onSubmit` function in this library *always* prevents the
default behavior:

[prevent]: https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault

    onSubmit : msg -> Attribute msg
    onSubmit msg =
      preventDefaultOn "submit" (Json.map alwaysPreventDefault (Json.succeed msg))

    alwaysPreventDefault : msg -> ( msg, Bool )
    alwaysPreventDefault msg =
      ( msg, True )


## stopPropagationOn

```elm
stopPropagationOn : String.String -> Json.Decode.Decoder ( msg, Basics.Bool ) -> Svg.Attribute msg
```

 Create an event listener that may [`stopPropagation`][stop]. Your decoder
must produce a message and a `Bool` that decides if `stopPropagation` should
be called.

[stop]: https://developer.mozilla.org/en-US/docs/Web/API/Event/stopPropagation

**Note:** This creates a [passive][] event listener, enabling optimizations for
touch, scroll, and wheel events in some browsers.

[passive]: https://github.com/WICG/EventListenerOptions/blob/gh-pages/explainer.md


# Svg.Keyed

 A keyed node helps optimize cases where children are getting added, moved,
removed, etc. Common examples include:

  - The user can delete items from a list.
  - The user can create new items in a list.
  - You can sort a list based on name or date or whatever.

When you use a keyed node, every child is paired with a string identifier. This
makes it possible for the underlying diffing algorithm to reuse nodes more
efficiently.

# Keyed Nodes
@docs node



## node

```elm
node : String.String -> List.List (Svg.Attribute msg) -> List.List ( String.String, Svg.Svg msg ) -> Svg.Svg msg
```

 Works just like `Svg.node`, but you add a unique identifier to each child
node. You want this when you have a list of nodes that is changing: adding
nodes, removing nodes, etc. In these cases, the unique identifiers help make
the DOM modifications more efficient.


# Svg.Lazy

 Since all Elm functions are pure we have a guarantee that the same input
will always result in the same output. This module gives us tools to be lazy
about building `Svg` that utilize this fact.

Rather than immediately applying functions to their arguments, the `lazy`
functions just bundle the function and arguments up for later. When diffing
the old and new virtual DOM, it checks to see if all the arguments are equal.
If so, it skips calling the function!

This is a really cheap test and often makes things a lot faster, but definitely
benchmark to be sure!

@docs lazy, lazy2, lazy3, lazy4, lazy5, lazy6, lazy7, lazy8


## lazy

```elm
lazy : (a -> Svg.Svg msg) -> a -> Svg.Svg msg
```

 A performance optimization that delays the building of virtual DOM nodes.

Calling `(view model)` will definitely build some virtual DOM, perhaps a lot of
it. Calling `(lazy view model)` delays the call until later. During diffing, we
can check to see if `model` is referentially equal to the previous value used,
and if so, we just stop. No need to build up the tree structure and diff it,
we know if the input to `view` is the same, the output must be the same!


## lazy2

```elm
lazy2 : (a -> b -> Svg.Svg msg) -> a -> b -> Svg.Svg msg
```

 Same as `lazy` but checks on two arguments.


## lazy3

```elm
lazy3 : (a -> b -> c -> Svg.Svg msg) -> a -> b -> c -> Svg.Svg msg
```

 Same as `lazy` but checks on three arguments.


## lazy4

```elm
lazy4 : (a -> b -> c -> d -> Svg.Svg msg) -> a -> b -> c -> d -> Svg.Svg msg
```

 Same as `lazy` but checks on four arguments.


## lazy5

```elm
lazy5 : (a -> b -> c -> d -> e -> Svg.Svg msg) -> a -> b -> c -> d -> e -> Svg.Svg msg
```

 Same as `lazy` but checks on five arguments.


## lazy6

```elm
lazy6 : (a -> b -> c -> d -> e -> f -> Svg.Svg msg) -> a -> b -> c -> d -> e -> f -> Svg.Svg msg
```

 Same as `lazy` but checks on six arguments.


## lazy7

```elm
lazy7 : (a -> b -> c -> d -> e -> f -> g -> Svg.Svg msg) -> a -> b -> c -> d -> e -> f -> g -> Svg.Svg msg
```

 Same as `lazy` but checks on seven arguments.


## lazy8

```elm
lazy8 : (a -> b -> c -> d -> e -> f -> g -> h -> Svg.Svg msg) -> a -> b -> c -> d -> e -> f -> g -> h -> Svg.Svg msg
```

 Same as `lazy` but checks on eight arguments.

