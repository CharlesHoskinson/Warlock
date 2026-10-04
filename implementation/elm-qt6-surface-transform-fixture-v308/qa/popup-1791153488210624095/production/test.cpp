
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <string>
#include <vector>
using quint64=std::uint64_t;
struct QPaintEvent{};struct QWidget{int width()const{return 100;}int height()const{return 40;}};
struct QAction{bool enabled=true,visible=true;bool isEnabled()const{return enabled;}bool isVisible()const{return visible;}};
struct ActionList{std::vector<QAction*>items;bool contains(QAction*a)const{return std::find(items.begin(),items.end(),a)!=items.end();}};
static int basePaints,markers,emitted;
struct QMenu:QWidget{ActionList list;explicit QMenu(QWidget*){} virtual void paintEvent(QPaintEvent*){basePaints++;}ActionList actions()const{return list;}};
struct QRect{int x,y,w,h;QRect(int a,int b,int c,int d):x(a),y(b),w(c),h(d){}};
namespace Qt{enum Color{magenta,yellow};}
struct QPainter{explicit QPainter(QWidget*){}void fillRect(QRect r,Qt::Color color){assert(basePaints>markers);assert(color==Qt::magenta&&r.x==4&&r.y==4&&r.w==8&&r.h==8);markers++;}};
struct Role{QWidget*widget=nullptr;quint64 instance=0;QAction*popupAction=nullptr;};static Role roles[5];
struct Record{int&operator[](const char*){static int cell;return cell;}};
static Record record(const char*name,const Role*r){assert(r->widget);assert(std::string(name)=="draw-queued"||std::string(name)=="popup-action-triggered");return {};}
static void emitRecord(Record){emitted++;}
#define protected public
static bool currentRole(int index,quint64 instance,const QWidget*widget){return index>=0&&index<5&&instance!=0&&roles[index].widget&&roles[index].instance==instance&&roles[index].widget==widget;}
static bool currentPopupAction(quint64 instance,const QMenu*menu,const QAction*action){return currentRole(4,instance,menu)&&action&&roles[4].popupAction==action&&menu->actions().contains(const_cast<QAction*>(action))&&action->isEnabled()&&action->isVisible();}
static void popupTriggered(quint64 instance,QMenu*menu,QAction*action){if(currentPopupAction(instance,menu,action))emitRecord(record("popup-action-triggered",&roles[4]));}class PopupLandmarkMenu final:public QMenu {quint64 instance;public:PopupLandmarkMenu(QWidget*parent,quint64 captured):QMenu(parent),instance(captured){}protected:void paintEvent(QPaintEvent*event)override{if(!currentRole(4,instance,this))return;QMenu::paintEvent(event);QPainter painter(this);painter.fillRect(QRect(4,4,8,8),Qt::magenta);auto o=record("draw-queued",&roles[4]);o["drawWidth"]=width();o["drawHeight"]=height();emitRecord(o);}};
int main(){QWidget owner;PopupLandmarkMenu menu(&owner,1),stale(&owner,1);QAction action,other;menu.list.items={&action,&other};roles[4]={&menu,1,&action};QPaintEvent event;
menu.paintEvent(&event);assert(basePaints==1&&markers==1&&emitted==1);
stale.paintEvent(&event);assert(basePaints==1&&markers==1&&emitted==1);
roles[4].instance=2;menu.paintEvent(&event);popupTriggered(1,&menu,&action);assert(emitted==1&&basePaints==1);roles[4].instance=1;
popupTriggered(1,&menu,&other);assert(emitted==1);popupTriggered(1,&stale,&action);assert(emitted==1);
action.enabled=false;popupTriggered(1,&menu,&action);assert(emitted==1);action.enabled=true;action.visible=false;popupTriggered(1,&menu,&action);assert(emitted==1);action.visible=true;
menu.list.items={&other};popupTriggered(1,&menu,&action);assert(emitted==1);menu.list.items={&action,&other};
popupTriggered(1,&menu,&action);assert(emitted==2);
roles[4].popupAction=nullptr;popupTriggered(1,&menu,&action);assert(emitted==2);
roles[4].widget=nullptr;menu.paintEvent(&event);popupTriggered(1,&menu,&action);assert(emitted==2&&markers==1&&basePaints==1);
return 0;}
