#include "ProspectiveGeometry.hpp"
#include <iostream>
using namespace Elm::ProspectiveGeometry;
static unsigned checks,failures;
#define CHECK(n,c) do{++checks;if(!(c)){++failures;std::cerr<<"FAIL "<<n<<"\n";}}while(0)
int main(){
 const double unlimited=std::numeric_limits<double>::max();
 for(double monitor:{1.0,2.0}) for(int bufferScale:{1,2}) for(bool highMin:{false,true}){
  const Bounds raw=highMin?Bounds{{640,480},{0,0}}:Bounds{{108,42},{900,700}};
  const Bounds layout=highMin?Bounds{{640,480},{unlimited,unlimited}}:Bounds{{108,42},{900,700}};
  Input i{Operation::Maximize,{0,0,800,600},{},{{1,1},{1,1}},{0,0},monitor,raw,layout};
  const auto result=project(i);CHECK("feasible-MAX",result.has_value());
  if(result){CHECK("MAX-real",result->real==CBox(1,1,798,598));CHECK("MAX-configure-logical",result->configure==Vector2D(798,598));CHECK("MAX-logical",result->logical==CBox(0,0,800,600));
   CHECK("buffer-scale-independent",result->configure*bufferScale==Vector2D(798*bufferScale,598*bufferScale));}
  i.operation=Operation::RestoreOrdinary;i.logical=highMin?CBox(83,61,700,500):CBox(83,61,320,180);i.visual=i.logical;
  const auto restored=project(i);CHECK("feasible-restore",restored.has_value());if(restored){CHECK("restore-real-exact",restored->real==i.logical);CHECK("restore-configure",restored->configure==i.logical.size());}
 }
 Input i{Operation::Maximize,{0,0,800,600},{},{{1,1},{1,1}},{0,0},1,{{108,42},{400,300}},{{108,42},{400,300}}};
 const auto before=i;CHECK("insufficient-finite-max",!project(i));CHECK("refusal-input-unchanged",i.logical==before.logical&&i.raw.minimum==before.raw.minimum&&i.raw.maximum==before.raw.maximum&&i.layout.maximum==before.layout.maximum&&i.reserved.topLeft==before.reserved.topLeft);
 i.raw={{810,610},{0,0}};i.layout={{810,610},{unlimited,unlimited}};CHECK("minimum-above-workarea",!project(i));
 i.operation=Operation::RestoreOrdinary;i.logical={83,61,850,650};i.visual=i.logical;CHECK("above-workarea-ordinary-still-feasible",project(i).has_value());
 i.operation=Operation::Maximize;i.logical={0,0,800,600};i.visual={};i.raw={{640,480},{0,0}};i.layout={{1,1},{630,470}};CHECK("contradictory-domains",!project(i));
 i.raw={{320,180},{320,180}};i.layout=i.raw;CHECK("fixed-refused",!project(i));
 i.raw={{108,42},{0,0}};i.layout={{124,66},{unlimited,unlimited}};i.xdgGeometryOrigin={16,24};CHECK("nonzero-refused",!project(i));
 i.xdgGeometryOrigin={0,0};i.monitorScale=2;i.logical={0,0,400,300};i.layout={{640,480},{unlimited,unlimited}};i.raw={{640,480},{0,0}};CHECK("half-logical-workarea-high-min-refused",!project(i));
 i.raw={{108,42},{900,700}};i.layout={{108,42},{900,700}};const auto small=project(i);CHECK("half-logical-workarea-finite-permitted",small&&small->configure==Vector2D(398,298));
 std::cout<<"{\"checks\":"<<checks<<",\"failures\":"<<failures<<"}\n";return failures?1:0;
}
