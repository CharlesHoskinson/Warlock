#include "census-budget.hpp"
#include <wayland-server-core.h>
#include <wayland-server-protocol.h>
#include <sys/socket.h>
#include <unistd.h>
#include <cassert>
#include <iostream>

template<class F> void refuses(F f) {
    bool rejected = false;
    try { f(); } catch (const CensusRefused&) { rejected = true; }
    assert(rejected);
}
int main() {
    auto display = wl_display_create(); assert(display);
    int a[2], b[2]; assert(socketpair(AF_UNIX, SOCK_STREAM, 0, a) == 0);
    assert(socketpair(AF_UNIX, SOCK_STREAM, 0, b) == 0);
    auto ca = wl_client_create(display, a[0]); auto cb = wl_client_create(display, b[0]);
    assert(ca && cb);
    auto sa = wl_resource_create(ca, &wl_surface_interface, 1, 2);
    auto sb = wl_resource_create(cb, &wl_surface_interface, 1, 2);
    assert(sa && sb);
    CensusBudget actual;
    actual.visit(reinterpret_cast<uintptr_t>(wl_resource_get_client(sa)), wl_resource_get_id(sa), true);
    actual.visit(reinterpret_cast<uintptr_t>(wl_resource_get_client(sb)), wl_resource_get_id(sb), true);
    assert(actual.surfaces() == 2 && actual.members() == 2);
    refuses([&] { actual.visit(reinterpret_cast<uintptr_t>(ca), 2, false); });
    refuses([] { CensusBudget c; c.visit(0, 1, false); });
    refuses([] { CensusBudget c; c.visit(1, 0, false); });
    CensusBudget surfaces;
    for (uint32_t i = 1; i <= 4096; ++i) surfaces.visit(1, i, false);
    assert(surfaces.surfaces() == 4096 && surfaces.members() == 0);
    refuses([&] { surfaces.visit(1, 4097, false); });
    CensusBudget members;
    for (uint32_t i = 1; i <= 256; ++i) members.visit(1, i, true);
    assert(members.members() == 256);
    refuses([&] { members.visit(2, 1, true); });
    members.output(60000);
    refuses([&] { members.output(60001); });
    wl_display_destroy_clients(display); wl_display_destroy(display);
    close(a[1]); close(b[1]);
    std::cout << "budget controls passed; actual libwayland resource identities exercised; no native grab\n";
}
