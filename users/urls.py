# users/urls.py
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="User API",
        default_version="v1",
        description="API for managing users",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# user-related URL patterns
urlpatterns = [
    path("register/", views.UserRegistrationView.as_view(), name="user-register"),
    path("login/", views.UserLoginView.as_view(), name="user-login"),
    # Other URL patterns for user-related views...
]
