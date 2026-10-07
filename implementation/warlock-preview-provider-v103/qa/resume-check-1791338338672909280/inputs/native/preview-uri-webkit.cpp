#include "preview-uri-api.h"
#include "preview_uri.hpp"
#include <libsoup/soup.h>
#include <string_view>
extern "C" gboolean preview_uri_dispatch(void* opaque,WebKitURISchemeRequest* request) {
    if(!WEBKIT_IS_URI_SCHEME_REQUEST(request)) return FALSE;
    const char* text=webkit_uri_scheme_request_get_uri(request);
    if(!text || !std::string_view(text).starts_with("elm-shell://preview/")) return FALSE;
    GError* error=nullptr;
    GInputStream* stream=nullptr;
    gsize length=0;
    try {
        auto view=webkit_uri_scheme_request_get_web_view(request);
        if(opaque && view) stream=static_cast<preview::uri::Endpoint*>(opaque)->open(reinterpret_cast<uintptr_t>(view),text,&length,&error);
    } catch(...) {g_clear_error(&error);}
    if(!stream) {
        if(!error) error=g_error_new_literal(G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,"Native preview unavailable");
        webkit_uri_scheme_request_finish_error(request,error);g_error_free(error);return TRUE;
    }
    auto response=webkit_uri_scheme_response_new(stream,static_cast<gint64>(length));
    webkit_uri_scheme_response_set_content_type(response,"image/png");
    auto headers=soup_message_headers_new(SOUP_MESSAGE_HEADERS_RESPONSE);
    soup_message_headers_append(headers,"Cache-Control","no-store");
    soup_message_headers_append(headers,"X-Content-Type-Options","nosniff");
    webkit_uri_scheme_response_set_http_headers(response,headers);
    // WebKit takes full ownership of the headers.
    webkit_uri_scheme_request_finish_with_response(request,response);
    g_object_unref(response);g_object_unref(stream);
    return TRUE;
}
