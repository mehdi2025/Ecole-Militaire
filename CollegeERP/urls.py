from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from mozilla_django_oidc import views as oidc_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('info.urls')),
    path('info/', include('info.urls')),
    path('api/', include('apis.urls')),
    # Replace Django auth views with OIDC views
    path('accounts/login/', oidc_views.OIDCAuthenticationRequestView.as_view(), name='login'),
    path('accounts/logout/', oidc_views.OIDCLogoutView.as_view(), name='logout'),
    
    # Add OIDC URLs
    path('oidc/', include('mozilla_django_oidc.urls')),
]

