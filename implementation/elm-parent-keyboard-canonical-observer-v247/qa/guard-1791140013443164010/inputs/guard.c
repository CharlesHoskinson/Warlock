#define _GNU_SOURCE
#define main inert_client_main
#include "parent-input-client.c"
#undef main
bool test_runtime(const char*p){return canonical_private_runtime(p);}
bool test_socket(void){return private_socket();}
