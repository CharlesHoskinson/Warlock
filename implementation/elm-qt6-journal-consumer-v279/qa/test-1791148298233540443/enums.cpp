#include <QEvent>
#include <Qt>
#include <iostream>
int main(){std::cout<<"{\"window-button-press\":"<<int(QEvent::MouseButtonPress)<<",\"window-button-release\":"<<int(QEvent::MouseButtonRelease)<<",\"window-button-double-click\":"<<int(QEvent::MouseButtonDblClick)<<",\"window-key-press\":"<<int(QEvent::KeyPress)<<",\"window-key-release\":"<<int(QEvent::KeyRelease)<<"}";}
