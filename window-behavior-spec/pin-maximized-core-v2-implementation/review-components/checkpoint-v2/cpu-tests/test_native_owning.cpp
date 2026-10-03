#include "desktop/state/pin/NativePinPolicy.hpp"
#include "layout/algorithm/tiled/scrolling/NativeScrollingRestore.hpp"
#include "layout/algorithm/tiled/scrolling/ScrollingAlgorithm.hpp"
#include "managers/fullscreen/handler/FullscreenHandler.hpp"
#include <cassert>
#include <iostream>
#include <limits>
using namespace Layout;
using namespace Layout::Tiled;
using namespace Fullscreen::ScrollingFullscreenHandler;
// Actual owning layout/controller objects. Null window/space intentionally cannot
// satisfy production native window admission; this adapter tests numeric ownership.
class CTarget final : public ITarget {
 public:
 eTargetType type() override{return TARGET_TYPE_WINDOW;}
 PHLWINDOW window() const override{return nullptr;}
 bool floating() override{return false;}
 void setFloating(bool) override{++floatCalls;}
 std::expected<SGeometryRequested,eGeometryFailure> desiredGeometry() override{return std::unexpected(GEOMETRY_NO_DESIRED);}
 std::optional<Vector2D> minSize() override{return std::nullopt;}
 std::optional<Vector2D> maxSize() override{return std::nullopt;}
 void damageEntire() override{}
 void warpPositionSize() override{}
 void onUpdateSpace() override{}
 int floatCalls=0;
};
class CRecordHandler final : public Fullscreen::IFullscreenHandler {
 public:
 CRecordHandler():IFullscreenHandler(nullptr){}
 void syncFullscreenTargets() override{} // native context absent: isolate real record operations
};
struct SFixture {
 SP<SScrollingData> data=makeShared<SScrollingData>(nullptr);
 SP<SColumnData> original,expanded;
 SP<CTarget> first=makeShared<CTarget>(),selected=makeShared<CTarget>(),last=makeShared<CTarget>(),unrelated=makeShared<CTarget>();
 SP<SScrollingTargetData> row;
 SNativeScrollRestore restore;
 SP<SColumnData> column(float width){auto c=makeShared<SColumnData>(data);c->self=c;data->columns.push_back(c);auto i=data->controller->addStrip(width);data->controller->getStrip(i).userData=c;return c;}
 SFixture(){
  data->self=data;original=column(.625F);original->add(first);original->add(selected);original->add(last);
  original->setTargetSize(0,.2F);original->setTargetSize(1,.3F);original->setTargetSize(2,.5F);data->controller->setOffset(143.75);
  restore.column=original;restore.width=original->getColumnWidth();restore.offset=data->controller->getOffset();
  for(size_t i=0;i<original->targetDatas.size();++i)restore.rows.push_back({original->targetDatas[i],original->getTargetSize(i)});
  row=original->targetDatas[1];original->remove(selected);expanded=column(1.F);expanded->add(row);
  for(size_t i=0;i<original->targetDatas.size();++i)restore.remaining.push_back({original->targetDatas[i],original->getTargetSize(i)});
  data->controller->setOffset(990.5);
 }
};
int main(){
 int checks=0;auto check=[&](bool v){++checks;assert(v);};
 {
  SFixture f;const auto selectedBox=f.selected->geometrySnapshot();check(nativeReturnValid(f.data,f.row,f.restore));
  check(restoreNativeColumn(f.data,f.row,f.restore));check(f.data->columns.size()==1&&f.data->columns.front()==f.original);
  check(f.original->targetDatas.size()==3&&f.original->targetDatas[1]==f.row&&f.row->column==f.original);
  check(f.original->getColumnWidth()==.625F&&f.original->getTargetSize(0)==.2F&&f.original->getTargetSize(1)==.3F&&f.original->getTargetSize(2)==.5F);
  check(f.data->controller->getOffset()==143.75&&f.selected->floatCalls==0);
  check(f.selected->geometrySnapshot().logicalBox==selectedBox.logicalBox);
 }
 {
  SFixture f;f.original->setTargetSize(0,.875F);const auto offset=f.data->controller->getOffset();
  check(!nativeReturnValid(f.data,f.row,f.restore));check(!restoreNativeColumn(f.data,f.row,f.restore));
  check(f.original->getTargetSize(0)==.875F&&f.data->controller->getOffset()==offset&&f.row->column==f.expanded);
 }
 {
  SFixture f;std::swap(f.original->targetDatas[0],f.original->targetDatas[1]);check(!restoreNativeColumn(f.data,f.row,f.restore));check(f.row->column==f.expanded);
 }
 {
  SFixture f;f.original->remove(f.first);f.original->add(f.unrelated);check(!restoreNativeColumn(f.data,f.row,f.restore));check(f.row->column==f.expanded);
 }
 {
  SFixture f;auto replacement=makeShared<SScrollingData>(nullptr);replacement->self=replacement;check(!restoreNativeColumn(replacement,f.row,f.restore));check(f.row->column==f.expanded);
 }
 {
  SFixture f;f.restore.width=std::numeric_limits<float>::quiet_NaN();check(!restoreNativeColumn(f.data,f.row,f.restore));check(f.row->column==f.expanded);
 }
 {
  SFixture f;f.restore.offset=std::numeric_limits<double>::infinity();check(!restoreNativeColumn(f.data,f.row,f.restore));check(f.row->column==f.expanded);
 }
 {
  SFixture f;f.restore.rows[1].data=f.restore.rows[0].data;check(!restoreNativeColumn(f.data,f.row,f.restore));check(f.row->column==f.expanded);
 }
 {
  SFixture f;f.data->columns.erase(f.data->columns.begin());check(!restoreNativeColumn(f.data,f.row,f.restore));check(f.row->column==f.expanded);
 }
 {
  // Real normal-return target and real core handler membership/client modes.
  // Map-only source retirement must leave independent destination modes and boxes.
  auto selected=makeShared<CTarget>(),peer=makeShared<CTarget>();CRecordHandler source,destination;
  selected->setPositionGlobal(STargetBox{.logicalBox={21,35,420,300},.visualBox={22,36,418,298}});peer->setPositionGlobal(CBox{5,6,70,80});
  source.setTargetFullscreenModeInternal(selected,Fullscreen::FSMODE_MAXIMIZED);source.setTargetFullscreenModeClient(selected,Fullscreen::FSMODE_MAXIMIZED);
  source.setTargetFullscreenModeInternal(peer,Fullscreen::FSMODE_FULLSCREEN);
  const auto before=source.getFullscreenModes(selected);const auto normal=selected->geometrySnapshot();const auto peerBox=peer->geometrySnapshot();
  check(before.internal==Fullscreen::FSMODE_MAXIMIZED&&before.client==Fullscreen::FSMODE_MAXIMIZED);
  destination.setTargetFullscreenModeInternal(selected,before.internal);destination.setTargetFullscreenModeClient(selected,before.client);
  source.detachFullscreenRecord(selected);const auto after=destination.getFullscreenModes(selected);
  check(after.internal==before.internal&&after.client==before.client&&source.getFullscreenModes(selected).internal==Fullscreen::FSMODE_NONE);
  check(source.getFullscreenModes(peer).internal==Fullscreen::FSMODE_FULLSCREEN);
  check(selected->geometrySnapshot().logicalBox==normal.logicalBox&&selected->geometrySnapshot().visualBox==normal.visualBox&&peer->geometrySnapshot().logicalBox==peerBox.logicalBox);
  check(selected->floatCalls==0&&peer->floatCalls==0);
  // Missing destination keeps source observations intact until terminal disposal.
  source.setTargetFullscreenModeInternal(selected,Fullscreen::FSMODE_MAXIMIZED);source.setTargetFullscreenModeClient(selected,Fullscreen::FSMODE_MAXIMIZED);
  const auto captured=source.getFullscreenModes(selected);check(captured.internal==Fullscreen::FSMODE_MAXIMIZED&&captured.client==Fullscreen::FSMODE_MAXIMIZED);
  source.detachFullscreenRecord(selected);check(captured.internal==Fullscreen::FSMODE_MAXIMIZED&&destination.getFullscreenModes(selected).internal==Fullscreen::FSMODE_MAXIMIZED);
 }
 std::cout<<checks<<" actual owning column/controller/target/handler checks passed\n";
}
