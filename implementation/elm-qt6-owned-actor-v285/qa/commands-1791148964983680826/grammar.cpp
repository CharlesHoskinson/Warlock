#include "commands.hpp"
#include <iostream>
int main(){std::string s;while(std::getline(std::cin,s)){Command c;std::cout<<(parseCommand(s,c)?"yes":"no")<<std::endl;}}
