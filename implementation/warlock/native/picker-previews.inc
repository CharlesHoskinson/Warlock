// Included after the owning wrapper; each family retains its original broker,
// opaque token namespace, metadata and exact terminal receipt journal.
struct WarlockPickerPreviews {
    preview::bridge::Native& native;
    const uint64_t popup;
    const GThread* thread=g_thread_self();
    struct Entry {
        std::unique_ptr<WarlockClientProducer> producer;
        std::unique_ptr<preview::bridge::ReceiptDelivery> delivery;
        bool refreshed=false;
    };
    std::map<uint64_t,Entry> entries;
    std::set<uint64_t> attempted;
    uint64_t attemptLease=0;
    WarlockPickerPreviews(preview::bridge::Native& native,gpointer popup):native(native),popup(reinterpret_cast<uintptr_t>(popup)) {}
    void owner(gpointer view) const {preview::bridge::require(g_thread_self()==thread && reinterpret_cast<uintptr_t>(view)==popup,"Exact picker owner thread/receiver");}
    static void append(JsonArray* out,const std::string& batch) {
        preview::bridge::Json value("{\"events\":"+batch+"}");
        auto rows=json_object_get_array_member(value.object(),"events");
        preview::bridge::require(rows && json_array_get_length(rows)<=8,"Bounded own picker producer events");
        for(guint i=0;i<json_array_get_length(rows);++i)json_array_add_element(out,json_node_copy(json_array_get_element(rows,i)));
    }
    static std::string encode(JsonArray* rows) {
        preview::bridge::require(json_array_get_length(rows)<=64,"Bounded picker event delivery");
        JsonNode* node=json_node_new(JSON_NODE_ARRAY);json_node_take_array(node,rows);
        char* text=json_to_string(node,FALSE);std::string result(text);g_free(text);json_node_unref(node);return result;
    }
};
extern "C" WarlockPickerPreviews* warlock_picker_previews_open(void* native,gpointer popup,GError** error) {
    try {preview::bridge::require(native && popup,"Own product picker transport");return new WarlockPickerPreviews(*static_cast<preview::bridge::Native*>(native),popup);}
    catch(const std::exception& e){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,e.what());return nullptr;}
}
extern "C" gboolean warlock_picker_previews_poll(WarlockPickerPreviews* pool,const guint64* subjects,guint count,guint64 publication,guint64 lease,char** events,GError** error) {
    if(events)*events=nullptr;
    try {
        using namespace preview::bridge;
        require(pool && events && count<=256 && (!count || (subjects && publication && lease)),"Trusted bounded picker gate");pool->owner(reinterpret_cast<gpointer>(pool->popup));
        std::set<uint64_t> visible;
        for(guint i=0;i<count;++i)require(subjects[i] && visible.insert(subjects[i]).second,"Distinct own picker subjects");
        if(lease && lease!=pool->attemptLease){require(lease>pool->attemptLease,"Monotonic picker admission lease");pool->attempted.clear();pool->attemptLease=lease;}
        g_autoptr(JsonArray) rows=json_array_new();
        for(auto it=pool->entries.begin();it!=pool->entries.end();) {
            auto& entry=it->second;auto& producer=*entry.producer;
            const bool shown=visible.contains(it->first);
            if(shown && !entry.refreshed) {
                const auto refreshed=producer.family->refreshRefused(publication,lease);
                if(refreshed!="[]"){entry.refreshed=true;WarlockPickerPreviews::append(rows,producer.decorate(refreshed));}
            }
            WarlockPickerPreviews::append(rows,producer.decorate(producer.family->poll(shown?publication:0,shown?lease:0),shown));
            for(const auto& proof:entry.delivery->pending(pool->popup)) {
                Json record(proof);json_array_add_element(rows,json_node_copy(json_parser_get_root(record.parser)));
            }
            if(shown && warlock_client_producer_empty(&producer) && lease>producer.family->lease()) {
                const auto resumed=producer.family->resume(publication,lease);
                if(resumed!="[]"){entry.refreshed=false;WarlockPickerPreviews::append(rows,producer.decorate(resumed));}
            }
            // Idle is not permanent incarnation retirement. Elm retains its
            // request floor and approved history across closing/reopening;
            // replacing this allocator would incorrectly restart at request 1.
            ++it;
        }
        guint enrolled=0;
        // Retained counters are logical actors, bounded by native catalog size.
        // Enroll at most two new demands per gate poll; actual raster/export
        // storage still uses the unchanged global 128MiB/two-allocation budget.
        for(guint i=0;i<count && enrolled<2 && pool->entries.size()<256;++i) {
            const auto subject=subjects[i];if(pool->entries.contains(subject) || pool->attempted.contains(subject))continue;
            pool->attempted.insert(subject);
            // A rejected source has no capture or slot. Inventory fallback stays
            // visible; never retry this enrollment within the same lease.
            std::unique_ptr<WarlockClientProducer> producer;
            try {producer=std::make_unique<WarlockClientProducer>(pool->native,pool->popup,subject,publication,lease,true,FamilyPlane::Transparent,true);}
            catch(const ScopeDenied&){continue;}
            auto delivery=std::make_unique<ReceiptDelivery>(producer->family->endpoint(),pool->native.binding(),pool->popup);
            WarlockPickerPreviews::append(rows,producer->decorate(producer->family->initial()));
            pool->entries.emplace(subject,WarlockPickerPreviews::Entry{std::move(producer),std::move(delivery)});
            ++enrolled;
        }
        *events=g_strdup(WarlockPickerPreviews::encode(g_steal_pointer(&rows)).c_str());return TRUE;
    } catch(const std::exception& e){if(!error || !*error)g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,e.what());return FALSE;}
}
extern "C" gboolean warlock_picker_previews_command(WarlockPickerPreviews* pool,gpointer popup,const char* identity,const char* command,gboolean acquisition_allowed,guint64 lease,char** events,GError** error) {
    if(events)*events=nullptr;
    try {
        using namespace preview::bridge;
        require(pool && identity && command && events,"Own picker command");pool->owner(popup);
        Json value(command);const auto kind=std::string_view(Json::text(value.object(),"kind"));
        require(kind=="acknowledge" || kind=="acquire" || kind=="release" || kind=="cancel","Only exact Elm picker controls");
        require(kind!="acquire" || acquisition_allowed,"Acquire requires current native GTK picker gate");
        const auto entry=std::find_if(pool->entries.begin(),pool->entries.end(),[&](const auto& item){return std::string_view(identity)=="family:"+std::to_string(item.first);});
        require(entry!=pool->entries.end(),"No foreign picker incarnation");
        require(kind!="acquire" || entry->second.producer->family->lease()==lease,"Acquire belongs to this current admitted lease");
        if(kind=="acknowledge") {require(entry->second.delivery->acknowledge(pool->popup,identity,command),"Exact retained terminal proof");*events=g_strdup("[]");}
        else {*events=g_strdup(entry->second.producer->decorate(entry->second.producer->family->command(identity,command)).c_str());}
        return TRUE;
    }catch(const std::exception& e){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,e.what());return FALSE;}
}
extern "C" GInputStream* warlock_picker_previews_stream(WarlockPickerPreviews* pool,gpointer popup,const char* uri,guint64 lease,gsize* length,GError** error) {
    if(length)*length=0;
    try {
        preview::bridge::require(pool && uri && length,"Own picker URI");pool->owner(popup);
        for(auto& [subject,entry]:pool->entries) {
            (void)subject;
            if(entry.producer->family->lease()==lease && entry.producer->family->currentURI()==uri)return warlock_client_producer_stream(entry.producer.get(),popup,uri,length,error);
        }
        preview::bridge::require(false,"Foreign or retired picker URI");
    }catch(const std::exception& e){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,e.what());}
    return nullptr;
}
extern "C" GInputStream* warlock_picker_previews_icon_stream(WarlockPickerPreviews* pool,gpointer popup,const char* uri,guint64 lease,gsize* length,GError** error) {
    if(length)*length=0;
    try {
        preview::bridge::require(pool && uri && length,"Own picker icon URI");pool->owner(popup);
        for(auto& [subject,entry]:pool->entries) {
            (void)subject;
            if(entry.producer->family->lease()==lease && entry.producer->icon && "elm-shell://icon/"+*entry.producer->icon==uri)return warlock_client_producer_icon_stream(entry.producer.get(),popup,uri,length,error);
        }
        preview::bridge::require(false,"Foreign or retired picker icon URI");
    }catch(const std::exception& e){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,e.what());}
    return nullptr;
}
extern "C" gboolean warlock_picker_previews_close(WarlockPickerPreviews* pool,GError** error) {
    if(!pool)return TRUE;
    try {
        pool->owner(reinterpret_cast<gpointer>(pool->popup));
        for(auto& [subject,entry]:pool->entries){(void)subject;preview::bridge::require(warlock_client_producer_empty(entry.producer.get()),"Outstanding native picker custody/journal");}
        for(auto& [subject,entry]:pool->entries){(void)subject;entry.delivery.reset();preview::bridge::require(warlock_client_producer_close(entry.producer.get(),error),"Completed picker producer teardown");entry.producer.release();}
        delete pool;return TRUE;
    }catch(const std::exception& e){if(!error || !*error)g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,e.what());return FALSE;}
}
extern "C" gboolean warlock_picker_previews_empty(WarlockPickerPreviews* pool) {
    if(!pool)return TRUE;
    try {
        pool->owner(reinterpret_cast<gpointer>(pool->popup));
        return std::all_of(pool->entries.begin(),pool->entries.end(),[](auto& item){return warlock_client_producer_empty(item.second.producer.get());});
    }catch(...){return FALSE;}
}
