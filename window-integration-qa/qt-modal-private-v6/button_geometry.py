"""Qt client button bounds mapped only through observed native root surface."""
def button_point(widget,native):
 width,height=widget['geometryGlobal'][2:]
 bx,by,bw,bh=widget['buttonClient'];nx,ny,nw,nh=native['surfaceBox']
 if not(width>0 and height>0 and nw>0 and nh>0 and bw>0 and bh>0 and bx>=0 and by>=0 and bx+bw<=width and by+bh<=height):raise AssertionError('Incoherent actual client/surface button geometry')
 localx=bx+min(5,bw/4);localy=by+bh/2
 point=(round(nx+localx*nw/width),round(ny+localy*nh/height))
 if not contains(native['surfaceBox'],point):raise AssertionError('Button point outside actual native surface')
 return point

def contains(box,point):
 x,y,width,height=box;px,py=point
 return x<=px<x+width and y<=py<y+height
