from django.contrib import admin
from django.urls import path, include
from auditor.views import serve_frontend_index, serve_frontend_static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', serve_frontend_index, name='frontend_index'),
    path('style.css', serve_frontend_static, {'filename': 'style.css'}, name='frontend_style'),
    path('script.js', serve_frontend_static, {'filename': 'script.js'}, name='frontend_script'),
    path('api/', include('auditor.urls')),
]

