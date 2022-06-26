from django.db import router
from django.urls import path, include
from .views import SongsAPIView, SongViewSet, AlbumViewSet, ArtistViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('songs', SongViewSet)
router.register('albums', AlbumViewSet)
router.register('artists', ArtistViewSet)


urlpatterns  =  [
    path('api/v1/songs/', SongsAPIView.as_view()),
    path('api/v2/', include(router.urls))
]