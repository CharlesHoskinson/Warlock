#include "incarnation-retirement.hpp"
#include <iostream>
#include <set>
#include <string>
int main() {
    uint64_t issued=0;
    std::set<uint64_t> owned;
    bool minimized=false;
    std::string event,status;
    while(std::getline(std::cin,event)) {
        if(event=="Birth") {owned.insert(++issued);status="Born";}
        else if(event=="CloseFirst") {owned.erase(1);status="Closed";}
        else if(event=="MinimizeFirst") {minimized=true;status="Minimized";}
        else {
            const auto subject=event=="QueryZero"?0:event=="QueryFuture" || event=="QueryIncoherent"?issued+1:1;
            const bool present=event=="QueryIncoherent" || owned.contains(subject);
            try {status=preview::retirement::name(preview::retirement::observe(subject,issued,present));}
            catch(const std::invalid_argument&) {status="Invalid";}
        }
        std::cout<<"{\"issued\":"<<issued<<",\"owned\":[";
        bool first=true;
        for(auto id:owned) {if(!first)std::cout<<',';first=false;std::cout<<id;}
        std::cout<<"],\"minimized\":"<<(minimized?"true":"false")<<",\"status\":\""<<status<<"\"}\n";
    }
}
