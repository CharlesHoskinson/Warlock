#include "FrameLedger.hpp"
#include <cassert>
#include <iostream>
static QVariantMap input(const char* token="abcdef123456-1",int x=10) {
 return {{"identity",QVariantList{"0x1","abc",123}},{"token",token},{"digest",QString(64,'1')},{"output","left"},{"rect",QVariantMap{{"x",x},{"y",5},{"width",100},{"height",60}}},{"progress",.5},{"active",true},{"imageReady",true}};
}
int main() {
 FrameLedger ledger;const auto gen=ledger.replaceWindow();ledger.setInputs(input());assert(ledger.synchronize(gen,1,{{"x",3},{"y",4},{"width",5},{"height",6}}));ledger.setInputs(input("abcdef123456-2",20));assert(ledger.swapped(gen,2));const auto old=ledger.after(0).first().toMap();assert(old.value("token")=="abcdef123456-1" && old.value("expectedGlobalRect").toMap().value("x")==10);assert(old.value("synchronizedItemSceneRect").toMap().value("x")==3);assert(!old.contains("digest") && !old.contains("identity") && !old.contains("rect"));assert(!old.value("pixelProof").toBool());assert(!ledger.swapped(gen,3));
 const auto next=ledger.replaceWindow();assert(!ledger.swapped(gen,4));assert(!ledger.synchronize(gen,4));assert(ledger.synchronize(next,5));assert(!ledger.synchronize(gen,6));assert(!ledger.swapped(next,4));assert(ledger.swapped(next,6));assert(ledger.after(1).size()==1);
 auto bad=input();bad["imageReady"]=false;ledger.setInputs(bad);assert(!ledger.synchronize(next,7));bad=input();bad["identity"]=QVariantList{"0x1","abc",0};ledger.setInputs(bad);assert(!ledger.synchronize(next,7));
 ledger.setInputs(input());for(int i=0;i<700;i++){assert(ledger.synchronize(next,10+i));assert(ledger.swapped(next,10+i));}assert(ledger.after(0).size()==512);assert(ledger.after(701).size()==1);
 std::cout<<"frame ledger snapshot/epoch/generation/duplicate/time/failure/bounded checks PASS\n";
}
