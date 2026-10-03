#pragma once
#include <stdexcept>

namespace OwnedProduction {
struct Selection {
    bool over;
    bool manual;
    bool explicitExperiment;
    const char* role;
};
inline Selection select(bool raster,bool manualExperiment,bool overExperiment){
    if(manualExperiment&&overExperiment)throw std::invalid_argument("one exact diagnostic experiment required");
    if((manualExperiment||overExperiment)&&!raster)throw std::invalid_argument("experiment flags cannot change production launch scope");
    if(manualExperiment)return {false,true,true,"diagnostic-manual-experiment"};
    if(overExperiment)return {true,true,true,"diagnostic-over-experiment"};
    return {true,true,false,raster?"diagnostic-default":"production-default"};
}
}
