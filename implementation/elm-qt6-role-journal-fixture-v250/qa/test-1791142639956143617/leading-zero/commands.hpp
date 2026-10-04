#pragma once
#include <cstdint>
#include <limits>
#include <sstream>
#include <string>
struct Command {std::uint64_t sequence;std::string operation;char role=0;};
inline bool parseCommand(const std::string &line,Command &c) {
 if(line.size()>511 || line.find('\0')!=std::string::npos)return false;
 std::istringstream stream(line);std::string sequence,operation,role,extra;
 if(!(stream>>sequence>>operation) || sequence.empty())return false;
 std::uint64_t value=0;
 for(char ch:sequence){if(ch<'0'||ch>'9')return false;unsigned digit=ch-'0';if(value>(std::uint64_t(std::numeric_limits<std::int64_t>::max())-digit)/10)return false;value=value*10+digit;}
 if(!value)return false;
 bool targeted=operation=="minimize"||operation=="restore"||operation=="maximize"||operation=="unmaximize"||operation=="reparent-modal";
 bool plain=operation=="open-owner"||operation=="create-owners"||operation=="create-family"||operation=="open-modal"||operation=="close-modal"||operation=="close-owner"||operation=="open-nested"||operation=="close-nested"||operation=="open-popup"||operation=="close-popup"||operation=="inspect"||operation=="quit";
 if(!plain&&!targeted)return false;
 if(targeted){if(!(stream>>role)||role.size()!=1||(role!="A"&&role!="C"))return false;}else if(stream>>role)return false;
 if(stream>>extra)return false;
 c={value,operation,targeted?role.front():char(0)};return true;
}
