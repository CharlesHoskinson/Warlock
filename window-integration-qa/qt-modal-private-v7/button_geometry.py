"""Paired configured Qt/native bounds for an exact scale1 private surface."""
def geometry_key(widget,native):
 width,height=widget['geometryGlobal'][2:]
 bx,by,bw,bh=widget['buttonClient'];nx,ny,nw,nh=native['surfaceBox']
 if width!=nw or height!=nh:raise AssertionError('Configured Qt client extent must equal native surface at scale1')
 if widget['layoutGeometry']!=[0,0,width,height]:raise AssertionError('Actual Qt layout must cover configured client extent')
 if not(width>0 and height>0 and bw>0 and bh>0 and bx>=0 and by>=0 and bx+bw<=width and by+bh<=height):raise AssertionError('Incoherent actual client/surface button geometry')
 return (width,height,bx,by,bw,bh,nx,ny,nw,nh)

def layout_ready(widget,native):
 try:geometry_key(widget,native);return True
 except (AssertionError,KeyError,TypeError,ValueError):return False

def button_point(widget,native):
 geometry_key(widget,native)
 bx,by,bw,bh=widget['buttonClient'];nx,ny,_,_=native['surfaceBox']
 # QWidget client units and native logical units agree at the required scale1.
 point=(round(nx+bx+min(5,bw/4)),round(ny+by+bh/2))
 if not contains(native['surfaceBox'],point) or not contains([nx+bx,ny+by,bw,bh],point):raise AssertionError('Button point outside actual native button/surface')
 return point

def contains(box,point):
 x,y,width,height=box;px,py=point
 return x<=px<x+width and y<=py<y+height
