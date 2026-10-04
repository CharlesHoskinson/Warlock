struct probe {
    struct weston_compositor *compositor;
    struct weston_seat *seat;
    struct wl_global *global;
    struct wl_resource *controller;
    struct wl_listener destroy, seat_destroy;
    bool held[3];
    bool held_keys[2];
    bool lost_child;
    struct wl_global *observer_global;
    struct wl_resource *observer;
    struct weston_view *observed_view;
    struct wl_listener observed_destroy;
    uint32_t view_identity, observation_revision;
};
