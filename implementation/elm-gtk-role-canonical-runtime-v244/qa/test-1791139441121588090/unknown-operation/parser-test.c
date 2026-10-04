#define _POSIX_C_SOURCE 200809L
#include "commands.h"
int main(void){struct command c;
if(parse_command("1 create-owners",&c) != true)return 1;
if(parse_command("1 open-modal",&c) != true)return 2;
if(parse_command("1 close-modal",&c) != true)return 3;
if(parse_command("1 close-owner",&c) != true)return 4;
if(parse_command("1 create-family",&c) != true)return 5;
if(parse_command("2 open-nested",&c) != true)return 6;
if(parse_command("3 close-nested",&c) != true)return 7;
if(parse_command("4 open-popover",&c) != true)return 8;
if(parse_command("5 close-popover",&c) != true)return 9;
if(parse_command("6 inspect",&c) != true)return 10;
if(parse_command("7 quit",&c) != true)return 11;
if(parse_command("8 minimize A",&c) != true)return 12;
if(parse_command("9 restore C",&c) != true)return 13;
if(parse_command("10 maximize A",&c) != true)return 14;
if(parse_command("11 unmaximize C",&c) != true)return 15;
if(parse_command("9223372036854775807 inspect",&c) != true)return 16;
if(parse_command("",&c) != false)return 17;
if(parse_command("0 inspect",&c) != false)return 18;
if(parse_command("01 inspect",&c) != false)return 19;
if(parse_command("-1 inspect",&c) != false)return 20;
if(parse_command("+1 inspect",&c) != false)return 21;
if(parse_command("1.0 inspect",&c) != false)return 22;
if(parse_command("true inspect",&c) != false)return 23;
if(parse_command("9223372036854775808 inspect",&c) != false)return 24;
if(parse_command("99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999 inspect",&c) != false)return 25;
if(parse_command("1 unknown",&c) != false)return 26;
if(parse_command("1 minimize",&c) != false)return 27;
if(parse_command("1 minimize B",&c) != false)return 28;
if(parse_command("1 minimize AA",&c) != false)return 29;
if(parse_command("1 inspect A",&c) != false)return 30;
if(parse_command("1 quit extra extra",&c) != false)return 31;
if(parse_command("1 inspect extra",&c) != false)return 32;
if(parse_command("1 maximize C extra",&c) != false)return 33;
if(parse_command("11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",&c) != false)return 34;
return 0;}
