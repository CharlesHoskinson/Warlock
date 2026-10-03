"""Caption glyph oracles for the private gold/green/blue fixture.

Interior-only contrast excludes the circular boundary and gold caption outside
the button. The maximize glyph uses the configured dark foreground; the pin is
a color emoji, whose red mark differs from both blue fill and gold backdrop.
"""
def classify(rgba,index,size=14):
    if len(rgba)!=size*size*4:raise ValueError('exact RGBA button raster required')
    background=glyph=interior_background=0
    for pixel in range(size*size):
        x,y=pixel%size,pixel//size;r,g,b,a=rgba[pixel*4:pixel*4+4]
        fill=(g>170 and 130<r<215 and 110<b<200) if index==1 else (b>175 and 80<r<175 and 120<g<220)
        if a>80 and fill:background+=1
        # Every selected pixel is strictly inside the circle, so backdrop and
        # its antialiased circular boundary cannot count as an icon.
        interior=3<=x<size-3 and 3<=y<size-3
        if a<=80 or not interior:continue
        if fill:interior_background+=1
        mark=(r<146 and g<202 and b<146) if index==1 else (r>177 and g<140 and b<200)
        if mark:glyph+=1
    return {'backgroundPixels':background,'interiorBackgroundPixels':interior_background,
            'glyphPixels':glyph,'passed':background>20 and interior_background>4 and glyph>2}
