#include "/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/producer-trajectory-dev-v11/ContinuousTrajectory.hpp"
#include <iostream>
#include <iomanip>
using namespace ContinuousMotion;
void run(const char* name,Origin o,double t){FamilyTrajectory a({o},4);auto s=a.sample(0,a.seconds()*t);bool refused=false;try{FamilyTrajectory b({Origin{s.rectangle,s.velocity,o.rectangle}},4);}catch(const std::invalid_argument&){refused=true;}std::cout<<std::setprecision(17)<<name<<" duration="<<a.seconds()<<" width="<<s.rectangle[2]<<" widthVelocity="<<s.velocity[2]<<" reversedRefused="<<refused<<"\n";}
int main(){run("positiveTangent",{{0,0,400000,1},{0,0,1e9,0},{0,0,400000,1}},1.0/3);run("shortDuration",{{0,0,1,1},{0,0,-1e9,0},{0,0,400000,1}},.5);}
