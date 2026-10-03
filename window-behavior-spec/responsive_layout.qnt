/** Refinement of the spec-first layout-contract.md. Logical Qt client pixels.
 * Physical Qt/Wayland fractional-scale rounding is measured by native fixture,
 * not asserted away by this model. File operation semantics are out of scope. */
module responsive_layout {
  type Event = Resize({w:int,h:int}) | Select | Clear | Details | Sidebar | Navigate | Filter
  pure val WIDTHS=Set(330,487,500,533,599,600,649,650,799,800,801,899,900,999,1000,1320,1600)
  pure val HEIGHTS=Set(320,487,800,1000)
  pure def min(a:int,b:int):int=if(a<b) a else b
  pure def max(a:int,b:int):int=if(a>b) a else b
  pure def boundedThumb(viewport:int,preferred:int):int=max(30,min(preferred,viewport-52))
  pure def toolbarH(w:int):int=if(w<600) 128 else if(w<1000) 92 else 52
  pure def mainW(w:int):int=w-(if(w>=900) 244 else 0)
  pure def docks(w:int):bool=mainW(w)>=650
  var width:int
  var height:int
  var selected:bool
  var preferred:bool
  var overlay:bool
  var sidebar:bool
  var expanded:bool
  action init=all{width'=330,height'=320,selected'=false,preferred'=true,overlay'=false,sidebar'=false,expanded'=false}
  action fire(e:Event):bool=all{
    width'=match e {|Resize(r)=>r.w|_=>width},
    height'=match e {|Resize(r)=>r.h|_=>height},
    selected'=if(e==Clear or e==Navigate) false else if(e==Select) true else selected,
    preferred'=if(e==Details) {if(docks(width)) not(preferred) else if(not(overlay)) true else preferred} else preferred,
    overlay'=match e {|Resize(r)=>if(docks(r.w)!=docks(width)) false else overlay|Clear=>false|Navigate=>false|Details=>if(docks(width)) overlay else not(overlay)|_=>overlay},
    sidebar'=match e {|Resize(r)=>if((r.w>=900)!=(width>=900)) false else sidebar|Navigate=>false|Sidebar=>if(width<900) not(sidebar) else sidebar|_=>sidebar},
    expanded'=if(e==Filter) not(expanded) else expanded
  }
  pure val EVENTS=WIDTHS.fold(Set(Select,Clear,Details,Sidebar,Navigate,Filter),(acc,w)=>acc.union(HEIGHTS.map(h=>Resize({w:w,h:h}))))
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val bodyH=height-toolbarH(width)-26
  val fileW=mainW(width)-(if(docks(width) and selected and preferred) 300 else 0)
  val fileHeaderH=if(fileW<760) 78 else 62
  val listH=bodyH-fileHeaderH-28
  val gridH=bodyH-fileHeaderH
  // Any preferred thumbnail bounded by the actual viewport fits its name,
  // metadata and six-pixel top margin. The QML/native test measures rounding.
  val thumbH=boundedThumb(gridH,fileW)
  val dateW=if(fileW>=650) 140 else 0
  val kindW=if(fileW>=480) 72 else 0
  val nameW=fileW-52-dateW-84-kindW-16-8
  val navW=if(width>=900) 137 else 171
  val toolsX=width-14-98
  val extraX=if(width<600) width-14-64 else toolsX-64-4
  val filterW=if(width<600) width-104 else if(width<1000) min(250,(width-40)/2) else if(expanded) 250 else 190
  val filterX=if(width<600) 14 else if(width<1000) width-filterW-14 else extraX-filterW-12
  val pathX=if(width<1000) 14 else 14+navW+14
  val pathW=if(width<600) width-28 else filterX-pathX-12
  val allProps=width>=330 and height>=320 and bodyH>=166 and fileW>=330 and listH>=60 and nameW>=100
    and thumbH>=30 and thumbH+52<=gridH
    and filterW>=100 and pathW>=100 and filterX>=0 and pathX>=0
    and filterX+filterW<=width and pathX+pathW<=width
    and (width<600 implies 14+navW<=toolsX)
    and (width>=600 implies 14+navW<=extraX)
    and (width<600 implies filterX+filterW+12<=extraX)
    and (width>=1000 implies pathX+pathW+12<=filterX)
    and (docks(width) and selected and preferred implies fileW>=350)
    and (not(docks(width)) implies fileW==mainW(width))
}
