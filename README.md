# DRF handle IDOR security issue

## Name
DRF handle IDOR security issue

## Description
this util use for DRF handle IDOR security issue

## Usage
for example in your main urls.py and nginx.conf you can use this util as blow:

urls.py:
```
# urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatters)),
    re_path(r'^media/(?P<path>.*)$', media_access, name='media'),
]
```

nginx:
```
# NGINX
location @proxy_api {
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header X-Url-Scheme $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Host $http_host;
    proxy_redirect off;
    proxy_pass   http://127.0.0.1:8080;
}

location ~ ^/api {
    try_files $uri @proxy_api;
}
    
location ~ ^/protected {
    try_files $uri @proxy_api;
    internal;
    alias /App;
}
```
