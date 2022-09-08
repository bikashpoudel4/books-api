from dataclasses import fields
from pyexpat import model
from rest_framework import serializers

from core.models import Tag, Genre, Book


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genre objects"""

    class Meta:
        model = Genre
        fields = ('id', 'name')
        read_only_fields = ('id',)


class BookSerializer(serializers.ModelSerializer):
    """Serializer of book"""
    genre = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Genre.objects.all()
    )
    tag = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'genre', 'tag', 'price', 'quantity', 'link')
        read_only_fields = ('id',)


class BookDetailSerializer(BookSerializer):
    """Serialize a receipe detail
       Nested Serializer 
    """
    genre = GenreSerializer(many=True, read_only=True)
    tag = TagSerializer(many=True, read_only=True)


class BookImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to book"""

    class Meta:
        model = Book
        fields = ('id', 'image')
        read_only_fields = ('id',)
        