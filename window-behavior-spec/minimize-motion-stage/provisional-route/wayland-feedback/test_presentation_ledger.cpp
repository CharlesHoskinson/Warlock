#include "PresentationLedger.hpp"
#include <cassert>
#include <iostream>
QVariantMap input(QString token="abcdef123456-1") {return {{"identity",QVariantList{"0x12","12",5}},{"token",token},{"digest",QString(64,'a')},{"output","DP-1"},{"rect",QVariantMap{{"x",10},{"y",20},{"width",100},{"height",90}}},{"progress",.2},{"active",true},{"imageReady",true},{"source","file:///tmp/atlas.png"}};}
int main(){
 auto make=[](PresentationLedger& l,quint64 g){return l.synchronize(g,{{"x",1},{"y",2},{"width",100},{"height",90}},"file:///tmp/atlas.png",true);};
 int tests=0;
 {PresentationLedger l;auto g=l.replaceWindow();l.setInputs(input());auto a=make(l,g);l.setInputs(input("abcdef123456-2"));assert(l.presented(*a,1,20,1,0,1,true));assert(l.after(0)[0].toMap()["token"]=="abcdef123456-1");++tests;}
 {PresentationLedger l;auto g=l.replaceWindow();l.setInputs(input());auto a=make(l,g);auto b=make(l,g);assert(l.presented(*a,1,20,1,0,1,true));assert(l.presented(*b,1,30,2,0,1,true));++tests;}
 {PresentationLedger l;auto g=l.replaceWindow();l.setInputs(input());auto a=make(l,g);auto b=make(l,g);assert(l.presented(*b,1,30,2,0,1,true));assert(!l.presented(*a,1,20,1,0,1,true));++tests;}
 {PresentationLedger l;auto g=l.replaceWindow();l.setInputs(input());auto a=make(l,g);l.replaceWindow();assert(!l.presented(*a,1,20,1,0,1,true));++tests;}
 {PresentationLedger l;auto g=l.replaceWindow();l.setInputs(input());auto a=make(l,g);assert(!l.presented(*a,1,20,1,0,1,false));assert(l.after(0).empty());++tests;}
 {for(auto suffix:{QString("\n"),QString("\r\n"),QString("-extra")}){PresentationLedger l;auto g=l.replaceWindow();l.setInputs(input("abcdef123456-1"+suffix));assert(!make(l,g));}++tests;}
 {PresentationLedger l;auto g=l.replaceWindow();l.setInputs(input());assert(!l.synchronize(g,{{"x",1}},"file:///tmp/other.png",true));assert(!l.synchronize(g,{{"x",1}},"file:///tmp/atlas.png",false));++tests;}
 {PresentationLedger l;auto g=l.replaceWindow();l.setInputs(input());auto a=make(l,g);assert(l.presented(*a,1,20,1,0,1,true));auto b=make(l,g);assert(!l.presented(*b,1,19,2,0,1,true));assert(!l.presented(*b,2,0,2,0,2,true));++tests;}
 {PresentationLedger l;auto g=l.replaceWindow();l.setInputs(input());for(int i=0;i<600;++i){auto a=make(l,g);assert(l.presented(*a,2,i,1,0,1,true));}assert(l.after(0).size()==512);assert(l.after(599).size()==1);++tests;}
 std::cout<<tests<<" presentation ledger scenarios PASS\n";
}
