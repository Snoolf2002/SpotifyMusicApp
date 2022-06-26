from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from django.db import transaction
from rest_framework import status, filters
from django.contrib.postgres.search import TrigramSimilarity

from .models import Song, Album, Artist
from .serializers import SongSerializer, AlbumSerializer, ArtistSerializer


class SongsAPIView(APIView):

    def get(self, request):
        songs = Song.objects.all()
        serializer = SongSerializer(songs, many=True)

        return Response(data=serializer.data)

    def post(self, request):
        serializer = SongSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data)


class SongViewSet(ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['-listened', 'listened']

    def get_queryset(self):
        queryset = Song.objects.all()
        query = self.request.query_params.get('search')

        if query is not None:
            queryset = Song.objects.annotate(
                similarity=TrigramSimilarity('title', query)
            ).filter(similarity__gt = 0.3).order_by('-similarity')

        return queryset

    @action(detail=True, methods=['POST'])
    def listen(self, request, *args, **kwargs):
        song = self.get_object()
        with transaction.atomic():
            song.listened += 1
            song.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def top(self, request, *args, **kwargs):
        songs = self.get_queryset()
        top = songs.order_by('-listened')
        serializer = SongSerializer(top, many=True)

        return Response(serializer.data)


class AlbumViewSet(ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'artist__name']

    @action(detail=True, methods=["GET"])
    def songs(self, request, *args, **kwargs):
        album = self.get_object()
        serializer = SongSerializer(album.song_set.all(), many=True)

        return Response(serializer.data)


class ArtistViewSet(ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=True, methods=["GET"])
    def albums(self, request, *args, **kwargs):
        artist = self.get_object()
        serializer = AlbumSerializer(artist.album_set.all(), many=True)

        return Response(serializer.data)