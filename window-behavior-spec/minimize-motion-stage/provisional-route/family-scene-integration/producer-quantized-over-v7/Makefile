CXX ?= g++
CC ?= cc
CXXFLAGS = -std=c++20 -O2 -fPIC -Wall -Wextra -Wno-misleading-indentation
PROTO = /usr/share/wayland-protocols
LAYER = /home/hoskinson/src/quickshell-accessibility/src/wayland/wlr_layershell/wlr-layer-shell-unstable-v1.xml
XMLS = $(LAYER) $(PROTO)/stable/presentation-time/presentation-time.xml $(PROTO)/stable/viewporter/viewporter.xml $(PROTO)/unstable/xdg-output/xdg-output-unstable-v1.xml $(PROTO)/staging/fractional-scale/fractional-scale-v1.xml $(PROTO)/stable/xdg-shell/xdg-shell.xml
NAMES = layer-shell presentation viewporter xdg-output fractional-scale xdg-shell
LIBS = $(shell pkg-config --cflags --libs Qt6Core libpng egl glesv2 wayland-client wayland-egl)
all: hypr-motion-renderer-staged test-commit-ledger test-family-scene test-backend-policy test-library-material
.protocols: $(XMLS)
	@set -e; set -- $(XMLS); for name in $(NAMES); do wayland-scanner client-header "$$1" "$$name-client.h"; wayland-scanner private-code "$$1" "$$name-protocol.c"; $(CC) -c "$$name-protocol.c" -o "$$name-protocol.o"; shift; done
	@touch $@
hypr-motion-renderer-staged: Renderer.cpp QuantizedOver.hpp SamplingExperiment.hpp CausalImage.hpp ReadbackImage.hpp CommitLedger.hpp BackendPolicy.hpp LibraryMaterial.hpp .protocols
	$(CXX) $(CXXFLAGS) Renderer.cpp $(addsuffix -protocol.o,$(NAMES)) -o $@ $(LIBS)
test-commit-ledger: test_commit_ledger.cpp CommitLedger.hpp
	$(CXX) $(CXXFLAGS) test_commit_ledger.cpp -o $@
test-backend-policy: test_backend_policy.cpp BackendPolicy.hpp
	$(CXX) $(CXXFLAGS) test_backend_policy.cpp -o $@

test-library-material: test_library_material.cpp LibraryMaterial.hpp
	$(CXX) $(CXXFLAGS) test_library_material.cpp -o $@ $(LIBS)

test-family-scene: test_family_scene.cpp Renderer.cpp QuantizedOver.hpp SamplingExperiment.hpp ReadbackImage.hpp CommitLedger.hpp BackendPolicy.hpp LibraryMaterial.hpp .protocols
	$(CXX) $(CXXFLAGS) test_family_scene.cpp $(addsuffix -protocol.o,$(NAMES)) -o $@ $(LIBS)

test-readback-image: test_readback_image.cpp ReadbackImage.hpp
	$(CXX) $(CXXFLAGS) test_readback_image.cpp -o $@ $(LIBS)

test-causal-image: test_causal_image.cpp CausalImage.hpp ReadbackImage.hpp
	$(CXX) $(CXXFLAGS) test_causal_image.cpp -o $@ $(LIBS)

test-manual-sampling: test_manual_sampling.cpp Renderer.cpp QuantizedOver.hpp SamplingExperiment.hpp CausalImage.hpp ReadbackImage.hpp CommitLedger.hpp BackendPolicy.hpp LibraryMaterial.hpp .protocols
	$(CXX) $(CXXFLAGS) test_manual_sampling.cpp $(addsuffix -protocol.o,$(NAMES)) -o $@ $(LIBS)

test-quantized-over: test_quantized_over.cpp Renderer.cpp QuantizedOver.hpp SamplingExperiment.hpp CausalImage.hpp ReadbackImage.hpp CommitLedger.hpp BackendPolicy.hpp LibraryMaterial.hpp .protocols
	$(CXX) $(CXXFLAGS) test_quantized_over.cpp $(addsuffix -protocol.o,$(NAMES)) -o $@ $(LIBS)
