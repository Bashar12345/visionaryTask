"""
URL configuration for movie_rating_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# movie_rating_api/urls.py
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Import the schema_view from the users app
from users.urls import schema_view as users_schema_view

urlpatterns = [
    # Add a URL pattern to redirect requests to the API documentation
    path(
        "",
        users_schema_view.with_ui("swagger", cache_timeout=0),
        name="api-documentation",
    ),
    # Include the users app URLs
    path("api/", include("users.urls")),
    path("api/", include("movies.urls")),
    
    # Include the swagger and redoc URLs for the users app
    path(
        "swagger/",
        users_schema_view.with_ui("swagger", cache_timeout=0),
        name="users-schema-swagger-ui",
    ),
    path(
        "redoc/",
        users_schema_view.with_ui("redoc", cache_timeout=0),
        name="users-schema-redoc",
    ),
]
