# Renderer process sharing prototype

The frozen V150 host creates separate controller, popup and per-output bar views.
V160/V161 observe three WebKit renderer processes for one output. V162 supplies
`related-view` at construction for popup and bars, while supplying each view's own
user-content-manager and the existing shared settings. Actual getters assert
context/settings/manager identity before use. Scope routing and renderer policy
are unchanged. No shared manager, second Elm controller or second backend is added.

Pinned WebKitGTK2.52.6 source (`WebKitWebView.cpp`, constructed around825–915,
configuration around778–779) honors an explicitly supplied user-content manager
and records the related page. It rejects supplying web-context simultaneously;
V162 deliberately omits that property on related children. Constructor convenience
API would inherit the manager, so it is not used.

References:
- https://webkitgtk.org/reference/webkit2gtk/stable/ctor.WebView.new_with_related_view.html
- https://raw.githubusercontent.com/WebKit/WebKit/webkitgtk-2.52.6/Source/WebKit/UIProcess/API/glib/WebKitWebView.cpp

Native source/ABI regression and resource measurements must establish actual
process reduction and continued view scope isolation; property presence alone
is not acceptance. Shared process failure affects all related views; fail-closed
host shutdown remains inherited, while graceful renderer recovery remains open.
This is a prototype, not selected host/release acceptance.
