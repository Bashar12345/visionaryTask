# urls.py
from rest_framework import routers
from .views import  MovieViewSet, RatingViewSet, MovieSearchViewSet

router = routers.DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'ratings', RatingViewSet, basename='rating')
router.register(r'search', MovieSearchViewSet, basename='movie-search')

urlpatterns = [
    # Your other URL patterns
]

urlpatterns += router.urls

