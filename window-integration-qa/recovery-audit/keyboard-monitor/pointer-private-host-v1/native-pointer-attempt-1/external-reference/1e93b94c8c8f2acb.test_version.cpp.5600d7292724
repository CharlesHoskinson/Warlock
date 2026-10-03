#include "candidate/src/backend/GlobalVersion.hpp"
#include <cassert>
#include <cstdint>
#include <iostream>
#include <limits>
int main() {
    using Aquamarine::RegistryVersion::negotiate;
    assert(negotiate(5,6,4)==5);  // actual failing server advertisement
    assert(negotiate(3,6,4)==0);  // damage_buffer unavailable
    assert(negotiate(3,4,4)==0);  // default-feedback unavailable
    assert(negotiate(0,9,5)==0);  // missing/invalid global
    assert(negotiate(4,6,4)==4);
    assert(negotiate(9,6,4)==6);
    assert(negotiate(std::numeric_limits<uint32_t>::max(),6,4)==6);
    unsigned checks=7;
    for (uint32_t advertised=0;advertised<=12;++advertised) {
        for (const auto& [cap,required] : {std::pair{9U,5U},{6U,1U},{6U,4U},{1U,1U},{4U,4U}}) {
            auto actual=negotiate(advertised,cap,required);
            assert(actual<=advertised && actual<=cap);
            assert((actual==0)==(advertised<required));
            assert(actual==0 || actual>=required);
            ++checks;
        }
    }
    std::cout << checks << " actual C++ boundary/property checks PASS\n";
}
