from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Genre, Book

from books.serializers import GenreSerializer


GENRES_URL = reverse('books:genre-list')


class PublicGenresApiTests(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(GENRES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGenresApiTests(TestCase):
    """Test the private genres API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'abc@xyz.com',
            'poiuytrew'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_genres_list(self):
        """Test retrieving a list of genres"""
        Genre.objects.create(user=self.user, name='Science')
        Genre.objects.create(user=self.user, name='History')

        res = self.client.get(GENRES_URL)

        genres = Genre.objects.all().order_by('-name')
        serializer = GenreSerializer(genres, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_genres_limited_to_user(self):
        """Test that genres for the authenticated user are returend"""
        user2 = get_user_model().objects.create_user(
            'other@panda.com',
            'okmijnuhb'
        )
        Genre.objects.create(user=user2, name='Secrete')
        genre = Genre.objects.create(user=self.user, name='Horror')

        res = self.client.get(GENRES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], genre.name)

    def test_create_genre_successful(self):
        """Test create a new genre"""
        payload = {'name': 'Cabbage'}
        self.client.post(GENRES_URL, payload)

        exists = Genre.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_genre_invalid(self):
        """Test creating invalid genre fails"""
        payload = {'name': ''}
        res = self.client.post(GENRES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retrieve_genres_assigned_to_books(self):
        """Test filtering genres by those assigned to books"""
        genre1 = Genre.objects.create(user=self.user, name='Scify')
        genre2 = Genre.objects.create(user=self.user, name='horror')
        book = Book.objects.create(
            title = 'The Ganges',
            author = 'Ramos',
            price = 23.00,
            quantity = 11,
            user=self.user
        )
        book.genre.add(genre1)

        res = self.client.get(GENRES_URL, {'assigned_only': 1})

        serializer1 = GenreSerializer(genre1)
        serializer2 = GenreSerializer(genre2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_genre_assigned_unique(self):
        """Test filtering genre by assigned returns unique items"""
        genre = Genre.objects.create(user=self.user, name='Thril')
        Genre.objects.create(user=self.user, name='child')
        book1 = Book.objects.create(
            title = 'The Empirre',
            author = 'Sparta',
            price = 20.00,
            quantity = 14,
            user=self.user
        )
        book1.genre.add(genre)
        book2 = Book.objects.create(
            title = 'The Dragon',
            author = 'chinese',
            price = 12.00,
            quantity = 2,
            user=self.user
        )
        book2.genre.add(genre)

        res = self.client.get(GENRES_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)