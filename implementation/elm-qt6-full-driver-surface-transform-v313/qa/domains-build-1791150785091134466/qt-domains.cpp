#include <QEvent>
#include <QKeyEvent>
#include <QJsonDocument>
#include <QJsonObject>
#include <QtGui/private/qxkbcommon_p.h>
#include <xkbcommon/xkbcommon.h>
#include <fstream>
#include <iostream>
#include <vector>
int main(int argc,char**argv){
 QJsonObject constants{{"window-button-press",int(QEvent::MouseButtonPress)},{"window-button-release",int(QEvent::MouseButtonRelease)},{"window-key-press",int(QEvent::KeyPress)},{"window-key-release",int(QEvent::KeyRelease)},{"leftButton",int(Qt::LeftButton)},{"mouseNotSynthesized",int(Qt::MouseEventNotSynthesized)},{"shiftModifier",int(Qt::ShiftModifier)},{"shiftKey",int(Qt::Key_Shift)},{"windowMaximized",int(Qt::WindowMaximized)}};
 QJsonObject out{{"qtVersion",QT_VERSION_STR},{"constants",constants}};
 if(argc==2){
  std::ifstream input(argv[1],std::ios::binary);if(!input)return 2;std::vector<char> data(1024*1024+1);input.read(data.data(),data.size());auto length=input.gcount();if(length<2||length>1024*1024||data[length-1]!=0)return 3;for(std::streamsize i=0;i<length-1;i++)if(!data[i])return 3;
  auto*ctx=xkb_context_new(XKB_CONTEXT_NO_FLAGS);if(!ctx)return 4;auto*map=xkb_keymap_new_from_string(ctx,data.data(),XKB_KEYMAP_FORMAT_TEXT_V1,XKB_KEYMAP_COMPILE_NO_FLAGS);if(!map){xkb_context_unref(ctx);return 4;}
  auto index=xkb_keymap_mod_get_index(map,XKB_MOD_NAME_SHIFT);if(index==XKB_MOD_INVALID||index>=32)return 5;auto mask=uint32_t(1)<<index;QJsonObject mapping;
  for(auto mods:{uint32_t(0),mask}){
   auto*state=xkb_state_new(map);if(!state)return 5;xkb_state_update_mask(state,mods,0,0,0,0,0);auto code=42+8;auto sym=xkb_state_key_get_one_sym(state,code);auto qtmods=QXkbCommon::modifiers(state,sym);auto key=QXkbCommon::keysymToQtKey(sym,qtmods,state,code);
   QKeyEvent event(QEvent::KeyPress,key,qtmods,code,sym,mods,QString(),false,1);QKeyEvent release(QEvent::KeyRelease,key,qtmods,code,sym,mods,QString(),false,1);
   if(key!=Qt::Key_Shift||sym!=XKB_KEY_Shift_L||event.modifiers()!=release.modifiers())return 6;
   mapping[QString::number(mods)]=QJsonObject{{"nativeScanCode",code},{"nativeVirtualKey",int(sym)},{"qtKey",key},{"qtModifiers",int(event.modifiers())},{"nativeModifiers",int(mods)}};xkb_state_unref(state);
  }
  out["mapping"]=mapping;out["xkbShiftMask"]=int(mask);xkb_keymap_unref(map);xkb_context_unref(ctx);
 }else if(argc!=1)return 2;
 std::cout<<QJsonDocument(out).toJson(QJsonDocument::Compact).toStdString()<<'\n';return 0;
}
