#include <memory>
#include <unordered_map>
namespace Aquamarine { class CWaylandOutput; namespace NestedPolicy { struct ConfigureLifecycle; } }
using Key = Aquamarine::CWaylandOutput*;
using Value = std::shared_ptr<Aquamarine::NestedPolicy::ConfigureLifecycle>;
using Table = std::__umap_hashtable<Key, Value>;
template std::pair<Table::iterator, bool> Table::_M_emplace_uniq<Key, const Value&>(Key&&, const Value&);
