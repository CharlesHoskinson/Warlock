#pragma once
#include <cstddef>
#include <string>
namespace preview::shader {
inline constexpr size_t ScreenShaderSourceBudget = 262144;
struct AppliedScreenShader {
    bool complete = true, enabled = false, contextualUniforms = false;
    std::string vertex, fragment;
    bool operator==(const AppliedScreenShader&) const = default;
};
// Same compositor owner thread only. Copied applied program inputs, no disk read,
// GL object identity, shader authority or presentation claim.
AppliedScreenShader appliedScreenShader();
}
