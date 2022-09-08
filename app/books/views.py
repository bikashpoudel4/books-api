from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Genre, Book

from books import serializers


class BaseBooksAttrViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin):
    """Base viewset for user owned books attributes"""  
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,) 

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        # For filtering [TAG and GENRE] etc
        # quer_params=first converts to int then boolean 
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset =queryset.filter(book__isnull=False)

        return queryset.filter(
                user=self.request.user
            ).order_by('-name').distinct()
    
    def perform_create(self,serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewset(BaseBooksAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class GenreViewSet(BaseBooksAttrViewSet):
    """Manage Genre in the database"""
    queryset = Genre.objects.all()
    serializer_class =  serializers.GenreSerializer


class BookViewSet(viewsets.ModelViewSet):
    """Manage books in the database"""
    serializer_class = serializers.BookSerializer
    queryset = Book.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        # for filtering
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieves books for the authenticated users"""
        # For filtering with tags and genres
        tag = self.request.query_params.get('tags')
        genre = self.request.query_params.get('genres')
        queryset = self.queryset
        if tag:
            tag_ids = self._params_to_ints(tag)
            queryset = queryset.filter(tag__id__in=tag_ids)
        if genre:
            genre_ids = self._params_to_ints(genre)
            queryset = queryset.filter(genre__id__in=genre_ids)

        return queryset.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.BookDetailSerializer
        # If @action is added 
        elif self.action == 'upload_image':
            return serializers.BookImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create new Book"""
        serializer.save(user=self.request.user)
    
    # writting custom function or to say custom actions
    # [url_path='upload-image] which is url for upload img
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a book"""
        book = self.get_object()
        serializer = self.get_serializer(
            book,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )