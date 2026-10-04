#include <QPointF>
#include <QMargins>
#include <cassert>
class QWaylandWindow { QMargins m; public: explicit QWaylandWindow(QMargins v):m(v){} QMargins clientSideMargins()const{return m;} QPointF mapFromWlSurface(const QPointF&)const; };
QPointF QWaylandWindow::mapFromWlSurface(const QPointF &surfacePosition) const
{
    const QMargins margins = clientSideMargins();
    return QPointF(surfacePosition.x() + margins.left(), surfacePosition.y() + margins.top());
}
int main(){int count=0;for(auto m:{QMargins(0,0,0,0),QMargins(6,30,7,8),QMargins(1,2,3,4),QMargins(256,512,1024,32)}){QWaylandWindow w(m);auto t=w.mapFromWlSurface(QPointF(0,0));assert(t==QPointF(-m.left(),-m.top()));for(auto p:{QPointF(0,0),QPointF(18,28),QPointF(-0.5,100.25),QPointF(1000,500)}){auto surface=p-t;assert(w.mapFromWlSurface(surface)==p);count++;}}return count==16?0:1;}
